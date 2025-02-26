import os
from datetime import datetime, date, timedelta
import calendar
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_babel import _
from werkzeug.utils import secure_filename
from app import db
from models import User, IfterEvent, IfterRegistration, RamadanQuranResource, RamadanVideo, RamadanProgram, PrayerTime

ramadan = Blueprint('ramadan', __name__)

def allowed_file(filename, allowed_extensions={'png', 'jpg', 'jpeg'}):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@ramadan.route('/')
def index():
    # Get today's prayer times
    today = date.today()
    prayer_times = PrayerTime.query.filter_by(date=today).all()

    # Get upcoming Ramadan programs
    programs = RamadanProgram.query.filter(
        RamadanProgram.start_date >= datetime.now()
    ).order_by(RamadanProgram.start_date).limit(3).all()

    # Get upcoming iftar events
    upcoming_iftars = IfterEvent.query.filter(
        IfterEvent.date >= today
    ).order_by(IfterEvent.date).limit(3).all()

    return render_template('ramadan/index.html',
                         prayer_times=prayer_times,
                         programs=programs,
                         upcoming_iftars=upcoming_iftars)

@ramadan.route('/quran-resources')
def quran_resources():
    resources = RamadanQuranResource.query.order_by(RamadanQuranResource.created_at.desc()).all()
    return render_template('ramadan/quran_resources.html', resources=resources)

@ramadan.route('/quran-resources/add', methods=['GET', 'POST'])
@login_required
def add_quran_resource():
    if request.method == 'POST':
        try:
            resource = RamadanQuranResource(
                title=request.form['title'],
                arabic_text=request.form['arabic_text'],
                translation=request.form['translation'],
                explanation=request.form['explanation'],
                category=request.form['category'],
                author_id=current_user.id
            )
            db.session.add(resource)
            db.session.commit()
            flash(_('Quran bron succesvol toegevoegd.'), 'success')
            return redirect(url_for('ramadan.quran_resources'))
        except Exception as e:
            db.session.rollback()
            flash(_('Er is een fout opgetreden bij het toevoegen van de Quran bron.'), 'error')
            print(f"Error adding Quran resource: {e}")

    return render_template('ramadan/add_quran_resource.html')

@ramadan.route('/videos')
def videos():
    videos = RamadanVideo.query.order_by(RamadanVideo.created_at.desc()).all()
    return render_template('ramadan/videos.html', videos=videos)

@ramadan.route('/videos/add', methods=['GET', 'POST'])
@login_required
def add_video():
    if request.method == 'POST':
        try:
            video = RamadanVideo(
                title=request.form['title'],
                description=request.form['description'],
                video_url=request.form['video_url'],
                thumbnail_url=request.form['thumbnail_url'],
                duration=request.form['duration'],
                speaker=request.form['speaker'],
                author_id=current_user.id
            )
            db.session.add(video)
            db.session.commit()
            flash(_('Video succesvol toegevoegd.'), 'success')
            return redirect(url_for('ramadan.videos'))
        except Exception as e:
            db.session.rollback()
            flash(_('Er is een fout opgetreden bij het toevoegen van de video.'), 'error')
            print(f"Error adding video: {e}")

    return render_template('ramadan/add_video.html')

@ramadan.route('/schedule')
def schedule():
    programs = RamadanProgram.query.order_by(RamadanProgram.start_date).all()
    return render_template('ramadan/schedule.html', programs=programs)

@ramadan.route('/schedule/add', methods=['GET', 'POST'])
@login_required
def add_program():
    if request.method == 'POST':
        try:
            program = RamadanProgram(
                title=request.form['title'],
                description=request.form['description'],
                start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M'),
                end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M') if request.form.get('end_date') else None,
                location=request.form['location'],
                organizer_id=current_user.id,
                image_url=request.form['image_url'] if request.form.get('image_url') else None,
                category=request.form['category']
            )
            db.session.add(program)
            db.session.commit()
            flash(_('Programma succesvol toegevoegd.'), 'success')
            return redirect(url_for('ramadan.schedule'))
        except Exception as e:
            db.session.rollback()
            flash(_('Er is een fout opgetreden bij het toevoegen van het programma.'), 'error')
            print(f"Error adding program: {e}")

    return render_template('ramadan/add_program.html')

