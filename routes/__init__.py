from flask import Blueprint

# Create main routes blueprint
routes = Blueprint('main', __name__)

# Import routes after creating the blueprint
from .routes import *  # noqa: F403, F401