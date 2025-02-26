import os
from datetime import datetime, date, timedelta
import calendar
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_babel import _
from werkzeug.utils import secure_filename
from app import db
from models import User, IfterEvent, IfterRegistration, RamadanQuranResource, RamadanVideo, RamadanProgram

ramadan = Blueprint('ramadan', __name__)

def allowed_file(filename, allowed_extensions={'png', 'jpg', 'jpeg'}):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@ramadan.route('/iftar-map')
def iftar_map():
    # Get filter parameter
    family_only = request.args.get('filter') == 'family'

    # Get date parameter or use current date
    try:
        date_str = request.args.get('date')
        if date_str:
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            current_date = date.today()
    except ValueError:
        current_date = date.today()

    # Get the calendar for current month
    cal = calendar.monthcalendar(current_date.year, current_date.month)

    # Calculate first and last day of month
    first_day = current_date.replace(day=1)
    if current_date.month == 12:
        last_day = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)

    # Navigation dates
    if current_date.month == 1:
        prev_month = current_date.replace(year=current_date.year - 1, month=12, day=1)
    else:
        prev_month = current_date.replace(month=current_date.month - 1, day=1)

    if current_date.month == 12:
        next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
    else:
        next_month = current_date.replace(month=current_date.month + 1, day=1)

    # Get all events for this month
    query = IfterEvent.query.filter(
        IfterEvent.date >= first_day,
        IfterEvent.date <= last_day
    )

    if family_only:
        query = query.filter(IfterEvent.is_family_friendly == True)

    events = query.all()

    # Create calendar events dictionary
    calendar_events = {}
    current_day = first_day
    while current_day <= last_day:
        calendar_events[current_day] = {
            'daily': [],
            'weekly': [],
            'single': []
        }
        current_day += timedelta(days=1)

    # Populate events
    for event in events:
        if event.date in calendar_events:
            if event.is_recurring and event.recurrence_type == 'daily':
                calendar_events[event.date]['daily'].append(event)
            elif event.is_recurring and event.recurrence_type == 'weekly':
                calendar_events[event.date]['weekly'].append(event)
            else:
                calendar_events[event.date]['single'].append(event)

    # Get all mosques for admin selection
    mosques = User.query.filter_by(user_type='mosque', is_verified=True).all() if current_user.is_authenticated and current_user.is_admin else None

    return render_template('ramadan/iftar_map.html',
                         calendar=cal,
                         calendar_events=calendar_events,
                         family_only=family_only,
                         current_date=current_date,
                         prev_month=prev_month.strftime('%Y-%m-%d'),
                         next_month=next_month.strftime('%Y-%m-%d'),
                         today=date.today(),
                         mosques=mosques)

@ramadan.route('/iftar/add', methods=['GET', 'POST'])
@login_required
def add_iftar():
    if not (current_user.is_admin or current_user.user_type == 'mosque'):
        flash(_('U heeft geen toegang tot deze pagina.'), 'error')
        return redirect(url_for('ramadan.iftar_map'))

    if request.method == 'POST':
        try:
            # Handle image upload
            image = request.files.get('iftar_image')
            image_url = None
            if image and allowed_file(image.filename):
                filename = secure_filename(f"iftar_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.filename}")
                image_path = os.path.join('static', 'uploads', 'iftar', filename)
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                image.save(image_path)
                image_url = url_for('static', filename=f'uploads/iftar/{filename}')

            # Create new iftar event
            iftar = IfterEvent(
                mosque_id=request.form.get('mosque_id') if current_user.is_admin else current_user.id,
                date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
                start_time=datetime.strptime(request.form.get('start_time'), '%H:%M').time(),
                end_time=datetime.strptime(request.form.get('end_time'), '%H:%M').time() if request.form.get('end_time') else None,
                location=request.form.get('location'),
                capacity=int(request.form.get('capacity')) if request.form.get('capacity') else None,
                is_family_friendly=bool(request.form.get('is_family_friendly')),
                is_recurring=bool(request.form.get('is_recurring')),
                recurrence_type=request.form.get('recurrence_type') if request.form.get('is_recurring') else None,
                recurrence_end_date=datetime.strptime(request.form.get('recurrence_end_date'), '%Y-%m-%d').date() if request.form.get('recurrence_end_date') else None,
                registration_required=bool(request.form.get('registration_required')),
                registration_deadline=datetime.strptime(request.form.get('registration_deadline'), '%Y-%m-%dT%H:%M') if request.form.get('registration_deadline') else None,
                dietary_options=bool(request.form.get('dietary_options')),
                notes=request.form.get('notes'),
                women_entrance=request.form.get('women_entrance'),
                image_url=image_url
            )

            db.session.add(iftar)
            db.session.commit()

            flash(_('Iftar evenement succesvol toegevoegd.'), 'success')
            return redirect(url_for('ramadan.iftar_map'))

        except Exception as e:
            db.session.rollback()
            print(f"Error adding iftar: {e}")
            flash(_('Er is een fout opgetreden bij het toevoegen van het iftar evenement.'), 'error')

    # Get list of mosques for admin selection
    mosques = User.query.filter_by(user_type='mosque', is_verified=True).all() if current_user.is_admin else None

    return render_template('ramadan/add_iftar.html', mosques=mosques)
