import os

from flask import Flask, request
from flask_cors import CORS
from flask_limiter import Limiter

import api.drip as drip
from api.daily import daily

redis_host = os.environ.get('REDIS_HOST')
redis_password = os.environ.get('REDIS_PASSWORD')
redis_port = os.environ.get('REDIS_PORT')

# Create a Flask app instance
app = Flask(__name__)
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
