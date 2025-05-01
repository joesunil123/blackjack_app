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
import numpy as np
from ultralytics import YOLO
from sklearn.cluster import KMeans
from collections import defaultdict

"""
Model Setup
"""
print("Loading Model...")
# model_path = "./best.engine" 
model_path = "./best_large.pt"
model = YOLO(model_path)
print("Done! \n")

"""
Class Definitions
"""
class Box:
    # Initialization
    def __init__(self, box_coords, cls_id, conf_score):
        # Box Info
        self.cls_id = cls_id
        self.conf_score = conf_score
        self.box = box_coords
        self.dealer_box = False
        # Cluster Info
        self.cluster_loc = None
        self.cluster_id = -1

    # String Method
    def __str__(self):
        return f"box = {self.box}, cls = {model.names[self.cls_id]}, conf_score = {self.conf_score}, dealer box = {self.dealer_box}, \n cluster_loc = {self.cluster_loc}, cluster_id = {self.cluster_id} \n"

"""
Helper Functions
"""
def regex(s):
    match = re.search(r'10', s)
    if match:
        return match.group(0)
    elif s[0] == 'K' or s[0] == 'J' or s[0] == 'Q':
        return '10'
    elif s:
        return s[0]
    else:
        return ''  # for empty strings

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
prev_time, curr_time = 0, 0

"""
Variable Setup
"""

# Colors
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]  

# Assumptions
fb_x    = 115
fb_y    = 150
x_tol   = 110
y_tol   = 60
c_tol   = 50
thresh  = 0.35

# Debug mode
debug = False

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

sio.connect("http://172.25.3.39:5050/")  # Adjust port if different

"""
Critical Loop
"""
while True:
    # Data Structures
    all_boxes = []
    fb_boxes  = []
    seen_cls = set()
    coords_to_cls_conf = {}
    cls_to_coords = {}

    # Capture frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame.")
        break

    # Perform detections
    result = model(frame)[0]

    
    """
    Processing
    """
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
            continue

        # Base Case: New Card Detected (Update local structures)

        # Add coords to the map
        coords_to_cls_conf[coords] = (curr_cls, curr_conf)

        # Add cls and coords to map
        cls_to_coords[curr_cls] = coords

        # Add box to all_boxes
        tmp_box = Box(coords, curr_cls, curr_conf)
        all_boxes.append(tmp_box)

        # Add the cls to the seen_cl
        seen_cls.add(curr_cls)

    """
    Clustering
    """

    # 1. Compute centers
    centers = []
    for box in all_boxes:
        x_min, y_min, x_max, y_max = box.box
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        centers.append([x_center,y_center])

    # 2. Run k-means
    k = 3
    X = np.array(centers)
    try:
        kmeans = KMeans(n_clusters=k, random_state=0).fit(X)
    except:
        continue

    # 3. Collect cluster y-values + Draw Cluster Centers
    centers = kmeans.cluster_centers_
    counter = 0
    y_centers = []
    clusters = []
    for (cx, cy) in centers:
        # Draw cluster centers
        # color = colors[counter % len(colors)] 
        # counter += 1
        # cv2.drawMarker(frame, (int(cx), int(cy)), color=color,
        #                markerType=cv2.MARKER_CROSS, markerSize=15, thickness=2)

        # Store y_coordinate for later
        y_centers.append([cy])

    # 4. Attach clusters to each box
    for i in range(len(all_boxes)):
        # Get needed data
        box = all_boxes[i]
        label = kmeans.labels_[i]
        center = centers[label]

        # Update box cluster info
        box.cluster_loc = (center[0], center[1])
        box.cluster_id = label

    # 5. Cluster based on the y-value
    k = 2
    Y = np.array(y_centers)
    y_kmeans = KMeans(n_clusters=k, random_state=0).fit(Y)
    y_cluster_centers = y_kmeans.cluster_centers_
    counts = []
    for y_coord in y_cluster_centers:

        # Vote on which center is player vs dealer
        count = 0
        for (cx, cy) in centers:
            d = abs(cy - y_coord)
            if d < c_tol:
                count += 1
        counts.append(count)

        # Draw the y_coord centers
        # if counter % 2 == 0:
        #     # print(f"pink is drawn at {y_coord}")
        #     # cv2.circle(frame, (320, int(y_coord[0])), 5, (203, 192, 255), -1)
        # else:
        #     # print(f"purple is drawn at {y_coord}")
        #     # cv2.circle(frame, (320, int(y_coord[0])), 5, (128, 0, 128), -1)
        # counter += 1

    # 6. Find the player and dealer cluster
    if counts[0] == counts[1]:
        # Break ties by assuming lower y_coord is dealer
        print("Tie Breaking!")
        dealer_cluster = np.argmin(y_cluster_centers)
        player_cluster = np.argmax(y_cluster_centers)
    else:
        player_cluster = np.argmax(counts)
        dealer_cluster = np.argmin(counts)

    # 7. Find the dealer cluster
    dealer_coords = (-1,-1)
    for i in range(len(y_kmeans.labels_)):
        label = y_kmeans.labels_[i]
        if label == dealer_cluster:
            dealer_coords = (centers[i][0], centers[i][1])

    # 8. Iterate through all boxes and mark boxes with the dealer_coords as dealer hands
    dealer_cards = []
    for box in all_boxes:
        if box.cluster_loc == dealer_coords:
            # print(f"{box} is a dealer card")
            box.dealer_box = True
            dealer_cards.append(box)

    """
    Data Transfer
    """

    # 1. Create dealer hand
    dealer_hand = [regex(str(model.names[box.cls_id])) for box in dealer_cards]
    data = {"player_hands" : [ {"id" : "dealer", "hand": [dealer_hand]}]}

    # 2. Map center_x to boxes
    centers = [(elt[0], elt[1]) for elt in kmeans.cluster_centers_ if (elt[0], elt[1]) != dealer_coords]
    centerx_to_box = {elt[0] : [] for elt in centers}
    for box in all_boxes:
        x_box, _ = box.cluster_loc
        if x_box in centerx_to_box:
            centerx_to_box[x_box].append(box)

    center_x_to_box = dict(sorted(centerx_to_box.items(), key=lambda item: item[0], reverse=True))
    
    # 3. Build up player hands, from (our) left to right
    counter = 1
    for key in center_x_to_box:
        hand = []
        for box in center_x_to_box[key]:
            cls_id = box.cls_id
            rank = regex(str(model.names[box.cls_id]))
            hand.append(rank)
        data["player_hands"].append({"id" : str(counter), "hand": [hand]})
        counter += 1

    """
    Server Comms
    """
    # Emit the event your server listens for
    print(data)
    sio.emit("card_data", data)

    # Wait a bit to allow processing
    time.sleep(0.2)

