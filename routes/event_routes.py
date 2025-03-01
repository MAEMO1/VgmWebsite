from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os
from app import db
from models import Event, EventRegistration, User

# Create blueprint with url_prefix
events = Blueprint('events', __name__, url_prefix='/events')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@events.route('/')
def event_list():
    # Get all mosques for the filter dropdown
    mosques = User.query.filter_by(user_type='mosque', is_verified=True).order_by(User.username).all()

    # Get upcoming events
    upcoming_events = Event.query.filter(
        Event.date >= datetime.utcnow()
    ).order_by(Event.date).all()

    return render_template('events/list.html',
                         mosques=mosques,
                         events=upcoming_events)

@events.route('/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    is_registered = False
    if current_user.is_authenticated:
        is_registered = EventRegistration.query.filter_by(
            user_id=current_user.id, 
            event_id=event_id,
            status='registered'
        ).first() is not None

    return render_template('events/detail.html',
                         event=event,
                         is_registered=is_registered)

@events.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        # Get event type from form
        event_type = request.form.get('event_type', 'individual')

        # Only allow admin users to create VGM events
        if event_type == 'vgm' and not current_user.is_admin:
            flash('You do not have permission to create VGM events.', 'error')
            return redirect(url_for('events.event_list'))

        event = Event(
            title=request.form['title'],
            description=request.form['description'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M'),
            location=request.form['location'],
            max_participants=int(request.form['max_participants']) if request.form['max_participants'] else None,
            registration_required=bool(request.form.get('registration_required')),
            event_type=event_type,
            is_collaboration=(event_type == 'collaboration'),
            organizer_id=current_user.id
        )

        # Handle flyer upload (from original code)
        if 'flyer' in request.files:
            flyer = request.files['flyer']
            if flyer and allowed_file(flyer.filename):
                filename = secure_filename(flyer.filename)
                # Save the file to a specific directory
                upload_folder = os.path.join('static', 'uploads', 'flyers')
                os.makedirs(upload_folder, exist_ok=True)
                flyer_path = os.path.join(upload_folder, filename)
                flyer.save(flyer_path)
                event.flyer_url = os.path.join('uploads', 'flyers', filename)

        db.session.add(event)
        db.session.commit()

        flash('Event successfully created!', 'success')
        return redirect(url_for('events.event_detail', event_id=event.id))

    return render_template('events/create.html')

@events.route('/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.registration_required:
        existing_registration = EventRegistration.query.filter_by(
            user_id=current_user.id,
            event_id=event_id
        ).first()

        if existing_registration:
            flash('You are already registered for this event.', 'info')
        else:
            registration = EventRegistration(
                user_id=current_user.id,
                event_id=event_id
            )
            db.session.add(registration)
            db.session.commit()
            flash('Successfully registered for the event!', 'success')

    return redirect(url_for('events.event_detail', event_id=event_id))

@events.route('/<int:event_id>/cancel-registration', methods=['POST'])
@login_required
def cancel_registration(event_id):
    registration = EventRegistration.query.filter_by(
        user_id=current_user.id,
        event_id=event_id,
        status='registered'
    ).first_or_404()

    registration.status = 'cancelled'
    db.session.commit()
    flash('Your registration has been cancelled.', 'info')
    return redirect(url_for('events.event_detail', event_id=event_id))

@events.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    # Check if user has permission to delete
    if not (current_user.is_admin or 
            (current_user.user_type == 'mosque' and event.organizer_id == current_user.id)):
        flash('You do not have permission to delete this event.', 'error')
        return redirect(url_for('events.event_detail', event_id=event_id))

    try:
        # Delete associated records first
        EventRegistration.query.filter_by(event_id=event_id).delete()

        # Delete the event
        db.session.delete(event)
        db.session.commit()
        flash('Event successfully deleted.', 'success')
        return redirect(url_for('events.event_list'))

    except Exception as e:
        db.session.rollback()
        print(f"Error deleting event: {e}")
        flash('An error occurred while deleting the event.', 'error')
        return redirect(url_for('events.event_detail', event_id=event_id))

@events.route('/api/calendar-events')
def calendar_events():
    # Get filter parameters
    mosque_id = request.args.get('mosque_id', type=int)
    event_type = request.args.get('event_type')

    start = request.args.get('start', type=str)
    end = request.args.get('end', type=str)

    # Convert string dates to datetime objects
    start_date = datetime.fromisoformat(start.replace('Z', '+00:00')) if start else datetime.utcnow()
    end_date = datetime.fromisoformat(end.replace('Z', '+00:00')) if end else datetime.utcnow() + timedelta(days=30)

    # Build query
    query = Event.query.filter(
        Event.date >= start_date,
        Event.date <= end_date
    )

    # Apply filters if provided
    if mosque_id:
        query = query.filter(Event.organizer_id == mosque_id)
    elif event_type:
        query = query.filter(Event.event_type == event_type)

    events = query.all()

    # Format events for FullCalendar
    event_list = []
    for event in events:
        event_data = {
            'id': event.id,
            'title': event.title,
            'start': event.date.isoformat(),
            'end': (event.date + timedelta(hours=2)).isoformat(),  # Assuming 2-hour default duration
            'extendedProps': {
                'eventType': event.event_type,
                'description': event.description,
                'organizerId': event.organizer_id
            }
        }
        event_list.append(event_data)

    return jsonify(event_list)