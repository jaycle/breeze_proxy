from flask import Flask
from flask import jsonify

app = Flask(__name__)

@app.route('/')
def root():
    return 'An api for interacting with the breeze api. Try api/events'


@app.route('/api/events')
def get_events():
    return jsonify({'Events': [{'1': 'First'}, {'2': 'Second'}]})
