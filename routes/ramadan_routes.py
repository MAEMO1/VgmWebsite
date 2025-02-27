import os
from datetime import datetime, date, timedelta
import calendar
import json
import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from flask_babel import _
from werkzeug.utils import secure_filename
from app import db
from models import User, IfterEvent, RamadanProgram, PrayerTime, RamadanQuranResource, RamadanVideo
from services.prayer_times import PrayerTimeService

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ramadan = Blueprint('ramadan', __name__)

@staticmethod
def get_ramadan_dates(year=2025):
    ramadan_start = date(2025, 3, 1)  # 1 Ramadan 1446
    ramadan_end = date(2025, 3, 30)   # 30 Ramadan 1446
    return ramadan_start, ramadan_end

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
    iftar_type = request.args.get('type', 'all')
    selected_mosque = request.args.get('mosque_id', type=int)
    period = request.args.get('period', 'three_days')

    # Get Ramadan dates and today
    ramadan_start, ramadan_end = get_ramadan_dates()
    today = date.today()

    logger.debug(f"Filter parameters - family_only: {family_only}, type: {iftar_type}, mosque: {selected_mosque}, period: {period}")

    # Calculate period filter dates
    if period == 'day':
        period_start = today
        period_end = today
    elif period == 'three_days':
        period_start = today
        period_end = today + timedelta(days=2)
    elif period == 'week':
        period_start = today
        period_end = today + timedelta(days=6)
    else:  # 'all'
        period_start = today
        period_end = ramadan_end

    logger.debug(f"Period dates - start: {period_start}, end: {period_end}")

    # Initialize fresh containers for the current period
    calendar_events = {}
    current_date = period_start
    while current_date <= period_end:
        calendar_events[current_date] = {
            'daily': set(),
            'weekly': set(),
            'single': set()
        }
        current_date += timedelta(days=1)

    logger.debug(f"Initialized calendar_events for dates: {list(calendar_events.keys())}")

    # Initialize result containers
    map_events = []
    sorted_events = []
    processed_occurrences = {}  # Track processed events by unique key

    # Build base query with filters
    base_query = IfterEvent.query
    if family_only:
        base_query = base_query.filter(IfterEvent.is_family_friendly == True)
    if selected_mosque:
        base_query = base_query.filter(IfterEvent.mosque_id == selected_mosque)
    if iftar_type != 'all':
        if iftar_type == 'daily':
            base_query = base_query.filter(IfterEvent.is_recurring == True,
                                       IfterEvent.recurrence_type == 'daily')
        elif iftar_type == 'weekly':
            base_query = base_query.filter(IfterEvent.is_recurring == True,
                                       IfterEvent.recurrence_type == 'weekly')
        elif iftar_type == 'single':
            base_query = base_query.filter(IfterEvent.is_recurring == False)

    events = base_query.all()
    logger.debug(f"Found {len(events)} events matching filters")

    # Process each event
    for event in events:
        logger.debug(f"Processing event ID {event.id} ({event.is_recurring}, {event.recurrence_type if event.is_recurring else 'single'})")

        # Skip past non-recurring events
        if not event.is_recurring and event.date < today:
            logger.debug(f"Skipping past non-recurring event {event.id}")
            continue

        # Process recurring events
        if event.is_recurring:
            # Start from event date or today, whichever is later
            current_date = max(event.date, today)

            # For weekly events, find next occurrence from today
            if event.recurrence_type == 'weekly' and current_date > event.date:
                days_since_start = (current_date - event.date).days
                days_to_next = 7 - (days_since_start % 7)
                if days_to_next < 7:
                    current_date += timedelta(days=days_to_next)
                logger.debug(f"Weekly event {event.id} next occurrence: {current_date}")

            # Process occurrences within period
            while current_date <= min(event.recurrence_end_date or ramadan_end, period_end):
                # Generate unique key for this occurrence
                occurrence_key = f"{event.id}_{current_date}_{event.recurrence_type}"

                if occurrence_key not in processed_occurrences:
                    logger.debug(f"Processing occurrence {occurrence_key}")
                    processed_occurrences[occurrence_key] = True

                    # Only add if date is in current period and calendar
                    if current_date in calendar_events:
                        calendar_events[current_date][event.recurrence_type].add(event.id)
                        add_event_to_lists(event, current_date, event.recurrence_type,
                                         map_events, sorted_events)
                        logger.debug(f"Added event {event.id} to {current_date} as {event.recurrence_type}")
                else:
                    logger.debug(f"Skipping already processed occurrence {occurrence_key}")

                # Move to next occurrence
                if event.recurrence_type == 'daily':
                    current_date += timedelta(days=1)
                elif event.recurrence_type == 'weekly':
                    current_date += timedelta(days=7)

        # Process single events
        else:
            if period_start <= event.date <= period_end:
                occurrence_key = f"{event.id}_{event.date}_single"

                if occurrence_key not in processed_occurrences:
                    logger.debug(f"Processing single event {occurrence_key}")
                    processed_occurrences[occurrence_key] = True

                    if event.date in calendar_events:
                        calendar_events[event.date]['single'].add(event.id)
                        add_event_to_lists(event, event.date, 'single',
                                         map_events, sorted_events)
                        logger.debug(f"Added single event {event.id} to {event.date}")

    # Sort events by date and time
    sorted_events.sort(key=lambda x: (x['date'], x['start_time']))
    logger.debug(f"Final event counts - map: {len(map_events)}, sorted: {len(sorted_events)}")

    # Convert sets to lists for JSON serialization
    calendar_events_json = {}
    for day, events_by_type in calendar_events.items():
        calendar_events_json[day.strftime('%Y-%m-%d')] = {
            event_type: list(events)
            for event_type, events in events_by_type.items()
        }

    # Get all mosques for filtering
    mosques = User.query.filter_by(user_type='mosque', is_verified=True).all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'calendar_events': calendar_events_json,
            'map_events': map_events,
            'sorted_events': sorted_events
        })

    return render_template('ramadan/iftar_map.html',
                       calendar_events=calendar_events,
                       family_only=family_only,
                       iftar_type=iftar_type,
                       period=period,
                       selected_mosque=selected_mosque,
                       today=today,
                       mosques=mosques,
                       google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY'),
                       events_json=json.dumps(map_events),
                       sorted_events=sorted_events,
                       ramadan_start=ramadan_start,
                       ramadan_end=ramadan_end)

