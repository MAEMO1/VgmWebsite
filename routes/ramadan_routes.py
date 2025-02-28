import os
from datetime import date, datetime
from flask import Blueprint, render_template
from extensions import db, logger
from models import IfterEvent, PrayerTime, Event

ramadan = Blueprint('ramadan', __name__)

@ramadan.route('/iftar-map')
def iftar_map():
    """Basic iftar map route"""
    try:
        logger.debug("Starting iftar map route")
        # Get today's date
        today = date.today()

        # Get all events after today
        events = IfterEvent.query\
            .filter(IfterEvent.date >= today)\
            .order_by(IfterEvent.date)\
            .all()

        logger.info(f"Retrieved {len(events)} events")

        return render_template('ramadan/iftar_map.html',
                             events=events,
                             today=today,
                             google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY'))
    except Exception as e:
        logger.error(f"Error in iftar_map route: {e}", exc_info=True)
        return render_template('base.html', 
                             content="Error loading iftar map"), 500

@ramadan.route('/')
def index():
    """Ramadan home page"""
    try:
        logger.debug("Starting ramadan index route")

        # Get today's prayer times
        today = date.today()
        prayer_times = {
            'fajr': None,
            'dhuhr': None,
            'asr': None,
            'maghrib': None,
            'isha': None
        }

        daily_prayers = PrayerTime.query.filter_by(date=today).all()
        for prayer in daily_prayers:
            if prayer.prayer_name.lower() in prayer_times:
                prayer_times[prayer.prayer_name.lower()] = prayer.time.strftime('%H:%M')

        # Get upcoming iftars
        upcoming_iftars = IfterEvent.query\
            .filter(IfterEvent.date >= today)\
            .order_by(IfterEvent.date)\
            .limit(5)\
            .all()

        # Get Ramadan programs/events
        programs = Event.query\
            .filter(Event.date >= datetime.now())\
            .order_by(Event.date)\
            .limit(3)\
            .all()

        return render_template('ramadan/index.html',
                             upcoming_iftars=upcoming_iftars,
                             prayer_times=prayer_times,
                             programs=programs)
    except Exception as e:
        logger.error(f"Error in ramadan index route: {e}", exc_info=True)
        return render_template('base.html', 
                             content="Error loading ramadan page"), 500