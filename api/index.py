from flask import Flask, jsonify
from api.nas import nas_events
from datetime import datetime

# Create a Flask app instance
app = Flask(__name__)

# Define a route that returns a JSON on a GET request to /drip
@app.route('/drip', methods=['GET'])
def return_events():
    test_date = datetime(2023, 7, 4)
    response = {'events': nas_events(test_date)}
    return jsonify(response)

# Define a route that returns a string on a GET request
@app.route('/', methods=['GET'])
def return_index():
    return "Connection established"

@app.route('/nas', methods=['GET'])
def return_string():
    return nas_events(datetime(2023, 7, 4)).replace('|', '\n')
