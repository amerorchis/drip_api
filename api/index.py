from flask import Flask, jsonify, request
from api.events import events
import api.nas_old
from datetime import datetime
import api.drip as drip
import time

# Create a Flask app instance
app = Flask(__name__)

# Define a route that returns a JSON on a GET request to /drip
@app.route('/drip', methods=['GET'])
def return_events():
    start_time = time.time()
    test_mode = False

    # Parse args
    if request.args:
        # Check if Drip is in test mode.
        if 'preview' in request.args:
            test_mode = True if 'preview' in request.args and request.args['preview'] == 'true' else False
    
    day = datetime(2023, 7, 4) if test_mode else datetime.now()

    result = events(day)
    print(f'Elapsed: {time.time() - start_time} seconds')

    return result
    
# Define a route that returns a string on a GET request
@app.route('/', methods=['GET'])
def return_index():
    return "Connection established"

@app.route('/nas', methods=['GET'])
def return_string():
    return api.nas_old.nas_events(datetime(2023, 7, 4)).replace('|', '\n')

@app.route('/dripactions', methods=['GET'])
def drip_actions():
    try:
        action, email = request.args['action'], request.args['email']
    except KeyError:
        return 'Sorry, your request could not be processed at this time.'
    
    if action == 'stopdaily':
        return drip.stopdaily(email)
    elif action == 'unsub':
        return drip.unsub(email)
    else:
        return "No action was specified."
