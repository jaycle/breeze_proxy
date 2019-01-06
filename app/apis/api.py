from flask import Blueprint
from flask import jsonify, request, g
from flasgger import swag_from
from .breeze_proxy import BreezeProxy

api = Blueprint('api', __name__)

def parse_events(events):
    proxy = BreezeProxy(g.get('breeze_info')['url'], g.get('breeze_info')['key'])
    return proxy.add_volunteers_to_breeze(events)

@api.route('/events', methods=['POST'])
@swag_from('events.yml')
def add_events():
    body = request.get_json()

    # Set breeze info on context
    g.breeze_info = body.get('breezeInfo')

    data = body.get('events')
    return parse_events(data)
