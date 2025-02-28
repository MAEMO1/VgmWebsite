import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_babel import Babel

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask-SQLAlchemy with model class
class Base(DeclarativeBase):
    pass

# Create shared instances
db = SQLAlchemy(model_class=Base)
babel = Babel()