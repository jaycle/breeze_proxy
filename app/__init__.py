from flask import Flask
from flask.logging import default_handler
from .apis.api import blueprint as api
import logging


app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
logger = logging.getLogger(__name__)
logger.addHandler(default_handler)

@app.route('/')
def root():
    return 'An API for interacting with the Breeze CMS. Head to <a href="api/">api/</a> for Swagger docs.'
