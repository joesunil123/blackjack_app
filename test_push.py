import socketio
import time
from collections import deque

# Connect to your Flask-SocketIO server
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server")

@sio.event
def disconnect():
    print("Disconnected from server")

sio.connect("http://127.0.0.1:5050")  # Adjust port if different


cards = deque(["8", "A", "4", "3", "6", "10", "4", "8", "5"])
dealer_hand = []
players = [[] for _ in range(4)]
 
counter = 0
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
            {"id": "1", "hand": [players[0].copy()]},
            {"id": "2", "hand": [players[1].copy()]},
            {"id": "3", "hand": [players[2].copy()]},
            {"id": "4", "hand": [players[3].copy()]}
        ],
    }

    time.sleep(2)


    # Emit the event your server listens for
    print("Sending card_data event...")
    sio.emit("card_data", sample_data)

    # Wait a bit to allow processing
    time.sleep(2)

# Done!
sio.disconnect()
