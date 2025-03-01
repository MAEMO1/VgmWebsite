from datetime import datetime, date
import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _
from sqlalchemy.orm import joinedload
from werkzeug.security import check_password_hash, generate_password_hash
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

        # Convert events to dictionaries for JSON serialization
        events_data = [{
            'id': event.id,
            'mosque_id': event.mosque_id,
            'mosque_name': event.mosque.mosque_name if event.mosque else None,
            'date': event.date.strftime('%Y-%m-%d'),
            'start_time': event.start_time.strftime('%H:%M'),
            'end_time': event.end_time.strftime('%H:%M') if event.end_time else None,
            'location': event.location,
            'is_family_friendly': event.is_family_friendly,
            'capacity': event.capacity
        } for event in events]

        # Get mosques for dropdown
        mosques = User.query.filter_by(user_type='mosque', is_verified=True).all()
        logger.info(f"Found {len(mosques)} verified mosques")

        # Template context
        context = {
            'events': events_data,  # Using serializable event data
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
        return render_template('ramadan/index.html', upcoming_iftars=[])

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

        # Here you would typically send the email
        flash(_('Bedankt voor uw bericht. We nemen zo spoedig mogelijk contact met u op.'), 'success')
        return redirect(url_for('ramadan.contact'))

    return render_template('ramadan/contact.html')

@ramadan.route('/mosques')
def mosques():
    """Mosques overview page"""
    mosque_users = User.query.filter_by(user_type='mosque', is_verified=True).all()
    return render_template('ramadan/mosques.html', 
                         mosques=mosque_users,
                         google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY'))

@ramadan.route('/prayer_times')
def prayer_times():
    """Prayer times page"""
    try:
        today = datetime.today().date()
        prayer_times = []  # You would typically fetch these from your database
        return render_template('ramadan/prayer_times.html', prayer_times=prayer_times)
    except Exception as e:
        logger.error(f"Error fetching prayer times: {e}")
        flash(_('Er is een fout opgetreden bij het laden van de gebedstijden.'), 'error')
        return render_template('ramadan/prayer_times.html', prayer_times=[])

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

@ramadan.route('/add-iftar', methods=['GET', 'POST'])
@login_required
def add_iftar():
    """Add new iftar event route"""
    # Only mosque users and admins can add iftars
    if not current_user.is_authenticated or (current_user.user_type != 'mosque' and not current_user.is_admin):
        flash(_('U heeft geen toestemming om iftars toe te voegen.'), 'error')
        return redirect(url_for('ramadan.iftar_map'))

    if request.method == 'POST':
        try:
            logger.debug("Processing iftar form submission")
            # Get form data
            date_str = request.form.get('date')
            time_str = request.form.get('start_time')
            location = request.form.get('location')

            logger.debug(f"Form data received - Date: {date_str}, Time: {time_str}, Location: {location}")

            # Parse date and time
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(time_str, '%H:%M').time()

            # Create new iftar event
            iftar = IfterEvent(
                mosque_id=current_user.id,  # Use current user's ID as mosque_id
                date=date,
                start_time=start_time,
                location=location,
                is_family_friendly='is_family_friendly' in request.form,
                capacity=request.form.get('max_attendees', type=int)  # Map max_attendees to capacity
            )

            logger.debug(f"Created IfterEvent object: mosque_id={iftar.mosque_id}, date={iftar.date}")

            db.session.add(iftar)
            db.session.commit()
            logger.info(f"Successfully added new iftar event for mosque {iftar.mosque_id}")

            flash(_('Iftar is succesvol toegevoegd.'), 'success')
            return redirect(url_for('ramadan.iftar_map'))

        except ValueError as ve:
            logger.error(f"Validation error in add_iftar: {ve}")
            db.session.rollback()
            flash(_('Controleer of alle velden correct zijn ingevuld.'), 'error')
        except Exception as e:
            logger.error(f"Error adding iftar: {e}", exc_info=True)
            db.session.rollback()
            flash(_('Er is een fout opgetreden bij het toevoegen van de iftar.'), 'error')

    # For GET request, show the form
    return render_template('ramadan/add_iftar.html')