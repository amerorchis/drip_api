import os
import threading
import time
from datetime import datetime

from flask import Flask, abort, jsonify, request
from flask_caching import Cache

import api.drip as drip
from api.cache_timing import get_remaining_time
from api.events import events

redis_host = os.environ.get('REDIS_HOST')
redis_password = os.environ.get('REDIS_PASSWORD')
redis_port = os.environ.get('REDIS_PORT')

config={'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_HOST': redis_host,
        'CACHE_REDIS_PORT': redis_port,
        'CACHE_REDIS_PASSWORD': redis_password}

# Create a Flask app instance
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

def async_data(day = datetime.now(), test = False):
    print('about to set cache')
    cache_name = 'cached_test_events' if test else 'cached_events'
    data = events(day)
    cache.set(cache_name, data, timeout=get_remaining_time())
    print(f'cache set with: \n{data}')

def handle_429():
    abort(429)

# Define a route that returns a JSON on a GET request to /drip
@app.route('/drip', methods=['GET'])
@app.route('/drip/', methods=['GET'])
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
        print('Operating in test mode.')
        cached_data = cache.get('cached_test_events')

    else:
        day = datetime.now()
        cached_data = cache.get('cached_events')

    if cached_data:
        # Code to execute when cached data exists
        print(f'Elapsed: {time.time() - start_time} seconds')
        return jsonify(cached_data)
    
    else:
        print('No cache found, initiate threading.')
        async_data(day, test_mode)
        print(f'New cache made; time elapsed: {time.time() - start_time} seconds')
        return jsonify(cached_data)
    
@app.route('/drip/clear')
def clear_cache():
    cache.clear()
    print('Cache cleared')
    return 'Cache cleared'

@app.route('/drip/set_test_cache')
def set_test_cache():
    print('setting test cache')
    cache.set('test_cache', 'You have retrieved test cache data.', timeout=300)
    return 'Test cache set.'

@app.route('/drip/get_test_cache')
def get_test_cache():
    print('getting test cache')
    data = cache.get('test_cache') if cache.get('test_cache') else 'There was no test cache data retrieved.'
    return data
    
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
    elif action == 'optout':
        tag = request.args.get('tag')
        return drip.untag(email, tag)
    else:
        return "No action was specified."
