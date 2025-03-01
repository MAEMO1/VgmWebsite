from datetime import datetime, date
import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from flask_babel import _
from sqlalchemy.orm import joinedload
from extensions import db
from models import User, IfterEvent
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ramadan = Blueprint('ramadan', __name__)

@ramadan.route('/iftar-map')
def iftar_map():
    """Iftar map route with simplified error handling"""
    try:
        logger.debug("Starting iftar map route handler")

        # Get filter parameters
        family_only = request.args.get('filter') == 'family'
        selected_mosque = request.args.get('mosque_id', type=int)
        period = request.args.get('period', 'day')

        today = date.today()
        logger.debug(f"Fetching events for date: {today}")

        # Base query
        query = IfterEvent.query.options(joinedload(IfterEvent.mosque))

        # Apply filters
        if selected_mosque:
            query = query.filter(IfterEvent.mosque_id == selected_mosque)
        if family_only:
            query = query.filter(IfterEvent.is_family_friendly == True)

        # Get events
        events = query.order_by(IfterEvent.date, IfterEvent.start_time).all()
        logger.info(f"Found {len(events)} events matching criteria")

        # Get mosques for dropdown
        mosques = User.query.filter_by(user_type='mosque', is_verified=True).all()
        logger.info(f"Found {len(mosques)} verified mosques")

        # Template context
        context = {
            'events': events,
            'family_only': family_only,
            'selected_mosque': selected_mosque,
            'period': period,
            'today': today,
            'mosques': mosques,
            'google_maps_api_key': os.environ.get('GOOGLE_MAPS_API_KEY'),
            'current_user': current_user
        }

        logger.debug("Rendering iftar map template")
        return render_template('ramadan/iftar_map.html', **context)

    except Exception as e:
        logger.error(f"Error in iftar_map route: {e}", exc_info=True)
        flash(_('Er is een fout opgetreden bij het laden van de iftar kaart.'), 'error')
        # Return to index instead of redirecting to avoid redirect loops
        return render_template('ramadan/index.html')

@ramadan.route('/')
def index():
    """Main Ramadan page with proper error handling"""
    try:
        logger.debug("Starting Ramadan index route")
        today = date.today()

        # Get upcoming iftar events
        upcoming_iftars = IfterEvent.query\
            .options(joinedload(IfterEvent.mosque))\
            .filter(IfterEvent.date >= today)\
            .order_by(IfterEvent.date)\
            .limit(3)\
            .all()
        logger.info(f"Retrieved {len(upcoming_iftars)} upcoming iftars")

        context = {
            'upcoming_iftars': upcoming_iftars,
            'current_user': current_user,
            'today': today
        }

        logger.debug("Rendering Ramadan index template")
        return render_template('ramadan/index.html', **context)

    except Exception as e:
        logger.error(f"Error in index route: {e}", exc_info=True)
        flash(_('Er is een fout opgetreden bij het laden van de Ramadan pagina.'), 'error')
        # Return empty context on error
        return render_template('ramadan/index.html', upcoming_iftars=[])