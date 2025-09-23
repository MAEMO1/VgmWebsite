from datetime import datetime, date
import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
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

        # Add prayer times data for today
        # Import here to avoid circular imports
        from services.prayer_service import get_prayer_times_for_date_range
        
        # Get prayer times for today
        prayer_times = get_prayer_times_for_date_range(today, today)
        logger.debug(f"Retrieved prayer times for {today}")

        return render_template('ramadan/iftar_map.html',
                           events=events,
                           events_json=events_json,
                           family_only=family_only,
                           selected_mosque=selected_mosque,
                           today=today,
                           prayer_times=prayer_times,
                           mosques=mosques,
                           google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY'))

    except Exception as e:
        logger.error(f"Error in iftar_map route: {e}", exc_info=True)
        flash(_('Er is een fout opgetreden bij het laden van de iftar kaart.'), 'error')
        return redirect(url_for('ramadan.index'))

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
        return redirect(url_for('ramadan.index'))

@ramadan.route('/api/debug-iftar')
def debug_iftar():
    """API endpoint for debugging iftar map"""
    try:
        today = date.today()
        
        # Collect debug information
        debug_info = {
            'date': today.strftime('%Y-%m-%d'),
            'events_count': IfterEvent.query.filter(IfterEvent.date >= today).count(),
            'verified_mosques': User.query.filter_by(user_type='mosque', is_verified=True).count(),
            'google_maps_api_key_set': bool(os.environ.get('GOOGLE_MAPS_API_KEY')),
            'db_url_set': bool(os.environ.get('DATABASE_URL')),
            'environment': os.environ.get('FLASK_ENV', 'development'),
        }
        
        # Add more detailed iftar events data
        events = IfterEvent.query.filter(IfterEvent.date >= today).limit(5).all()
        events_data = []
        
        for event in events:
            mosque = User.query.get(event.mosque_id) if event.mosque_id else None
            event_data = {
                'id': event.id,
                'date': event.date.strftime('%Y-%m-%d'),
                'mosque_id': event.mosque_id,
                'mosque_name': mosque.mosque_name if mosque else 'Unknown',
                'has_coordinates': bool(mosque and mosque.latitude and mosque.longitude),
                'coordinates': {
                    'lat': mosque.latitude if mosque else None,
                    'lng': mosque.longitude if mosque else None
                } if mosque else None
            }
            events_data.append(event_data)
            
        debug_info['sample_events'] = events_data
        
        return jsonify(debug_info)
    except Exception as e:
        logger.error(f"Error in debug endpoint: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500