@ramadan.route('/iftar-map')
def iftar_map():
    # Get filter parameters
    family_only = request.args.get('filter') == 'family'
    iftar_type = request.args.get('type', 'all')  # 'daily', 'weekly', 'single', 'all'
    selected_mosque = request.args.get('mosque_id', type=int)

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

    # Build the base query
    query = IfterEvent.query.filter(
        IfterEvent.date >= first_day,
        IfterEvent.date <= last_day
    )

    # Apply filters
    if family_only:
        query = query.filter(IfterEvent.is_family_friendly == True)

    if selected_mosque:
        query = query.filter(IfterEvent.mosque_id == selected_mosque)

    if iftar_type != 'all':
        if iftar_type == 'daily':
            query = query.filter(IfterEvent.is_recurring == True, 
                               IfterEvent.recurrence_type == 'daily')
        elif iftar_type == 'weekly':
            query = query.filter(IfterEvent.is_recurring == True, 
                               IfterEvent.recurrence_type == 'weekly')
        elif iftar_type == 'single':
            query = query.filter(IfterEvent.is_recurring == False)

    # Materialize the query results
    events = list(query.all())  # Convert to list to ensure query is executed once

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

    # Debug prints
    print(f"\nProcessing events for {current_date.strftime('%B %Y')}")
    print(f"Date range: {first_day} to {last_day}")
    print(f"Found {len(events)} events")
    print("Query filters:")
    print(f"- Family only: {family_only}")
    print(f"- Selected mosque: {selected_mosque}")
    print(f"- Iftar type: {iftar_type}")
    print("\nCalendar Dictionary Keys:")
    for key in calendar_events.keys():
        print(f"Key type: {type(key)}, Value: {key}")
    print("\nEvent details:")

    # Populate events
    for event in events:
        print(f"\nProcessing event: {event.id}")
        print(f"Date: {event.date}, Is recurring: {event.is_recurring}")
        if event.is_recurring:
            print(f"Recurrence type: {event.recurrence_type}")
            print(f"End date: {event.recurrence_end_date}")

            # Calculate all dates this event occurs on within the month
            event_date = event.date
            while event_date <= (event.recurrence_end_date or last_day) and event_date <= last_day:
                if event_date >= first_day:
                    if event.recurrence_type == 'daily':
                        calendar_events[event_date]['daily'].append(event)
                        print(f"Added daily event to {event_date}")
                    elif event.recurrence_type == 'weekly':
                        calendar_events[event_date]['weekly'].append(event)
                        print(f"Added weekly event to {event_date}")

                # Move to next occurrence
                if event.recurrence_type == 'daily':
                    event_date += timedelta(days=1)
                elif event.recurrence_type == 'weekly':
                    event_date += timedelta(days=7)
        else:
            # Single event
            if first_day <= event.date <= last_day:
                calendar_events[event.date]['single'].append(event)
                print(f"Added single event to {event.date}")

    print("\nCalendar events summary:")
    for day, events in calendar_events.items():
        print(f"Key type: {type(day)}, Value: {day}")
        if any(events.values()):
            print(f"{day}: Daily={len(events['daily'])}, Weekly={len(events['weekly'])}, Single={len(events['single'])}")

    # Get all mosques for filtering
    mosques = User.query.filter_by(user_type='mosque', is_verified=True).all()

    return render_template('ramadan/iftar_map.html',
                         calendar=cal,
                         calendar_events=calendar_events,
                         family_only=family_only,
                         iftar_type=iftar_type,
                         selected_mosque=selected_mosque,
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

    # Get mosque data - either the current user's mosque or selected mosque for admin
    if current_user.is_admin:
        mosques = User.query.filter_by(user_type='mosque', is_verified=True).all()
        mosques_data = [mosque.to_dict() for mosque in mosques]  # Serialize mosque data
        current_mosque = None  # Will be set based on form selection
    else:
        mosques = None
        mosques_data = []
        current_mosque = current_user

    if request.method == 'POST':
        try:
            # Debug log: Print form data
            print("\nProcessing Iftar Add Request:")
            print(f"Form data: {request.form}")

            # Handle image upload
            image = request.files.get('iftar_image')
            image_url = None
            if image and allowed_file(image.filename, {'png', 'jpg', 'jpeg'}):
                filename = secure_filename(f"iftar_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.filename}")
                image_path = os.path.join('static', 'uploads', 'iftar', filename)
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                image.save(image_path)
                image_url = url_for('static', filename=f'uploads/iftar/{filename}')

            # Get mosque for the iftar
            mosque_id = request.form.get('mosque_id') if current_user.is_admin else current_user.id
            mosque = User.query.get(mosque_id)

            print(f"Creating iftar for mosque: {mosque.mosque_name} (ID: {mosque_id})")

            # Create new iftar event
            date_str = request.form.get('date')
            start_time_str = request.form.get('start_time')
            end_time_str = request.form.get('end_time')

            print(f"Date: {date_str}, Start time: {start_time_str}, End time: {end_time_str}")

            # Handle recurrence settings
            is_recurring = bool(request.form.get('is_recurring'))
            recurrence_type = request.form.get('recurrence_type') if is_recurring else None
            recurrence_end_date = datetime.strptime(request.form.get('recurrence_end_date'), '%Y-%m-%d').date() if request.form.get('recurrence_end_date') else None

            print(f"Recurrence settings - Is recurring: {is_recurring}, Type: {recurrence_type}, End date: {recurrence_end_date}")

            iftar = IfterEvent(
                mosque_id=mosque_id,
                date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                start_time=datetime.strptime(start_time_str, '%H:%M').time(),
                end_time=datetime.strptime(end_time_str, '%H:%M').time() if end_time_str else None,
                location=request.form.get('location') or mosque.get_full_address(),
                capacity=int(request.form.get('capacity')) if request.form.get('capacity') else None,
                is_family_friendly=bool(request.form.get('is_family_friendly')),
                is_recurring=is_recurring,
                recurrence_type=recurrence_type,
                recurrence_end_date=recurrence_end_date,
                registration_required=bool(request.form.get('registration_required')),
                registration_deadline=datetime.strptime(request.form.get('registration_deadline'), '%Y-%m-%dT%H:%M') if request.form.get('registration_deadline') else None,
                dietary_options=bool(request.form.get('dietary_options')),
                notes=request.form.get('notes'),
                women_entrance=request.form.get('women_entrance'),
                image_url=image_url
            )

            db.session.add(iftar)
            db.session.commit()

            print(f"Successfully created iftar with ID: {iftar.id}")
            flash(_('Iftar evenement succesvol toegevoegd.'), 'success')
            return redirect(url_for('ramadan.iftar_map'))

        except Exception as e:
            db.session.rollback()
            print(f"Error adding iftar: {e}")
            print(f"Exception details: {str(e.__class__.__name__)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            flash(_('Er is een fout opgetreden bij het toevoegen van het iftar evenement.'), 'error')

    return render_template('ramadan/add_iftar.html', 
                         mosques=mosques,
                         mosques_data=mosques_data,  # Pass serialized data
                         current_mosque=current_mosque)



@ramadan.route('/iftar/<int:iftar_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_iftar(iftar_id):
    iftar = IfterEvent.query.get_or_404(iftar_id)

    # Check if user has permission to edit (admin or mosque owner)
    if not (current_user.is_admin or current_user.id == iftar.mosque_id):
        flash(_('Je hebt geen toestemming om dit iftar evenement te bewerken.'), 'error')
        return redirect(url_for('ramadan.iftar_map'))

    if request.method == 'POST':
        try:
            # Update iftar event details
            iftar.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            iftar.start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
            iftar.end_time = datetime.strptime(request.form['end_time'], '%H:%M').time() if request.form.get('end_time') else None
            iftar.location = request.form.get('location')
            iftar.women_entrance = request.form.get('women_entrance')
            iftar.capacity = int(request.form['capacity']) if request.form.get('capacity') else None
            iftar.is_family_friendly = bool(request.form.get('is_family_friendly'))
            iftar.registration_required = bool(request.form.get('registration_required'))
            iftar.dietary_options = bool(request.form.get('dietary_options'))
            iftar.notes = request.form.get('notes')

            if current_user.is_admin:
                iftar.mosque_id = int(request.form['mosque_id'])

            db.session.commit()
            flash(_('Iftar evenement succesvol bijgewerkt.'), 'success')
            return redirect(url_for('ramadan.iftar_map'))

        except Exception as e:
            db.session.rollback()
            flash(_('Er is een fout opgetreden bij het bijwerken van het iftar evenement.'), 'error')
            print(f"Error updating iftar event: {e}")

    # Get all mosques for admin selection
    mosques = User.query.filter_by(user_type='mosque', is_verified=True).all() if current_user.is_admin else None
    return render_template('ramadan/edit_iftar.html',
                         iftar=iftar,
                         mosques=mosques)

@ramadan.route('/iftar/<int:iftar_id>/delete', methods=['POST'])
@login_required
def delete_iftar(iftar_id):
    iftar = IfterEvent.query.get_or_404(iftar_id)

    # Check if user has permission to delete (admin or mosque owner)
    if not (current_user.is_admin or current_user.id == iftar.mosque_id):
        flash(_('Je hebt geen toestemming om dit iftar evenement te verwijderen.'), 'error')
        return redirect(url_for('ramadan.iftar_map'))

    try:
        db.session.delete(iftar)
        db.session.commit()
        flash(_('Iftar evenement succesvol verwijderd.'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Er is een fout opgetreden bij het verwijderen van het iftar evenement.'), 'error')
        print(f"Error deleting iftar event: {e}")

    return redirect(url_for('ramadan.iftar_map'))