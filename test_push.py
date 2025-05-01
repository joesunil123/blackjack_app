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

while True:
    cards = deque(["8", "A", "4", "3", "6", "10", "4", "8", "5", "10"])
    dealer_hand = []
    players = [[] for _ in range(4)]
    
    counter = 0
    mp = [0, 1, 2, 3]
    random.shuffle(mp)
    while cards:
        debug = False
        if cards:
            if counter == 4:
                debug = True
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

        print(sample_data)

        time.sleep(0.2)

        # TO COPY
        # Emit the event your server listens for
        t = 1
        if debug:
            t = 10
        for _ in range(t):
            print(f"Sending card_data event... {t}")
            sio.emit("card_data", sample_data)

        # Wait a bit to allow processing
        time.sleep(2)
    
sio.disconnect()