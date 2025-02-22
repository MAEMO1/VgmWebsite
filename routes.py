from flask import render_template
from app import app
from models import Event, PrayerTime
from datetime import datetime

# The main routes are registered directly on the app
# While feature-specific routes are in their respective blueprints

@app.route('/')
def index():
    # Get upcoming events for the homepage
    events = Event.query.order_by(Event.date).limit(3).all()
    prayer_times = PrayerTime.query.filter_by(date=datetime.today().date()).all()
    return render_template('index.html', events=events, prayer_times=prayer_times)

@app.route('/prayer-times')
def prayer_times():
    times = PrayerTime.query.filter_by(date=datetime.today().date()).all()
    return render_template('prayer_times.html', times=times)

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Event routes are handled by the events blueprint in routes/event_routes.py
# Obituary routes will be moved to a separate blueprint when implemented