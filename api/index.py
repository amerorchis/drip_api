from flask import Flask, jsonify
from api.nas import nas_events
from datetime import datetime

# Create a Flask app instance
app = Flask(__name__)

# Define a route that returns a JSON on a GET request to /drip
@app.route('/drip', methods=['GET'])
def return_events():
    
    # Check if Drip is in test mode.
    test_mode = False
    if request.args: 
        test_mode = True if 'preview' in request.args and request.args['preview'] == 'true' else False
    day = datetime(2023, 7, 4) if test_mode else datetime.now()
    
    response = {'events': nas_events(day)}
    return jsonify(response)

# Define a route that returns a string on a GET request
@app.route('/', methods=['GET'])
def return_index():
    return "Connection established"

@app.route('/nas', methods=['GET'])
def return_string():
    return nas_events(datetime(2023, 7, 4)).replace('|', '\n')
