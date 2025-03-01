from datetime import datetime, date
import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import current_user, login_required, login_user, logout_user
from flask_babel import _
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models import User
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ramadan = Blueprint('ramadan', __name__)

@ramadan.route('/')
def index():
    """Main Ramadan page"""
    try:
        logger.debug("Starting Ramadan index route")
        today = date.today()

        context = {
            'current_user': current_user,
            'today': today
        }

        logger.debug("Rendering Ramadan index template")
        return render_template('ramadan/index.html', **context)

    except Exception as e:
        logger.error(f"Error in index route: {e}", exc_info=True)
        flash(_('Er is een fout opgetreden bij het laden van de Ramadan pagina.'), 'error')
        return render_template('ramadan/index.html')

@ramadan.route('/about')
def about():
    """About page"""
    return render_template('ramadan/about.html')

@ramadan.route('/memorandum')
def memorandum():
    """Memorandum page"""
    return render_template('ramadan/memorandum.html')

@ramadan.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form handling"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        flash(_('Bedankt voor uw bericht. We nemen zo spoedig mogelijk contact met u op.'), 'success')
        return redirect(url_for('ramadan.contact'))

    return render_template('ramadan/contact.html')

@ramadan.route('/mosques')
def mosques():
    """Mosques overview page with proper error handling"""
    try:
        logger.debug("Starting mosques route handler")
        mosque_users = User.query.filter_by(user_type='mosque').all()
        logger.info(f"Found {len(mosque_users)} mosques")

        context = {
            'mosques': mosque_users,
            'google_maps_api_key': os.environ.get('GOOGLE_MAPS_API_KEY')
        }

        logger.debug("Rendering mosques template")
        return render_template('ramadan/mosques.html', **context)

    except Exception as e:
        logger.error(f"Error in mosques route: {e}", exc_info=True)
        flash(_('Er is een fout opgetreden bij het laden van de moskeeën.'), 'error')
        return render_template('ramadan/mosques.html', mosques=[])

@ramadan.route('/prayer_times')
def prayer_times():
    """Prayer times page with proper error handling"""
    try:
        logger.debug("Starting prayer_times route handler")
        today = datetime.today().date()

        # Mock prayer times data structure (replace with actual API call later)
        prayer_times = [
            {'prayer_name': 'Fajr', 'time': datetime.strptime('05:30', '%H:%M')},
            {'prayer_name': 'Dhuhr', 'time': datetime.strptime('13:15', '%H:%M')},
            {'prayer_name': 'Asr', 'time': datetime.strptime('16:45', '%H:%M')},
            {'prayer_name': 'Maghrib', 'time': datetime.strptime('19:30', '%H:%M')},
            {'prayer_name': 'Isha', 'time': datetime.strptime('21:00', '%H:%M')}
        ]

        logger.info("Prayer times loaded successfully")
        return render_template('prayer_times.html', prayer_times=prayer_times)
    except Exception as e:
        logger.error(f"Error fetching prayer times: {e}", exc_info=True)
        flash(_('Er is een fout opgetreden bij het laden van de gebedstijden.'), 'error')
        return render_template('prayer_times.html', prayer_times=[])

@ramadan.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('ramadan/profile.html')

@ramadan.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(_('U bent succesvol ingelogd!'), 'success')
            return redirect(url_for('ramadan.index'))

        flash(_('Ongeldige email of wachtwoord.'), 'error')
    return render_template('ramadan/login.html')

@ramadan.route('/logout')
@login_required
def logout():
    """Logout handler"""
    logout_user()
    flash(_('U bent uitgelogd.'), 'info')
    return redirect(url_for('ramadan.index'))

@ramadan.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash(_('Dit emailadres is al geregistreerd.'), 'error')
            return redirect(url_for('ramadan.register'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            user_type='visitor'
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(_('Registratie succesvol!'), 'success')
        return redirect(url_for('ramadan.index'))

    return render_template('ramadan/register.html')

@ramadan.route('/set_language/<language>')
def set_language(language):
    """Language setting handler"""
    if language not in ['en', 'nl', 'ar']:
        return redirect(url_for('ramadan.index'))

    session['language'] = language
    return redirect(request.referrer or url_for('ramadan.index'))