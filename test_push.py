import socketio
import time
from collections import deque
import random

# Connect to your Flask-SocketIO server
# TO COPY
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server")

@sio.event
def disconnect():
    print("Disconnected from server")

sio.connect("http://127.0.0.1:5050/")  # Adjust port if different
# END TO COPY


cards = deque(["8", "A", "4", "3", "6", "10", "4", "8", "5"])
dealer_hand = []
players = [[] for _ in range(4)]
 
counter = 0
mp = [0, 1, 2, 3]
random.shuffle(mp)
while cards:
    if counter == 4:
        dealer_hand.append(cards[0])
    else:
        players[counter].append(cards[0])
    
    counter = (counter + 1) % 5
    cards.popleft()
    
    # Simulate pushing card stream data to the backend
    sample_data = {
        "player_hands": [
            {"id": "dealer", "hand": [dealer_hand.copy()]},
            {"id": "1", "hand": [players[mp[0]].copy()]},
            {"id": "2", "hand": [players[mp[1]].copy()]},
            {"id": "3", "hand": [players[mp[2]].copy()]},
            {"id": "4", "hand": [players[mp[3]].copy()]}
        ],
    }

    time.sleep(0.2)

    # TO COPY
    # Emit the event your server listens for
    print("Sending card_data event...")
    sio.emit("card_data", sample_data)

    # Wait a bit to allow processing
    time.sleep(0.2)
    #END TO COPY

# Done!
    # TO COPY
sio.disconnect()
# END TO COPY
