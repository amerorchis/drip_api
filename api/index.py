from flask import Flask, jsonify, request, abort, g
from flask_caching import Cache
from api.events import events
from datetime import datetime
import api.drip as drip
import time
from api.cache_timing import get_remaining_time
import threading

config = {
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

# Create a Flask app instance
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

def async_data(day, test = False):
    cache_name = 'cached_test_events' if test else 'cached_events'
    cache.set(cache_name, events(day), timeout=get_remaining_time())

def handle_429():
    abort(429)

# Define a route that returns a JSON on a GET request to /drip
@cache.cached()
@app.route('/drip', methods=['GET'])
def return_events():
    start_time = time.time()
    test_mode = False

    # Parse args
    if request.args:
        # Check if Drip is in test mode.
        if 'preview' in request.args:
            test_mode = True if 'preview' in request.args and request.args['preview'] == 'true' else False
    
    if test_mode:
        day = datetime(2023, 7, 4)
        cached_data = cache.get('cached_test_events')

    else:
        day = datetime.now()
        cached_data = cache.get('cached_events')

    if cached_data:
        # Code to execute when cached data exists
        print(f'Elapsed: {time.time() - start_time} seconds')
        return jsonify(cached_data)
    
    else:
        threading.Thread(target=handle_429).start
        threading.Thread(target=async_data, args=[day, test_mode]).start()
        return 'Data is being retrieved. Please try again in a minute.', 429
    
# Define a route that returns a string on a GET request
@app.route('/', methods=['GET'])
def return_index():
    return "Connection established"

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
