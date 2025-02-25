from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app import db
from models import User, BoardMember, Event, PrayerTime, BlogPost, MosqueImage, MosqueVideo, Donation, MosqueNotificationPreference, MosqueBoardMember, MosqueHistory, MosquePhoto, ContentChangeLog, EventMosqueCollaboration, FundraisingCampaign, IfterEvent, IfterRegistration, RamadanQuranResource, RamadanVideo, RamadanProgram # Added Ramadan models
from datetime import datetime, date, timedelta
import os
from utils.canva_client import canva_client # Added import statement


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

        # Check if mosque exists in official list
        official_mosque = User.query.filter(
            db.and_(
                User.user_type == 'mosque',
                User.mosque_name == mosque_name,
                User.mosque_street == street,
                User.mosque_number == number,
                User.is_verified == True
            )
        ).first()

        verification_status = 'pending'
        verification_note = None

        if official_mosque:
            if official_mosque.email != "info@" + mosque_name.lower().replace(" ", "") + ".be":
                verification_status = 'requires_review'
                verification_note = 'Mosque exists in official list but requires admin verification.'
        else:
            verification_status = 'requires_review'
            verification_note = 'Mosque not found in official list. Requires admin verification.'

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
            verification_status=verification_status,
            verification_note=verification_note,
            is_verified=False  # All mosques need verification
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
        # Get next event
        next_event = Event.query.filter(
            Event.date >= datetime.utcnow()
        ).order_by(Event.date).first()

        # Get latest blog posts
        latest_posts = BlogPost.query.filter_by(
            published=True
        ).order_by(BlogPost.created_at.desc()).limit(3).all()

        # Get today's prayer times
        today = datetime.today().date()
        prayer_times = PrayerTime.query.filter_by(date=today).all()

        # Get active campaigns
        active_campaigns = FundraisingCampaign.query.filter_by(
            is_active=True
        ).order_by(FundraisingCampaign.start_date.desc()).limit(3).all()

        return render_template('index.html', 
                            next_event=next_event,
                            latest_posts=latest_posts,
                            prayer_times=prayer_times,
                            campaigns=active_campaigns)
    except Exception as e:
        print(f"Error loading index page: {e}")
        return render_template('index.html', 
                            next_event=None,
                            latest_posts=[],
                            prayer_times=[],
                            campaigns=[])

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

@routes.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Here you would typically send the email or store the contact message
        # For now, just show a success message
        flash(_('Thank you for your message. We will get back to you soon.'), 'success')
        return redirect(url_for('main.contact'))

    return render_template('contact.html')

