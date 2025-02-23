from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from models import Event, EventRegistration, EventNotification, User, EventMosqueCollaboration

# Create blueprint with url_prefix
events = Blueprint('events', __name__, url_prefix='/events')

@events.route('/api/calendar-events')
def calendar_events():
    start = request.args.get('start', type=str)
    end = request.args.get('end', type=str)

    # Convert string dates to datetime objects
    start_date = datetime.fromisoformat(start.replace('Z', '+00:00')) if start else datetime.utcnow()
    end_date = datetime.fromisoformat(end.replace('Z', '+00:00')) if end else datetime.utcnow() + timedelta(days=30)

    # Query all events within the date range
    events = Event.query.filter(
        Event.date >= start_date,
        Event.date <= end_date
    ).all()

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
                'description': event.description
            }
        }
        event_list.append(event_data)

    return jsonify(event_list)

@events.route('/')
def event_list():
    # Get VGM events (highest priority)
    vgm_events = Event.query.filter(
        Event.event_type == 'vgm',
        Event.date >= datetime.utcnow()
    ).order_by(Event.date).all()

    # Get collaboration events
    collab_events = Event.query.filter(
        Event.event_type == 'collaboration',
        Event.date >= datetime.utcnow()
    ).order_by(Event.date).all()

    # Get individual mosque events
    individual_events = Event.query.filter(
        Event.event_type == 'individual',
        Event.date >= datetime.utcnow()
    ).order_by(Event.date).all()

    return render_template('events/list.html',
                         vgm_events=vgm_events,
                         collab_events=collab_events,
                         individual_events=individual_events)

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

    # Get collaborating mosques for this event
    collaborations = EventMosqueCollaboration.query.filter_by(event_id=event_id).all()

    return render_template('events/detail.html',
                         event=event,
                         is_registered=is_registered,
                         collaborations=collaborations)

@events.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        event_type = request.form.get('event_type')
        collaborating_mosque_ids = request.form.getlist('collaborating_mosques[]')

        event = Event(
            title=request.form['title'],
            description=request.form['description'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M'),
            location=request.form['location'],
            max_participants=int(request.form['max_participants']) if request.form['max_participants'] else None,
            registration_required=bool(request.form.get('registration_required')),
            reminder_before=int(request.form['reminder_before']) if request.form['reminder_before'] else None,
            event_type=event_type,
            is_featured=bool(request.form.get('is_featured')),
            organizer_id=current_user.id
        )

        if event_type == 'collaboration':
            for mosque_id in collaborating_mosque_ids:
                collab = EventMosqueCollaboration(
                    event_id=event.id,
                    mosque_id=int(mosque_id),
                    role='co-organizer'
                )
                db.session.add(collab)

        db.session.add(event)
        db.session.commit()

        # Create notifications for users who want to be notified about new events
        users = User.query.filter_by(notify_new_events=True).all()
        for user in users:
            notification = EventNotification(
                user_id=user.id,
                event_id=event.id,
                type='new_event',
                message=f'New event: {event.title} on {event.date.strftime("%B %d, %Y")}'
            )
            db.session.add(notification)
        db.session.commit()

        flash('Event created successfully!', 'success')
        return redirect(url_for('events.event_detail', event_id=event.id))

    # Get all mosques for collaboration selection
    mosques = User.query.filter_by(user_type='mosque', is_verified=True).all()
    return render_template('events/create.html', mosques=mosques)

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

@events.route('/notifications')
@login_required
def user_notifications():
    notifications = EventNotification.query.filter_by(
        user_id=current_user.id
    ).order_by(EventNotification.sent_at.desc()).all()
    return render_template('events/notifications.html', notifications=notifications)

@events.route('/notification-settings', methods=['GET', 'POST'])
@login_required
def notification_settings():
    if request.method == 'POST':
        current_user.notify_new_events = bool(request.form.get('notify_new_events'))
        current_user.notify_event_changes = bool(request.form.get('notify_event_changes'))
        current_user.notify_event_reminders = bool(request.form.get('notify_event_reminders'))
        db.session.commit()
        flash('Notification settings updated successfully!', 'success')
        return redirect(url_for('events.notification_settings'))
    return render_template('events/notification_settings.html')


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
        EventNotification.query.filter_by(event_id=event_id).delete()
        EventMosqueCollaboration.query.filter_by(event_id=event_id).delete()

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