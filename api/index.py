import os
import threading
import time
from datetime import datetime

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from flask_caching import Cache
from flask_limiter import Limiter

import api.drip as drip
from api.cache_timing import get_remaining_time
from api.events import events
from api.daily import daily

redis_host = os.environ.get('REDIS_HOST')
redis_password = os.environ.get('REDIS_PASSWORD')
redis_port = os.environ.get('REDIS_PORT')

# Fall back to an in-process cache when Redis isn't configured (local dev, tests).
if redis_host:
    config={'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_HOST': redis_host,
            'CACHE_REDIS_PORT': redis_port,
            'CACHE_REDIS_PASSWORD': redis_password}
else:
    config={'CACHE_TYPE': 'SimpleCache'}

# Create a Flask app instance
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
cors = CORS(app, resources={r"/dripactions": {"origins": "https://glacier.org"}})

def client_ip():
    # Behind Vercel's proxy, remote_addr is Vercel itself; the real client
    # IP arrives in x-real-ip / x-forwarded-for.
    return (request.headers.get('x-real-ip')
            or request.headers.get('x-forwarded-for', '').split(',')[0].strip()
            or request.remote_addr
            or 'unknown')

# Rate-limit counters live in Redis because each serverless invocation is a
# fresh process; in-memory counts would reset on every request. Fails open
# (swallow_errors) so a Redis outage can't take down the API.
limiter_storage = f"redis://:{redis_password}@{redis_host}:{redis_port}" if redis_host else "memory://"
limiter = Limiter(client_ip, app=app, storage_uri=limiter_storage, swallow_errors=True)

@app.errorhandler(429)
def ratelimit_exceeded(e):
    return "Too many requests. Please try again later.", 429

def async_data(day = None, test = False):
    if day is None:
        day = datetime.now()
    print('fetching new event data')
    cache_name = 'cached_test_events' if test else 'cached_events'
    data = events(day)
    cache.set(cache_name, data, timeout=get_remaining_time())
    print(f'cache set with: \n{data}')
    return data

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
        print('No cache found, fetching new data.')
        try:
            data = async_data(day, test_mode)
        except Exception as e:
            print(f'Could not fetch events data: {e}')
            return jsonify({'error': 'Could not fetch events data.'}), 502
        print(f'New cache made; time elapsed: {time.time() - start_time} seconds')
        return jsonify(data)
    
@app.route('/drip/clear')
@limiter.limit("3 per hour")
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

@app.route('/dripactions', methods=['GET', 'POST'])
@limiter.limit("10 per minute; 30 per hour")
def drip_actions():
    try:
        action, email = request.args['action'], request.args['email']
    except KeyError:
        return 'Sorry, your request could not be processed at this time.', 400

    def optout():
        tag = request.args.get('tag')
        if not tag:
            return "No tag was specified.", 400
        return drip.untag(email, tag)

    def untilspring():
        remove_message, remove_status = drip.untag(email, 'Glacier Daily Update')
        add_message, add_status = drip.tag(email, 'Resume Daily Spring')
        if remove_status < 400 and add_status < 400:
            return "You have been removed from Daily Updates until spring."
        return f"Sorry, your request could not be processed at this time. ({remove_message}; {add_message})", 502

    actions = {
        'stopdaily': lambda: drip.untag(email, 'Glacier Daily Update'),
        'stopsunset': lambda: drip.untag(email, 'Sunset Timelapse'),
        'startsunset': lambda: drip.subscribe(email, ['Sunset Timelapse']),
        'unsub': lambda: drip.unsub(email),
        'optout': optout,
        'untilspring': untilspring,
        'startdaily': lambda: daily(request.args),
    }

    handler = actions.get(action)
    if handler is None:
        return "No action was specified.", 400

    return handler()
