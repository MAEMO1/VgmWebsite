from datetime import date
import logging
from flask import Blueprint, render_template
from app import db
from models import User, IfterEvent

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ramadan = Blueprint('ramadan', __name__)

@ramadan.route('/iftar-map')
def iftar_map():
    """Basic iftar map route"""
    try:
        logger.debug("Starting iftar map route")
        return "Iftar map placeholder - Coming soon!"
    except Exception as e:
        logger.error(f"Error in iftar_map route: {e}", exc_info=True)
        return "Error loading iftar map", 500