@ramadan.route('/iftar/add', methods=['GET', 'POST'])
@login_required
def add_iftar():
    if not (current_user.is_admin or current_user.user_type == 'mosque'):
        flash(_('U heeft geen toegang tot deze pagina.'), 'error')
        return redirect(url_for('ramadan.iftar_map'))

    # Get mosque data - either the current user's mosque or selected mosque for admin
    if current_user.is_admin:
        mosques = User.query.filter_by(user_type='mosque', is_verified=True).all()
        mosques_data = [mosque.to_dict() for mosque in mosques]
        current_mosque = None
    else:
        mosques = None
        mosques_data = []
        current_mosque = current_user

    if request.method == 'POST':
        try:
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

            # Get the date and determine if it's recurring
            start_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            is_recurring = bool(request.form.get('is_recurring'))
            recurrence_type = request.form.get('recurrence_type') if is_recurring else None
            recurrence_end_date = (datetime.strptime(request.form.get('recurrence_end_date'), '%Y-%m-%d').date() 
                                if request.form.get('recurrence_end_date') else None)

            # Calculate all dates for recurring events
            dates = [start_date]
            if is_recurring and recurrence_end_date:
                current_date = start_date
                while current_date <= recurrence_end_date:
                    if recurrence_type == 'daily':
                        current_date += timedelta(days=1)
                    elif recurrence_type == 'weekly':
                        current_date += timedelta(days=7)
                    if current_date <= recurrence_end_date:
                        dates.append(current_date)

            # Handle prayer-based timing
            time_type = request.form.get('time_type')
            if time_type == 'prayer':
                try:
                    # Get prayer times for all dates at once
                    prayer_name = request.form.get('prayer_name', 'maghrib')  # Default to maghrib
                    prayer_source = request.form.get('prayer_source', 'diyanet')  # Default to diyanet
                    prayer_offset = int(request.form.get('prayer_offset', 0))

                    # Fetch all prayer times efficiently
                    prayer_times = PrayerTimeService.get_prayer_times_batch(
                        source=prayer_source,
                        dates=dates,
                        prayer_name=prayer_name,
                        city="Gent"  # Default to Gent
                    )

                    if not prayer_times:
                        flash(_('De gebedstijden konden niet worden opgehaald. Controleer of de API correct is geconfigureerd.'), 'error')
                        return redirect(url_for('ramadan.add_iftar'))

                    missing_dates = [d for d, t in prayer_times.items() if t is None]
                    if missing_dates:
                        flash(_('Gebedstijden ontbreken voor sommige datums. Controleer of alle datums binnen het toegestane bereik vallen.'), 'error')
                        return redirect(url_for('ramadan.add_iftar'))

                    # Create an iftar event for each date with its specific prayer time
                    for event_date in dates:
                        # Get the specific prayer time for this date
                        prayer_time = datetime.strptime(prayer_times[event_date], '%H:%M').time()
                        start_time = (datetime.combine(date.today(), prayer_time) + 
                                    timedelta(minutes=prayer_offset)).time()

                        iftar = IfterEvent(
                            mosque_id=mosque_id,
                            date=event_date,
                            start_time=start_time,  # Using date-specific prayer time
                            end_time=datetime.strptime(request.form.get('end_time'), '%H:%M').time() if request.form.get('end_time') else None,
                            location=request.form.get('location') or mosque.get_full_address(),
                            capacity=int(request.form.get('capacity')) if request.form.get('capacity') else None,
                            is_family_friendly=bool(request.form.get('is_family_friendly')),
                            registration_required=bool(request.form.get('registration_required')),
                            registration_deadline=datetime.strptime(request.form.get('registration_deadline'), '%Y-%m-%dT%H:%M') 
                                                if request.form.get('registration_deadline') else None,
                            dietary_options=bool(request.form.get('dietary_options')),
                            notes=request.form.get('notes'),
                            women_entrance=request.form.get('women_entrance'),
                            image_url=image_url,
                            prayer_based_timing=True,
                            prayer_name=prayer_name,
                            prayer_source=prayer_source,
                            prayer_offset=prayer_offset,
                            is_recurring=is_recurring,
                            recurrence_type=recurrence_type,
                            recurrence_end_date=recurrence_end_date
                        )
                        db.session.add(iftar)

                except ValueError as ve:
                    flash(_('Er is een fout opgetreden bij het verwerken van de gebedstijden. Controleer of alle tijden correct zijn ingevoerd.'), 'error')
                    print(f"Error processing prayer times: {ve}")
                    return redirect(url_for('ramadan.add_iftar'))

            else:
                # Handle specific time
                try:
                    start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
                    end_time = (datetime.strptime(request.form.get('end_time'), '%H:%M').time() 
                               if request.form.get('end_time') else None)

                    # Create an iftar event for each date
                    for event_date in dates:
                        iftar = IfterEvent(
                            mosque_id=mosque_id,
                            date=event_date,
                            start_time=start_time,
                            end_time=end_time,
                            location=request.form.get('location') or mosque.get_full_address(),
                            capacity=int(request.form.get('capacity')) if request.form.get('capacity') else None,
                            is_family_friendly=bool(request.form.get('is_family_friendly')),
                            registration_required=bool(request.form.get('registration_required')),
                            registration_deadline=datetime.strptime(request.form.get('registration_deadline'), '%Y-%m-%dT%H:%M') 
                                                if request.form.get('registration_deadline') else None,
                            dietary_options=bool(request.form.get('dietary_options')),
                            notes=request.form.get('notes'),
                            women_entrance=request.form.get('women_entrance'),
                            image_url=image_url,
                            is_recurring=is_recurring,
                            recurrence_type=recurrence_type,
                            recurrence_end_date=recurrence_end_date
                        )
                        db.session.add(iftar)

                except ValueError as ve:
                    flash(_('Er is een fout opgetreden bij het verwerken van de tijden. Controleer of alle tijden correct zijn ingevoerd.'), 'error')
                    print(f"Error processing times: {ve}")
                    return redirect(url_for('ramadan.add_iftar'))

            try:
                db.session.commit()
                flash(_('Iftar succesvol toegevoegd.'), 'success')
                return redirect(url_for('ramadan.iftar_map'))
            except Exception as e:
                db.session.rollback()
                flash(_('Er is een fout opgetreden bij het opslaan van de iftar.'), 'error')
                print(f"Error saving iftar: {e}")
                return redirect(url_for('ramadan.add_iftar'))

        except Exception as e:
            db.session.rollback()
            flash(_('Er is een fout opgetreden bij het toevoegen van de iftar.'), 'error')
            print(f"Error adding iftar: {e}")
            return redirect(url_for('ramadan.add_iftar'))

    return render_template('ramadan/add_iftar.html', 
                         mosques=mosques,
                         mosques_data=mosques_data,
                         current_mosque=current_mosque,
                         prayer_sources=[
                             ('mawaqit', _('Mawaqit')),
                             ('diyanet', _('Diyanet (via Aladhan)'))
                         ])

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

def allowed_file(filename, allowed_extensions={'png', 'jpg', 'jpeg'}):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def add_event_to_lists(event, current_date, event_type, map_events, sorted_events):
    """Helper function to add events to map_events and sorted_events lists"""
    map_events.append({
        'type': event_type,
        'id': event.id,
        'mosque_name': event.mosque.mosque_name,
        'date': current_date.strftime('%Y-%m-%d'),
        'start_time': event.start_time.strftime('%H:%M'),
        'location': event.location,
        'is_family_friendly': event.is_family_friendly,
        'latitude': event.mosque.latitude,
        'longitude': event.mosque.longitude
    })

    sorted_events.append({
        'type': event_type,
        'mosque': event.mosque,
        'date': current_date,
        'start_time': event.start_time,
        'end_time': event.end_time,
        'location': event.location,
        'is_family_friendly': event.is_family_friendly,
        'registration_required': event.registration_required
    })