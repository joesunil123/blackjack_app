import socketio
import time

# Connect to your Flask-SocketIO server
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server")

@sio.event
def disconnect():
    print("Disconnected from server")

# Connect to your app
time.sleep(2)
sio.connect("http://127.0.0.1:5050")  # Adjust port if different

# Simulate pushing card stream data to the backend
sample_data = {
    "player_hands": [
        {"id": "dealer", "hand": [["8"]]},
        {"id": "1", "hand": [["8", "3", "3"]]},
        {"id": "2", "hand": [["10", "10"], ["8", "7"]]},
        {"id": "3", "hand": [["7", "7", "7"]]},
        {"id": "4", "hand": [["A", "4"]]}
    ],
}
# Emit the event your server listens for
print("Sending card_data event...")
sio.emit("card_data", sample_data)

# Wait a bit to allow processing
time.sleep(2)

# Done!
sio.disconnect()
