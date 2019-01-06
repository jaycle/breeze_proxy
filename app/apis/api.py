from flask import Blueprint
from flask import jsonify, request, g
from flask_restplus import Api, Model, Resource, fields
from .breeze_proxy import BreezeProxy

blueprint = Blueprint('api', __name__)
api = Api(blueprint)

Event = api.model('Event', {
    'date': fields.String,
    'assignments': fields.List(fields.Nested(api.model('Assignment', {
        'role': fields.String,
        'assignee': fields.String
    })))
})

EventTask = api.model('EventTask', {
    'events': fields.List(fields.Nested(Event)),
    'breezeInfo': fields.Nested(api.model('BreezeInfo', {
        'url': fields.String,
        'key': fields.String
    }))
})

EventItem = api.model('EventItem', {
    'date': fields.String,
    'assignee': fields.String,
    'role': fields.String
})

ErrorEventItem = api.inherit('ErrorEventItem', EventItem, {
    'error': fields.String
})

EventsResponse = api.model('EventsResponse', {
    'itemsAdded': fields.List(fields.Nested(EventItem)),
    'itemsNotAdded': fields.List(fields.Nested(ErrorEventItem))
})

def parse_events(events):
    proxy = BreezeProxy(g.get('breeze_info')['url'], g.get('breeze_info')['key'])
    return proxy.add_volunteers_to_breeze(events)

@api.route('/events')
class Events(Resource):
    @api.doc(body=EventTask)
    @api.response(200, 'Success', EventsResponse)
    def post(self):
        body = request.get_json()

        # Set breeze info on context
        g.breeze_info = body.get('breezeInfo')

        data = body.get('events')
        return parse_events(data)
