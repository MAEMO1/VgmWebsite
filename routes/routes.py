from flask import render_template, redirect, url_for
from app import db
from models import Event, PrayerTime, Obituary
from datetime import datetime

# Import the blueprint instance
from . import routes

# Register routes on the blueprint instead of app
@routes.route('/')
def index():
    try:
        # Get upcoming events for the homepage
        events = Event.query.filter(
            Event.date >= datetime.utcnow()
        ).order_by(Event.date).limit(3).all()

        # Get today's prayer times
        today = datetime.today().date()
        prayer_times = PrayerTime.query.filter_by(date=today).all()

        return render_template('index.html', events=events, prayer_times=prayer_times)
    except Exception as e:
        # Create an empty list if database is not yet populated
        return render_template('index.html', events=[], prayer_times=[])

@routes.route('/prayer-times')
def prayer_times():
    times = PrayerTime.query.filter_by(date=datetime.today().date()).all()
    return render_template('prayer_times.html', times=times)

@routes.route('/contact')
def contact():
    return render_template('contact.html')

@routes.route('/obituaries')
def obituaries():
    obituaries = Obituary.query.filter_by(is_approved=True).order_by(Obituary.date_of_death.desc()).all()
    return render_template('obituaries.html', obituaries=obituaries)

@routes.route('/login')
def login():
    return render_template('login.html')