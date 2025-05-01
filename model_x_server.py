"""
Camera Detection + Server Interface

Author: Nicholas Mesa-Cucalon + Joe Sunil Inchodikaran

Description: This script will load a finetuned YOLO Model, capture a frame, then send the detected data to a server api
"""

"""
Imports
"""
import re
import cv2
import time
import socketio
from ultralytics import YOLO
from collections import defaultdict, deque

"""
Model Setup
"""
print("Loading Model...")
model_path = "./best_large.engine" 
# model_path = "./best_large.pt"
model = YOLO(model_path)
print("Done! \n")

"""
Server Setup
"""
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server")

@sio.event
def disconnect():
    print("Disconnected from server")

sio.connect("http://127.0.0.1:5050/")  # Adjust port if different

"""
Camera Setup
"""
print("Opening Camera...")
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()
print("Done! \n")

"""
Variable Setup for Model
"""
# Colors
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]  

# Assumptions
fb_x    = 100
fb_y    = 150
x_tol   = 100
y_tol   = 60
thresh  = 0.35
debug   = False

"""
Class Definitions
"""
class Box:
    # Initialization
    def __init__(self, box_coords, cls_id, conf_score):
        self.cls_id = cls_id
        self.conf_score = conf_score
        self.box = box_coords
        self.dealer_box = False

    # String Method
    def __str__(self):
        return f"box = {self.box}, cls = {model.names[self.cls_id]}, conf_score = {self.conf_score}, dealer box = {self.dealer_box}"

"""
Helper Functions
"""
def regex(s):
    match = re.search(r'10', s)
    if match:
        return match.group(0)
    elif s:
        if s[0] == 'K' or s[0] == 'Q' or s[0] == 'J':
            return '10'
        return s[0]
    else:
        return ''  # for empty strings

while True:
    """
    Detection Code
    """
    all_boxes = []
    fb_boxes  = []
    seen_cls = set()
    coords_to_cls_conf = {}
    cls_to_coords = {}

    # Capture frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame.")
        exit(0)

    # Perform detections
    result = model(frame)[0]

    # Establish all_boxes
    for i in range(len(result.boxes)):
        # Get detection data
        box = result.boxes[i]
        curr_cls = int(box.cls)
        curr_conf = float(box.conf)
        curr_x1, curr_y1, curr_x2, curr_y2 = map(int,box.xyxy[0])
        coords = (curr_x1, curr_y1, curr_x2, curr_y2)

        # Case 1: Threshold out low confidence scores
        if curr_conf <= thresh:
            continue

        # Case 2: Resolve Conflicting Predictions
        if coords in coords_to_cls_conf:
            past_cls, past_conf = coords_to_cls_conf[coords]

            # Our current prediction for this box is better than our past one.
            if curr_conf > past_conf:
                coords_to_cls_conf[coords] = (curr_cls, curr_conf)

            # Continue regardless of if there is an update or not
            continue

        # Case 3: Repeat Detections
        if curr_cls in seen_cls:
            # Get past data
            past_x1, past_y1, past_x2, past_y2 = cls_to_coords[curr_cls]
            # NOTE: fb = full body
            fb_x1, fb_y1 = min(curr_x1, past_x1), min(curr_y1, past_y1)
            fb_x2, fb_y2 = max(curr_x2, past_x2), max(curr_y2, past_y2)
            # Determine if vertical or horizontal and proceed accordingly
            vertical = abs(curr_x2 - curr_x1) < abs(curr_y2 - curr_y1)
            x_dist, y_dist = abs(fb_x2 - fb_x1), abs(fb_y2 - fb_y1)
            if debug:
                print(x_dist)
                print(y_dist)
            if (vertical and x_dist <= fb_x) or (not vertical and y_dist <= fb_y):
                # The repeat detection is the same card, so create a fb_box
                fb_coords = (fb_x1, fb_y1, fb_x2, fb_y2)
                fb_box    = Box(fb_coords, curr_cls, curr_conf)
                fb_boxes.append(fb_box)
                continue

        # Base Case: New Card Detected (Update local structures)

        # Add the cls to the seen_cls
        seen_cls.add(curr_cls)

        # Add coords to the map
        coords_to_cls_conf[coords] = (curr_cls, curr_conf)

        # Add cls and coords to map
        cls_to_coords[curr_cls] = coords

        # Add box to all_boxes
        all_boxes.append(Box(coords, curr_cls, curr_conf))
        

    """
    Data Processing
    """
    # Find the dealers hand using fb_boxes
    y_tol = 60
    y_vals = []
    for box in fb_boxes:
        _, y1, _, y2 = box.box
        mid_y = (y1 + y2) / 2
        y_vals.append(mid_y)
        # print(f"fb_box = {box}, mid_y = {mid_y}")
    y_vals.sort()

    # Find the middle element of the sorted y_vals
    try:
        avg_y = int(y_vals[len(y_vals) // 2])
    except:
        avg_y = 0

    for box in all_boxes:
        _, y1, _, y2 = box.box
        mid_y = (y1 + y2) / 2
        if (mid_y <= avg_y - y_tol) or (avg_y + y_tol <= mid_y):
            box.dealer_box = True
            # print(f"dealers hand = {box}")

    # Clustering
    tl_coords = []
    dealer_cards = []
    for box in all_boxes:
        # Keep only the x1 coordinate
        if not box.dealer_box:
            x1, _, _, _ = box.box
            tl_coords.append((x1,box))
        else:
            dealer_cards.append(box)

    # Sort the tl coords to then cluster
    tl_coords.sort(key = lambda x: x[0])

    # Cluster assuming the boxes have a distance of x_tol between them
    try:
        clusters = [[tl_coords[0]]]
        for i in range(1, len(tl_coords)):
            prev = tl_coords[i - 1][0]
            curr = tl_coords[i][0]
            if curr - prev > x_tol:
                # Start a new cluster
                clusters.append([tl_coords[i]])
            else:
                # Add to current cluster
                clusters[-1].append(tl_coords[i])
    except:
        clusters = [[]]

    """
    Data Transfer
    """
    dealer_hand = [regex(str(model.names[box.cls_id])) for box in dealer_cards]
    player_hands = [{"id" : "dealer", "hand": [dealer_hand]}]
    counter = 1
    for cluster in clusters:
        hand = []
        for elt in cluster:
            box = elt[1]
            rank = regex(str(model.names[box.cls_id]))
            hand.append(rank)
        player_hands.append({"id" : str(counter), "hand": [hand]})
        counter += 1

    data = {"player_hands" : player_hands}

    # Print data to CLI
    print(f"Player Hands after Processing = {player_hands}")
    
    """
    Server Comms
    """
    # Emit the event your server listens for
    print("Sending card_data event...")
    sio.emit("card_data", data)

    # Wait a bit to allow processing
    time.sleep(0.2)

# Done!
sio.disconnect()
