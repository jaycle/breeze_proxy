from flask import Flask
from flask.logging import default_handler
from .apis.api import api
from flasgger import Swagger
import logging


app = Flask(__name__)
swagger = Swagger(app)
app.register_blueprint(api, url_prefix='/api')
logger = logging.getLogger(__name__)
logger.addHandler(default_handler)

@app.route('/')
def root():
    return 'An API for interacting with the Breeze CMS. Head to <a href="apidocs/">apidocs/</a> for Swagger docs.'