@routes.route('/mosque/<int:mosque_id>')
def mosque_detail(mosque_id):
    mosque = User.query.filter_by(id=mosque_id, user_type='mosque', is_verified=True).first_or_404()

    # Get today's prayer times
    today = datetime.today().date()
    prayer_times = PrayerTime.query.filter_by(mosque_id=mosque_id, date=today).all()

    # Get upcoming events that are either organized by or collaborated with the mosque
    events = Event.query.filter(
        db.or_(
            Event.mosque_id == mosque_id,
            Event.id.in_(
                db.session.query(EventMosqueCollaboration.event_id).filter_by(mosque_id=mosque_id)
            )
        ),
        Event.date >= datetime.utcnow()
    ).order_by(Event.date).limit(5).all()

    return render_template('mosque_detail.html',
                         mosque=mosque,
                         prayer_times=prayer_times,
                         events=events,
                         google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY'))

@routes.route('/mosque/<int:mosque_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_mosque(mosque_id):
    mosque = User.query.get_or_404(mosque_id)

    # Check if user has permission to edit
    if not (current_user.is_admin or current_user.id == mosque.id):
        flash(_('Je hebt geen toestemming om deze moskee te bewerken.'), 'error')
        return redirect(url_for('main.mosque_detail', mosque_id=mosque_id))

    if request.method == 'POST':
        try:
            # Store old values for change logging
            old_values = {
                'mission_statement': mosque.mission_statement,
                'vision_statement': mosque.vision_statement,
                'activities': mosque.activities,
                'facilities': mosque.facilities,
                'languages': mosque.languages,
                'capacity': mosque.capacity,
                'foundation_year': mosque.foundation_year,
                'accessibility_features': mosque.accessibility_features,
                'parking_info': mosque.parking_info,
                'public_transport': mosque.public_transport
            }

            # Update basic profile information
            mosque.mission_statement = request.form.get('mission_statement')
            mosque.vision_statement = request.form.get('vision_statement')
            mosque.activities = request.form.get('activities')
            mosque.facilities = request.form.get('facilities')
            mosque.languages = request.form.get('languages')
            mosque.capacity = int(request.form.get('capacity')) if request.form.get('capacity') else None
            mosque.foundation_year = int(request.form.get('foundation_year')) if request.form.get('foundation_year') else None
            mosque.accessibility_features = request.form.get('accessibility_features')
            mosque.parking_info = request.form.get('parking_info')
            mosque.public_transport = request.form.get('public_transport')

            # Contact information
            mosque.mosque_email = request.form.get('mosque_email')
            mosque.mosque_website = request.form.get('mosque_website')
            mosque.mosque_phone = request.form.get('mosque_phone')
            mosque.mosque_fax = request.form.get('mosque_fax')
            mosque.emergency_contact = request.form.get('emergency_contact')
            mosque.emergency_phone = request.form.get('emergency_phone')

            # Social media links
            mosque.facebook_url = request.form.get('facebook_url')
            mosque.twitter_url = request.form.get('twitter_url')
            mosque.instagram_url = request.form.get('instagram_url')
            mosque.youtube_url = request.form.get('youtube_url')
            mosque.whatsapp_number = request.form.get('whatsapp_number')

            # Log changes to profile information
            new_values = {
                'mission_statement': mosque.mission_statement,
                'vision_statement': mosque.vision_statement,
                'activities': mosque.activities,
                'facilities': mosque.facilities,
                'languages': mosque.languages,
                'capacity': mosque.capacity,
                'foundation_year': mosque.foundation_year,
                'accessibility_features': mosque.accessibility_features,
                'parking_info': mosque.parking_info,
                'public_transport': mosque.public_transport
            }

            # Create change log for profile updates
            if any(old_values[k] != new_values[k] for k in old_values.keys()):
                change_log = ContentChangeLog(
                    mosque_id=mosque.id,
                    changed_by_id=current_user.id,
                    content_type='profile',
                    change_type='update',
                    old_value=old_values,
                    new_value=new_values
                )
                db.session.add(change_log)

            # Handle board members
            names = request.form.getlist('board_member_names[]')
            roles = request.form.getlist('board_member_roles[]')
            emails = request.form.getlist('board_member_emails[]')
            phones = request.form.getlist('board_member_phones[]')
            bios = request.form.getlist('board_member_bios[]')
            photos = request.files.getlist('board_member_photos[]')

            # Remove existing board members
            MosqueBoardMember.query.filter_by(mosque_id=mosque.id).delete()

            # Add new board members
            for i, (name, role) in enumerate(zip(names, roles)):
                if name and role:  # Only add if name and role are provided
                    photo = photos[i] if i < len(photos) and photos[i].filename else None
                    photo_url = None
                    if photo and allowed_file(photo.filename):
                        filename = secure_filename(f"board_{mosque.id}_{i}_{photo.filename}")
                        photo_path = os.path.join('static', 'uploads', 'board', filename)
                        os.makedirs(os.path.dirname(photo_path), exist_ok=True)
                        photo.save(photo_path)
                        photo_url = url_for('static', filename=f'uploads/board/{filename}')

                    board_member = MosqueBoardMember(
                        mosque_id=mosque.id,
                        name=name,
                        role=role,
                        contact_email=emails[i] if i < len(emails) else None,
                        contact_phone=phones[i] if i < len(phones) else None,
                        bio=bios[i] if i < len(bios) else None,
                        photo_url=photo_url
                    )
                    db.session.add(board_member)

            # Handle history entries
            years = request.form.getlist('history_years[]')
            titles = request.form.getlist('history_titles[]')
            descriptions = request.form.getlist('history_descriptions[]')
            history_photos = request.files.getlist('history_photos[]')

            # Remove existing history entries
            MosqueHistory.query.filter_by(mosque_id=mosque.id).delete()

            # Add new history entries
            for i, (year, title, description) in enumerate(zip(years, titles, descriptions)):
                if year and title and description:
                    photo = history_photos[i] if i < len(history_photos) and history_photos[i].filename else None
                    photo_url = None
                    if photo and allowed_file(photo.filename):
                        filename = secure_filename(f"history_{mosque.id}_{i}_{photo.filename}")
                        photo_path = os.path.join('static', 'uploads', 'history', filename)
                        os.makedirs(os.path.dirname(photo_path), exist_ok=True)
                        photo.save(photo_path)
                        photo_url = url_for('static', filename=f'uploads/history/{filename}')

                    history_entry = MosqueHistory(
                        mosque_id=mosque.id,
                        year=int(year),
                        title=title,
                        description=description,
                        photo_url=photo_url
                    )
                    db.session.add(history_entry)

            # Handle photo gallery
            if 'new_photos[]' in request.files:
                for photo in request.files.getlist('new_photos[]'):
                    if photo and allowed_file(photo.filename):
                        filename = secure_filename(photo.filename)
                        photo_path = os.path.join('static', 'uploads', 'gallery', filename)
                        os.makedirs(os.path.dirname(photo_path), exist_ok=True)
                        photo.save(photo_path)
                        photo_url = url_for('static', filename=f'uploads/gallery/{filename}')

                        mosque_photo = MosquePhoto(
                            mosque_id=mosque.id,
                            url=photo_url
                        )
                        db.session.add(mosque_photo)

            # Handle photo removals
            remove_photos = request.form.getlist('remove_photos[]')
            if remove_photos:
                MosquePhoto.query.filter(MosquePhoto.id.in_(remove_photos)).delete(synchronize_session=False)

            # Update photo details
            photo_titles = request.form.getlist('photo_titles[]')
            photo_descriptions = request.form.getlist('photo_descriptions[]')
            photo_featured = request.form.getlist('photo_featured[]')

            for photo in mosque.photos:
                idx = mosque.photos.index(photo)
                if idx < len(photo_titles):
                    photo.title = photo_titles[idx]
                if idx < len(photo_descriptions):
                    photo.description = photo_descriptions[idx]
                photo.is_featured = str(photo.id) in photo_featured

            db.session.commit()
            flash(_('Moskee informatie succesvol bijgewerkt.'), 'success')
            return redirect(url_for('main.mosque_detail', mosque_id=mosque_id))

        except Exception as e:
            db.session.rollback()
            flash(_('Er is een fout opgetreden bij het bijwerken van de moskee informatie.'), 'error')
            print(f"Error updating mosque: {e}")

    return render_template('edit_mosque.html', mosque=mosque, current_year=datetime.now().year)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from werkzeug.utils import secure_filename

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

@routes.route('/about')
def about():
    # Initialize default board members if count is not correct
    expected_board_count = 9
    if BoardMember.query.count() != expected_board_count:
        print("\nStarting board member initialization...")
        print("----------------------------------------")

        # First clear any existing board members
        BoardMember.query.delete()
        db.session.commit()
        print("Cleared existing board members")

        default_board_members = [
            {
                'name': 'Abd El Motleb Omar Mohamed',
                'role': 'Voorzitter',
                'mosque_name': 'Islamitisch Cultureel centrum - Badr',
            },
            {
                'name': 'Alci Bilal',
                'role': 'Bestuurder',
                'mosque_name': 'Groene Moskee Fatih',
            },
            {
                'name': 'Cetin Mutlu',
                'role': 'Bestuurder',
                'mosque_name': 'Eyup sultan Camii',
            },
            {
                'name': 'Demirogullari Nedim',
                'role': 'Bestuurder',
                'mosque_name': 'Tevhid Camii',
            },
            {
                'name': 'El Bakali Mohamed',
                'role': 'Bestuurder',
                'mosque_name': 'Moskee Al Fath',
            },
            {
                'name': 'Ibrahimi Hikmatullah',
                'role': 'Bestuurder',
                'mosque_name': 'Afghan Attaqwa moskee',
            },
            {
                'name': 'Köse Demirali',
                'role': 'Bestuurder',
                'mosque_name': 'Eyup sultan Camii',
            },
            {
                'name': 'Saman Sheikh',
                'role': 'Bestuurder',
                'mosque_name': 'Moskee Salahaddien',
            },
            {
                'name': 'Senel Furkan',
                'role': 'Bestuurder',
                'mosque_name': 'Tevhid Camii',
            }
        ]

        # Current term: 2024-2027
        term_start = date(2024, 1, 1)
        term_end = date(2027, 12, 31)

        # Create board images directory if it doesn't exist
        board_dir = os.path.join('static', 'images', 'board')
        os.makedirs(board_dir, exist_ok=True)

        print("\nAttempting to add board members...")
        print("----------------------------------------")

        for member_data in default_board_members:
            try:
                # Find the associated mosque with detailed logging
                mosque = User.query.filter_by(
                    user_type='mosque',
                    mosque_name=member_data['mosque_name']
                ).first()

                print(f"\nProcessing board member: {member_data['name']}")
                print(f"Looking for mosque: {member_data['mosque_name']}")

                if mosque:
                    print(f"Found mosque: {mosque.mosque_name} (ID: {mosque.id})")

                    # Generate member image name
                    image_name = f"member_{member_data['name'].lower().replace(' ', '_')}.jpg"

                    board_member = BoardMember(
                        name=member_data['name'],
                        role=member_data['role'],
                        mosque_id=mosque.id,
                        term_start=term_start,
                        term_end=term_end,
                        image=image_name
                    )
                    db.session.add(board_member)
                    print(f"Added board member successfully")
                else:
                    print(f"ERROR: Mosque not found: {member_data['mosque_name']}")
                    # Query to show similar mosque names
                    similar_mosques = User.query.filter(
                        User.user_type == 'mosque',
                        User.mosque_name.ilike(f"%{member_data['mosque_name'].split()[-1]}%")
                    ).all()
                    if similar_mosques:
                        print("Similar mosque names found:")
                        for m in similar_mosques:
                            print(f"- {m.mosque_name}")

            except Exception as e:
                print(f"Error adding board member {member_data['name']}: {str(e)}")
                db.session.rollback()

        try:
            db.session.commit()
            print("\nSuccessfully committed all board members to database")
            print(f"Number of board members: {BoardMember.query.count()}")
            print("----------------------------------------\n")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing board members: {e}")

    # Get all available terms
    terms = db.session.query(
        BoardMember.term_start,
        BoardMember.term_end
    ).distinct().group_by(BoardMember.term_start, BoardMember.term_end).all()

    # Get the requested term or default to current term
    term_start_str = request.args.get('term')
    if term_start_str:
        term_start = datetime.strptime(term_start_str, '%Y-%m-%d').date()
        # Get the corresponding term_end for this term_start
        term = next((t for t in terms if t[0] == term_start), None)
        term_end = term[1] if term else None
    else:  # Default to current ormost recent term
        current_date = date.today()
        latest_term = BoardMember.query.filter(
            BoardMember.term_end >= current_date
        ).order_by(BoardMember.term_start.desc()).first()

        if latest_term:
            term_start = latest_term.term_start
            term_end = latest_term.term_end
        else:
            term_start = date(current_date.year, 1, 1)
            term_end = date(current_date.year, 12, 31)

    # Get board members for the selected term
    board_members = BoardMember.query.filter(
        BoardMember.term_start == term_start
    ).all()

    # Get all mosques for the admin form
    mosques = User.query.filter_by(user_type='mosque', is_verified=True).all()

    return render_template('about.html',
                       board_members=board_members,
                       terms=terms,
                       current_term_start=term_start,
                       current_term_end=term_end,
                       mosques=mosques)

@routes.route('/memorandum')
def memorandum():
    return render_template('memorandum.html')

@routes.route('/manage_board_members', methods=['POST'])
@login_required
def manage_board_members():
    if not current_user.is_admin:
        flash('Alleen beheerders kunnen bestuursleden beheren.', 'error')
        return redirect(url_for('main.about'))

    try:
        term_start = datetime.strptime(request.form['term_start'], '%Y-%m-%d').date()
        term_end = datetime.strptime(request.form['term_end'], '%Y-%m-%d').date()

        # Validate term dates
        if term_end <= term_start:
            flash('De einddatum moet na de startdatum liggen.', 'error')
            return redirect(url_for('main.about'))

        # Get existing board members for this term to preserve images if not updated
        existing_members = {member.id: member.image for member in BoardMember.query.filter_by(term_start=term_start).all()}

        # Remove existing board members for this term
        BoardMember.query.filter_by(term_start=term_start).delete()

        names = request.form.getlist('names[]')
        roles = request.form.getlist('roles[]')
        mosque_ids = request.form.getlist('mosque_ids[]')
        member_ids = request.form.getlist('member_ids[]')  # Added to track existing members
        photos = request.files.getlist('photos[]')

        for i, (name, role, mosque_id, member_id) in enumerate(zip(names, roles, mosque_ids, member_ids)):
            photo = photos[i] if i < len(photos) else None

            # Handle photo upload or keep existing photo
            image_filename = None
            if photo and photo.filename and allowed_file(photo.filename):
                # Create board images directory if it doesn't exist
                board_dir = os.path.join('static', 'images', 'board')
                os.makedirs(board_dir, exist_ok=True)

                # Generate unique filename
                image_filename = f"member_{name.lower().replace(' ', '_')}.jpg"
                photo.save(os.path.join(board_dir, image_filename))
            elif member_id and member_id in existing_members:
                # Keep existing photo if no new photo was uploaded
                image_filename = existing_members[member_id]

            # Create board member
            board_member = BoardMember(
                name=name,
                role=role,
                mosque_id=mosque_id,
                image=image_filename,
                term_start=term_start,
                term_end=term_end
            )
            db.session.add(board_member)

        db.session.commit()
        flash('Bestuursleden succesvol bijgewerkt.', 'success')

    except Exception as e:
        db.session.rollback()
        print(f"Error managing board members: {e}")
        flash('Er is een fout opgetreden bij het bijwerken van de bestuursleden.', 'error')

    return redirect(url_for('main.about'))


@routes.route('/upload_board_photo', methods=['POST'])
@login_required
def upload_board_photo():
    if not current_user.is_admin:
        flash('Alleen beheerders kunnen bestuurderfoto\'s uploaden.', 'error')
        return redirect(url_for('main.about'))

    try:
        if 'photo' not in request.files:
            flash('Geen foto geselecteerd.', 'error')
            return redirect(url_for('main.about'))

        photo = request.files['photo']
        member_id = request.form.get('member_id')

        if photo.filename == '':
            flash('Geen foto geselecteerd.', 'error')
            return redirect(url_for('main.about'))

        if not allowed_file(photo.filename):
            flash('Ongeldig bestandstype. Gebruik .jpg, .jpeg, .png of .gif bestanden.', 'error')
            return redirect(url_for('main.about'))

        # Create the board directory if it doesn't exist
        board_dir = os.path.join('static', 'images', 'board')
        os.makedirs(board_dir, exist_ok=True)

        # Save the file with the correct name based on member_id
        filename = f"{member_id}.jpg"
        filepath = os.path.join(board_dir, filename)
        photo.save(filepath)

        flash('Foto succesvol geüpload.', 'success')
        return redirect(url_for('main.about'))

    except Exception as e:
        print(f"Error uploading photo: {e}")
        flash('Er is een fout opgetreden bij het uploaden van de foto.', 'error')
        return redirect(url_for('main.about'))

@routes.route('/register/admin/<code>', methods=['GET', 'POST'])
def register_admin(code):
    # Check if the registration code is valid
    ADMIN_REGISTRATION_CODE = "VGM2024"  # This should be an environment variable in production

    if code != ADMIN_REGISTRATION_CODE:
        flash('Ongeldige registratiecode.', 'error')
        return redirect(url_for('main.register'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email bestaat al.', 'error')
            return redirect(url_for('main.register_admin', code=code))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            user_type='admin',
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Admin registratie succesvol!', 'success')
        return redirect(url_for('main.index'))

    return render_template('register_admin.html', code=code)


@routes.route('/admin/verify_mosque/<int:mosque_id>', methods=['POST'])
@login_required
def verify_mosque(mosque_id):
    if not current_user.is_admin:
        flash('Geen toegang.', 'error')
        return redirect(url_for('main.index'))

    mosque = User.query.get_or_404(mosque_id)
    action = request.form.get('action')
    note = request.form.get('note')

    if action == 'approve':
        mosque.is_verified = True
        mosque.verification_status = 'approved'
        flash('Moskee geverifieerd.', 'success')
    elif action == 'reject':
        mosque.is_verified = False
        mosque.verification_status = 'rejected'
        flash('Moskee verificatie geweigerd.', 'warning')

    mosque.verification_note = note
    db.session.commit()

    return redirect(url_for('admin.mosque_verification_list'))


@routes.route('/mosque/<int:mosque_id>/donations', methods=['GET', 'POST'])
@login_required
def mosque_donations(mosque_id):
    mosque = User.query.get_or_404(mosque_id)

    # Check if user has permission to manage donations
    if not (current_user.is_admin or current_user.id == mosque.id):
        flash('Geen toegang tot donatie instellingen.', 'error')
        return redirect(url_for('main.mosque_detail', mosque_id=mosque_id))

    if request.method == 'POST':
        mosque.donation_enabled = bool(request.form.get('donation_enabled'))
        mosque.donation_iban = request.form.get('donation_iban')
        mosque.donation_description = request.form.get('donation_description')
        mosque.donation_goal = float(request.form.get('donation_goal')) if request.form.get('donation_goal') else None
        mosque.donation_goal_description = request.form.get('donation_goal_description')

        db.session.commit()
        flash('Donatie instellingen bijgewerkt.', 'success')
        return redirect(url_for('main.mosque_detail', mosque_id=mosque_id))

    return render_template('mosque_donations.html', mosque=mosque)

@routes.route('/donate/vgm', methods=['GET', 'POST'])
def donate_vgm():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        donor_name = request.form.get('donor_name')
        donor_email = request.form.get('donor_email')
        message = request.form.get('message')
        is_anonymous = bool(request.form.get('is_anonymous'))

        donation = Donation(
            amount=amount,
            donor_name=donor_name if not is_anonymous else None,
            donor_email=donor_email,
            message=message,
            is_anonymous=is_anonymous
        )
        db.session.add(donation)
        db.session.commit()

        # Here you would typically integrate with a payment provider
        flash('Bedankt voor uw steun aan VGM!', 'success')
        return redirect(url_for('main.index'))

    return render_template('donate_vgm.html')

@routes.route('/mosque/<int:mosque_id>/donate', methods=['GET', 'POST'])
def donate_mosque(mosque_id):
    mosque = User.query.get_or_404(mosque_id)

    if not mosque.donation_enabled:
        flash('Donaties zijn momenteel niet mogelijk voor deze moskee.', 'info')
        return redirect(url_for('main.mosque_detail', mosque_id=mosque_id))

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        donor_name = request.form.get('donor_name')
        donor_email = request.form.get('donor_email')
        message = request.form.get('message')
        is_anonymous = bool(request.form.get('is_anonymous'))

        donation = Donation(
            amount=amount,
            donor_name=donor_name if not is_anonymous else None,
            donor_email=donor_email,
            message=message,
            is_anonymous=is_anonymous,
            mosque_id=mosque_id
        )
        db.session.add(donation)
        db.session.commit()

        # Here you would typically integrate with a payment provider
        flash(f'Bedankt voor uw steun aan {mosque.mosque_name}!', 'success')
        return redirect(url_for('main.mosque_detail', mosque_id=mosque_id))

    return render_template('donate_mosque.html', mosque=mosque)

# Add profile route after existing routes
@routes.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'follow_mosque':
            mosque_id = request.form.get('mosque_id')
            if mosque_id:
                # Check if already following
                existing = MosqueNotificationPreference.query.filter_by(
                    user_id=current_user.id,
                    mosque_id=mosque_id
                ).first()

                if not existing:
                    pref = MosqueNotificationPreference(
                        user_id=current_user.id,
                        mosque_id=mosque_id
                    )
                    db.session.add(pref)
                    flash('Je volgt nu deze moskee.', 'success')
                else:
                    flash('Je volgt deze moskee al.', 'info')

        elif action == 'update_profile':
            # Update notification preferences
            current_user.notify_new_events = bool(request.form.get('notify_events'))
            current_user.notify_obituaries = bool(request.form.get('notify_obituaries'))

            # Update profile info
            current_user.username = request.form.get('username')
            current_user.email = request.form.get('email')

            new_password = request.form.get('new_password')
            if new_password:
                current_user.password_hash = generate_password_hash(new_password)

            flash('Profiel succesvol bijgewerkt.', 'success')

        elif 'unfollow_mosque' in request.form:
            mosque_id = request.form.get('unfollow_mosque')
            pref = MosqueNotificationPreference.query.filter_by(
                user_id=current_user.id,
                mosque_id=mosque_id
            ).first()

            if pref:
                db.session.delete(pref)
                flash('Je volgt deze moskee niet meer.', 'success')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Er is een fout opgetreden bij het bijwerken van je profiel.', 'error')
            print(f"Error updating profile: {e}")

    # Get all verified mosques for the dropdown
    mosques = User.query.filter_by(user_type='mosque', is_verified=True).all()
    return render_template('profile.html', mosques=mosques)

@routes.route('/test_canva')
@login_required
def test_canva():
    try:
        # Get brand resources
        brand_resources = canva_client.get_brand_resources()

        # Get recent designs
        designs = canva_client.get_designs(limit=5)

        return render_template(
            'admin/canva_test.html',
            brand_resources=brand_resources,
            designs=designs
        )
    except Exception as e:
        flash(f'Error accessing Canva API: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@routes.route('/ramadan')
def ramadan():
    # Get today's prayer times
    today = date.today()
    prayer_times = PrayerTime.query.filter_by(date=today).all()

    # Get upcoming Ramadan programs
    programs = RamadanProgram.query.filter(
        RamadanProgram.start_date >= datetime.now()
    ).order_by(RamadanProgram.start_date).limit(3).all()

    return render_template('ramadan/index.html',
                         prayer_times=prayer_times,
                         programs=programs)

@routes.route('/ramadan/iftar/add', methods=['GET', 'POST'])
@login_required
def add_iftar():
    if not (current_user.is_admin or current_user.user_type == 'mosque'):
        flash('Alleen moskeeën en beheerders kunnen iftar evenementen toevoegen.', 'error')
        return redirect(url_for('main.ramadan'))

    # Get list of mosques for admin selection
    mosques = None
    if current_user.is_admin:
        mosques = User.query.filter_by(user_type='mosque', is_verified=True).order_by(User.mosque_name).all()

    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            is_recurring = 'is_recurring' in request.form

            # Determine mosque_id based on user type
            mosque_id = current_user.id if current_user.user_type == 'mosque' else request.form.get('mosque_id')

            # Base iftar event data
            iftar_data = {
                'mosque_id': mosque_id,
                'start_time': datetime.strptime(request.form['start_time'], '%H:%M').time(),
                'end_time': datetime.strptime(request.form['end_time'], '%H:%M').time() if request.form.get('end_time') else None,
                'location': request.form['location'],
                'capacity': int(request.form['capacity']) if request.form.get('capacity') else None,
                'is_family_friendly': 'is_family_friendly' in request.form,
                'registration_required': 'registration_required' in request.form,
                'registration_deadline': datetime.strptime(request.form['registration_deadline'], '%Y-%m-%dT%H:%M') if request.form.get('registration_deadline') else None,
                'dietary_options': 'dietary_options' in request.form,
                'notes': request.form.get('notes'),
                'is_recurring': is_recurring
            }

            if is_recurring:
                recurrence_type = request.form['recurrence_type']
                end_date = datetime.strptime(request.form['recurrence_end_date'], '%Y-%m-%d').date()
                iftar_data['recurrence_type'] = recurrence_type
                iftar_data['recurrence_end_date'] = end_date

                current_date = start_date
                while current_date <= end_date:
                    # Create an iftar event for this date
                    iftar = IfterEvent(
                        **iftar_data,
                        date=current_date
                    )
                    db.session.add(iftar)

                    # Calculate next date based on recurrence type
                    if recurrence_type == 'daily':
                        current_date += timedelta(days=1)
                    elif recurrence_type == 'weekly':
                        current_date += timedelta(weeks=1)
            else:
                # Create a single iftar event
                iftar = IfterEvent(
                    **iftar_data,
                    date=start_date
                )
                db.session.add(iftar)

            db.session.commit()
            flash('Iftar evenement(en) succesvol toegevoegd.', 'success')
            return redirect(url_for('main.ramadan'))

        except Exception as e:
            db.session.rollback()
            flash('Er is een fout opgetreden bij het toevoegen van het iftar evenement.', 'error')
            print(f"Error adding iftar event: {e}")
            return redirect(url_for('main.add_iftar'))

    return render_template('ramadan/add_iftar.html', mosques=mosques)

@routes.route('/ramadan/iftar/<int:iftar_id>/register', methods=['POST'])
@login_required
def register_iftar(iftar_id):
    try:
        iftar = IfterEvent.query.get_or_404(iftar_id)
        if iftar.capacity and iftar.registrations.count() >= iftar.capacity:
            flash('Dit iftar evenement is helaas vol.', 'error')
            return redirect(url_for('main.ramadan'))

        registration = IfterRegistration(
            ifter_event_id=iftar_id,
            user_id=current_user.id,
            number_of_people=int(request.form.get('number_of_people', 1)),
            dietary_requirements=request.form.get('dietary_requirements')
        )
        db.session.add(registration)
        db.session.commit()
        flash('Je bent succesvol geregistreerd voor dit iftar evenement.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Er is een fout opgetreden bij het registreren.', 'error')
        print(f"Error registering for iftar: {e}")

    return redirect(url_for('main.ramadan'))

@routes.route('/ramadan/quran-resources')
def quran_resources():
    resources = RamadanQuranResource.query.order_by(RamadanQuranResource.created_at.desc()).all()
    return render_template('ramadan/quran_resources.html', resources=resources)

@routes.route('/ramadan/quran-resources/add', methods=['GET', 'POST'])
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
            flash('Quran bron succesvol toegevoegd.', 'success')
            return redirect(url_for('main.quran_resources'))
        except Exception as e:
            db.session.rollback()
            flash('Er is een fout opgetreden bij het toevoegen van de Quran bron.', 'error')
            print(f"Error adding Quran resource: {e}")

    return render_template('ramadan/add_quran_resource.html')

@routes.route('/ramadan/videos')
def ramadan_videos():
    videos = RamadanVideo.query.order_by(RamadanVideo.created_at.desc()).all()
    return render_template('ramadan/videos.html', videos=videos)

@routes.route('/ramadan/videos/add', methods=['GET', 'POST'])
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
            flash('Video succesvol toegevoegd.', 'success')
            return redirect(url_for('main.ramadan_videos'))
        except Exception as e:
            db.session.rollback()
            flash('Er is een fout opgetreden bij het toevoegen van de video.', 'error')
            print(f"Error adding video: {e}")

    return render_template('ramadan/add_video.html')

@routes.route('/ramadan/schedule')
def ramadan_schedule():
    programs = RamadanProgram.query.order_by(RamadanProgram.start_date).all()
    return render_template('ramadan/schedule.html', programs=programs)

@routes.route('/ramadan/schedule/add', methods=['GET', 'POST'])
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
            flash('Programma succesvol toegevoegd.', 'success')
            return redirect(url_for('main.ramadan_schedule'))
        except Exception as e:
            db.session.rollback()
            flash('Er is een fout opgetreden bij het toevoegen van het programma.', 'error')
            print(f"Error adding program: {e}")

    return render_template('ramadan/add_program.html')

@routes.route('/ramadan/iftar-map')
def iftar_map():
    # Get query parameters
    date_str = request.args.get('date')
    family_only = request.args.get('filter') == 'family'

    # Parse date or use today
    try:
        current_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    except ValueError:
        current_date = date.today()

    # Calculate previous and next dates
    prev_date = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')

    # Build query for iftar events
    query = IfterEvent.query.filter(
        IfterEvent.date == current_date
    )

    if family_only:
        query = query.filter(IfterEvent.is_family_friendly == True)

    iftar_events = query.order_by(IfterEvent.start_time).all()

    # Calculate map center (average of all mosque coordinates)
    if iftar_events:
        lats = [event.mosque.latitude for event in iftar_events]
        lngs = [event.mosque.longitude for event in iftar_events]
        center_lat = sum(lats) / len(lats)
        center_lng = sum(lngs) / len(lngs)
    else:
        # Default to Gent center if no events
        center_lat = 51.0543
        center_lng = 3.7174

    return render_template('ramadan/iftar_map.html',
                         iftar_events=iftar_events,
                         current_date=current_date,
                         prev_date=prev_date,
                         next_date=next_date,
                         family_only=family_only,
                         center_lat=center_lat,
                         center_lng=center_lng,
                         google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY'))