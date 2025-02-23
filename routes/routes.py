from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from models import User, Event, PrayerTime, Obituary
from datetime import datetime
import os

routes = Blueprint('main', __name__)

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Succesvol ingelogd!', 'success')
            return redirect(url_for('main.index'))

        flash('Ongeldige email of wachtwoord.', 'error')
    return render_template('login.html')

@routes.route('/register')
def register():
    return render_template('register.html')

@routes.route('/register/visitor', methods=['GET', 'POST'])
def register_visitor():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email bestaat al.', 'error')
            return redirect(url_for('main.register_visitor'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            user_type='visitor'
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Registratie succesvol!', 'success')
        return redirect(url_for('main.index'))

    return render_template('register_visitor.html')

@routes.route('/register/mosque', methods=['GET', 'POST'])
def register_mosque():
    if request.method == 'POST':
        mosque_name = request.form.get('mosque_name')
        email = request.form.get('email')
        password = request.form.get('password')
        street = request.form.get('street')
        number = request.form.get('number')
        postal = request.form.get('postal')
        city = request.form.get('city')
        phone = request.form.get('phone')

        if User.query.filter_by(email=email).first():
            flash('Email bestaat al.', 'error')
            return redirect(url_for('main.register_mosque'))

        mosque = User(
            username=mosque_name.lower().replace(" ", "_"),
            email=email,
            password_hash=generate_password_hash(password),
            user_type='mosque',
            mosque_name=mosque_name,
            mosque_street=street,
            mosque_number=number,
            mosque_postal=postal,
            mosque_city=city,
            mosque_phone=phone,
            is_verified=False  # Mosques need verification by admin
        )
        db.session.add(mosque)
        db.session.commit()

        login_user(mosque)
        flash('Moskee registratie succesvol! Wacht op verificatie door een beheerder.', 'success')
        return redirect(url_for('main.index'))

    return render_template('register_mosque.html')

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('U bent uitgelogd.', 'info')
    return redirect(url_for('main.index'))

# Keep existing routes
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

@routes.route('/contact')
def contact():
    return render_template('contact.html', 
                         google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY'))

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
        {
            "name": "Pakistaans Islamitisch Cultureel Centrum",
            "street": "Victor Frisstraat",
            "number": "27-29",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0619,
            "lng": 3.7334
        },
        {
            "name": "Okba ibn Nafi-moskee",
            "street": "Warandestraat",
            "number": "39",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0558,
            "lng": 3.7248
        },
        {
            "name": "Eyup sultan Camii",
            "street": "Kazemattenstraat",
            "number": "80",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0492,
            "lng": 3.7218
        },
        {
            "name": "Groene Moskee Fatih",
            "street": "Kwakkelstraat",
            "number": "41",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0597,
            "lng": 3.7386
        },
        {
            "name": "Tevhid Camii",
            "street": "Fr. Ferrerlaan",
            "number": "214A",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0672,
            "lng": 3.7454
        },
        {
            "name": "Moskee Al Fath",
            "street": "Beukelaarsstraat",
            "number": "23-25",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0583,
            "lng": 3.7279
        },
        {
            "name": "Vzw de Toekomst",
            "street": "R. Novarumplein",
            "number": "1A",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0633,
            "lng": 3.7401
        },
        {
            "name": "Yavuz Sultan Selim Camii",
            "street": "Langestraat",
            "number": "204",
            "postal": "9050",
            "city": "Gent",
            "lat": 51.0521,
            "lng": 3.7595
        },
        {
            "name": "Islamitisch Cultureel centrum - Badr",
            "street": "Kerkstraat",
            "number": "188",
            "postal": "9050",
            "city": "Gent",
            "lat": 51.0557,
            "lng": 3.7593
        },
        {
            "name": "Dzamet Ensarija",
            "street": "Doornzelestraat",
            "number": "5-7",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0669,
            "lng": 3.7423
        },
        {
            "name": "Vaynah Kaukasisch Cultureel Centrum vzw",
            "street": "Kapiteinstraat",
            "number": "42",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0588,
            "lng": 3.7332
        },
        {
            "name": "Moskee Salahaddien",
            "street": "Antwerpsesteenweg",
            "number": "24",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0635,
            "lng": 3.7442
        },
        {
            "name": "Ittahad el muslimin",
            "street": "Voormuide",
            "number": "71",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0647,
            "lng": 3.7297
        },
        {
            "name": "Moskee Alfurkaan",
            "street": "Rietstraat",
            "number": "35",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0578,
            "lng": 3.7367
        },
        {
            "name": "El-Albani Moskee",
            "street": "Phoenixstraat",
            "number": "49",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0612,
            "lng": 3.7289
        },
        {
            "name": "Ilmihal Dernegi",
            "street": "Dendermondsesteenweg",
            "number": "283",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0669,
            "lng": 3.7489
        },
        {
            "name": "Afghan Attaqwa moskee",
            "street": "Dendermondsesteenweg",
            "number": "417",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0701,
            "lng": 3.7567
        },
        {
            "name": "Somalische Culturele Vereniging",
            "street": "Voormuide",
            "number": "89",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0649,
            "lng": 3.7301
        },
        {
            "name": "Sadique Cultureel centrum",
            "street": "Frans van Ryhovelaan",
            "number": "317",
            "postal": "9000",
            "city": "Gent",
            "lat": 51.0683,
            "lng": 3.7145
        }
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