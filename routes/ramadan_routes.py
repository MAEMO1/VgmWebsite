from datetime import datetime, date
import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from flask_babel import _
from sqlalchemy.orm import joinedload
from app import db
from models import User, IfterEvent
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ramadan = Blueprint('ramadan', __name__)

@ramadan.route('/iftar-map')
def iftar_map():
    """Simplified iftar map route"""
    try:
        logger.debug("Starting iftar map route")

        # Get filter parameters
        family_only = request.args.get('filter') == 'family'
        selected_mosque = request.args.get('mosque_id', type=int)

        # Get today and calculate period dates
        today = date.today()

        # Get events with optimized loading
        logger.debug("Building event query...")
        query = IfterEvent.query\
            .options(joinedload(IfterEvent.mosque))\
            .filter(IfterEvent.date >= today)

        if selected_mosque:
            query = query.filter(IfterEvent.mosque_id == selected_mosque)
        if family_only:
            query = query.filter(IfterEvent.is_family_friendly == True)

        events = query.order_by(IfterEvent.date, IfterEvent.start_time).all()
        logger.info(f"Retrieved {len(events)} events")

        # Convert events to JSON-serializable format
        events_json = []
        for event in events:
            event_dict = {
                'id': event.id,
                'mosque_name': event.mosque.mosque_name if event.mosque else 'Unknown',
                'date': event.date.strftime('%Y-%m-%d'),
                'start_time': event.start_time.strftime('%H:%M'),
                'location': event.location,
                'is_family_friendly': event.is_family_friendly,
                'latitude': event.mosque.latitude if event.mosque else None,
                'longitude': event.mosque.longitude if event.mosque else None
            }
            events_json.append(event_dict)
            logger.debug(f"Processed event: {event_dict}")

        # Get mosques for filtering
        mosques = User.query.filter_by(
            user_type='mosque',
            is_verified=True
        ).all()
        logger.debug(f"Found {len(mosques)} verified mosques")

        return render_template('ramadan/iftar_map.html',
                           events=events,
                           events_json=events_json,
                           family_only=family_only,
                           selected_mosque=selected_mosque,
                           today=today,
                           mosques=mosques,
                           google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY'))

    except Exception as e:
        logger.error(f"Error in iftar_map route: {e}", exc_info=True)
        flash(_('Er is een fout opgetreden bij het laden van de iftar kaart.'), 'error')
        return redirect(url_for('main.index'))

@ramadan.route('/')
def index():
    """Main Ramadan page"""
    try:
        today = date.today()

        # Get upcoming iftar events
        upcoming_iftars = IfterEvent.query\
            .options(joinedload(IfterEvent.mosque))\
            .filter(IfterEvent.date >= today)\
            .order_by(IfterEvent.date)\
            .limit(3)\
            .all()

        return render_template('ramadan/index.html',
                           upcoming_iftars=upcoming_iftars)

    except Exception as e:
        logger.error(f"Error in index route: {e}", exc_info=True)
        flash(_('Er is een fout opgetreden bij het laden van de Ramadan pagina.'), 'error')
        return redirect(url_for('main.index'))