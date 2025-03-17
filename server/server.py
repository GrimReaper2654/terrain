from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS  # Import CORS
import json
import time
import math

app = Flask(__name__, static_folder='../static', static_url_path='')
CORS(app)  # Enable CORS for Flask routes
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable CORS for WebSockets

CONSTANTS_DATA_FILE = "data/data.json"
PLAYER_DATA_FILE = "data/players/players.json"

def regionName(x, y=None, file=False):
    if type(x) == dict: # stored as a dictionary?
        if file:
            return f"x{x["x"]}y{x["y"]}"
        return f"data/regions/region_{x["x"]}_{x["y"]}.json"
    
    if type(x) != int: # in an array or tuple?
        if file:
            return f"x{x[0]}y{x[1]}"
        return f"data/regions/region_{x[0]}_{x[1]}.json"
    
    # otherwise, assume x and y are ints
    if file:
        return f"x{x}y{y}"
    return f"data/regions/region_{x}_{y}.json"

# Load json from file
def load_json(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return empty if no file exists or JSON is invalid

# Save data to json file
def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# Initialize data
DATA = load_json(CONSTANTS_DATA_FILE)
players = load_json(PLAYER_DATA_FILE)
world = {
    "x0y0": load_json(regionName(0, 0, True)),
}

@app.route('/')
def index():
    return app.send_static_file('index.html')

@socketio.on('connect')
def handle_connect():
    print("A client connected.")
    emit('gameConstants', DATA)  # Send current data to newly connected client
    emit('world', world["x0y0"]) 
    emit('player', players["player1"])

@socketio.on("playerMove")
def handle_player_move(packet):
    player_id = packet.get("playerID")
    payload = packet.get("payload", {})
    timestamp = packet.get("timestamp")

    current_time_ms = int(time.time() * 1000)
    if timestamp > current_time_ms:
        return

    '''
    region = (position["x"] // (DATA.world.regionSize * DATA.world.chunkSize), 
              position["y"] // (DATA.world.regionSize * DATA.world.chunkSize))
    chunk = ((position["x"] % (DATA.world.regionSize * DATA.world.chunkSize)) // DATA.world.chunkSize, 
             (position["y"] % (DATA.world.regionSize * DATA.world.chunkSize)) // DATA.world.chunkSize)
    block = (position["x"] % DATA.world.chunkSize, 
             position["y"] % DATA.world.chunkSize)

    column = world[regionName(region)][chunk[0]][chunk[1]][block[0]][block[1]]
    if len(column["surface"]) == 0:
        surface = column['underground'][-1]
    else:
        surface = column["surface"][-1]
    '''

    players[player_id]["pos"]["x"] = payload["x"]
    players[player_id]["pos"]["y"] = payload["y"]

    players[player_id]["pos"]["motion"].append({"x": payload["x"], "y": payload["y"], "time": timestamp})

    while len(players[player_id]["pos"]["motion"]) > 10:
        players[player_id]["pos"]["motion"].pop(0)

    save_data(PLAYER_DATA_FILE, players)  # Save updated player data

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=6969, debug=True)
