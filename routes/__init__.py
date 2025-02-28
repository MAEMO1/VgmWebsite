from flask import Blueprint

# Create main routes blueprint
routes = Blueprint('main', __name__)

# Import routes
from .routes import routes  # noqa: F401