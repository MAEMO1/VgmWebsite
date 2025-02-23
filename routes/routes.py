from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from models import User, Event, PrayerTime, Obituary
from datetime import datetime
import os

routes = Blueprint('main', __name__)

def initialize_mosques():
    """Initialize the mosques in the database with their coordinates"""
    mosques_data = [
        {
            "name": "IH-VAK Moskee",
            "street": "Koopvaardijlaan",
            "number": "44",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0673,
            "lng": 3.7373
        },
        {
            "name": "Al Markaz at Tarbawi",
            "street": "Elyzeese Velden",
            "number": "35",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0543,
            "lng": 3.7174
        },
        # Add all other mosques here with their coordinates
    ]

    for mosque_data in mosques_data:
        # Check if mosque already exists
        existing_mosque = User.query.filter_by(mosque_name=mosque_data["name"]).first()
        if not existing_mosque:
            mosque = User(
                username=mosque_data["name"].lower().replace(" ", "_"),
                email=f"info@{mosque_data['name'].lower().replace(' ', '')}.be",
                password_hash=generate_password_hash("temporary_password"),
                user_type="mosque",
                mosque_name=mosque_data["name"],
                mosque_street=mosque_data["street"],
                mosque_number=mosque_data["number"],
                mosque_postal=mosque_data["postal"],
                mosque_city=mosque_data["city"],
                latitude=mosque_data["lat"],
                longitude=mosque_data["lng"],
                is_verified=True
            )
            db.session.add(mosque)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing mosques: {e}")

@routes.route('/prayer_times')
def prayer_times():
    try:
        today = datetime.today().date()
        prayer_times = PrayerTime.query.filter_by(date=today).all()
        return render_template('prayer_times.html', prayer_times=prayer_times)
    except Exception as e:
        print(f"Error fetching prayer times: {e}")
        return render_template('prayer_times.html', prayer_times=[])

@routes.route('/')
def index():
    try:
        events = Event.query.filter(
            Event.date >= datetime.utcnow()
        ).order_by(Event.date).limit(3).all()

        today = datetime.today().date()
        prayer_times = PrayerTime.query.filter_by(date=today).all()

        return render_template('index.html', 
                             events=events, 
                             prayer_times=prayer_times,
                             google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY'))
    except Exception as e:
        return render_template('index.html', 
                             events=[], 
                             prayer_times=[],
                             google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY'))

@routes.route('/mosques')
def mosques():
    # Get all verified mosque users
    mosque_users = User.query.filter_by(user_type='mosque', is_verified=True).all()
    return render_template('mosques.html', 
                         mosques=mosque_users,
                         google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY'))

@routes.route('/set_language/<language>')
def set_language(language):
    if language not in ['en', 'nl', 'ar']:
        return redirect(url_for('main.index'))

    session['language'] = language
    return redirect(request.referrer or url_for('main.index'))