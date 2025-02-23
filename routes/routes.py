from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app import db
from models import User, BoardMember # Added BoardMember import
from datetime import datetime, date
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

@routes.route('/mosque/<int:mosque_id>')
def mosque_detail(mosque_id):
    mosque = User.query.filter_by(id=mosque_id, user_type='mosque', is_verified=True).first_or_404()

    # Get today's prayer times
    today = datetime.today().date()
    prayer_times = mosque.prayer_times.filter_by(date=today).all()

    # Get upcoming events
    events = mosque.events.filter(Event.date >= datetime.utcnow()).order_by(Event.date).limit(5).all()

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
        flash('Je hebt geen toestemming om deze moskee te bewerken.', 'error')
        return redirect(url_for('main.mosque_detail', mosque_id=mosque_id))

    if request.method == 'POST':
        try:
            # Update basic information
            mosque.history = request.form.get('history')
            mosque.establishment_year = int(request.form.get('establishment_year')) if request.form.get('establishment_year') else None

            # Update contact information
            mosque.mosque_email = request.form.get('mosque_email')
            mosque.mosque_website = request.form.get('mosque_website')
            mosque.mosque_phone = request.form.get('mosque_phone')
            mosque.mosque_fax = request.form.get('mosque_fax')
            mosque.emergency_contact = request.form.get('emergency_contact')
            mosque.emergency_phone = request.form.get('emergency_phone')

            # Update social media links
            mosque.facebook_url = request.form.get('facebook_url')
            mosque.twitter_url = request.form.get('twitter_url')
            mosque.instagram_url = request.form.get('instagram_url')
            mosque.youtube_url = request.form.get('youtube_url')
            mosque.whatsapp_number = request.form.get('whatsapp_number')

            # Parse and set Friday prayer time
            friday_time = request.form.get('friday_prayer_time')
            if friday_time:
                mosque.friday_prayer_time = datetime.strptime(friday_time, '%H:%M').time()

            # Handle image uploads
            if 'images' in request.files:
                for image in request.files.getlist('images'):
                    if image and allowed_file(image.filename):
                        filename = secure_filename(image.filename)
                        image_path = os.path.join('static', 'uploads', filename)
                        image.save(image_path)

                        mosque_image = MosqueImage(
                            mosque_id=mosque.id,
                            url=url_for('static', filename=f'uploads/{filename}'),
                            description=request.form.get('image_description')
                        )
                        db.session.add(mosque_image)

            # Handle video URLs
            video_urls = request.form.getlist('video_urls[]')
            video_titles = request.form.getlist('video_titles[]')
            for url, title in zip(video_urls, video_titles):
                if url and title:
                    mosque_video = MosqueVideo(
                        mosque_id=mosque.id,
                        url=url,
                        title=title
                    )
                    db.session.add(mosque_video)

            db.session.commit()
            flash('Moskee informatie succesvol bijgewerkt.', 'success')
            return redirect(url_for('main.mosque_detail', mosque_id=mosque_id))

        except Exception as e:
            db.session.rollback()
            flash('Er is een fout opgetreden bij het bijwerken van de moskee informatie.', 'error')
            print(f"Error updating mosque: {e}")

    return render_template('edit_mosque.html', mosque=mosque)

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
    # Initialize default board members if none exist
    if BoardMember.query.count() == 0:
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

        # First clear any existing board members
        BoardMember.query.delete()

        # Create board images directory if it doesn't exist
        board_dir = os.path.join('static', 'images', 'board')
        os.makedirs(board_dir, exist_ok=True)

        for member_data in default_board_members:
            # Find the associated mosque using exact name match
            mosque = User.query.filter_by(
                user_type='mosque',
                mosque_name=member_data['mosque_name']
            ).first()

            if mosque:
                board_member = BoardMember(
                    name=member_data['name'],
                    role=member_data['role'],
                    mosque_id=mosque.id,
                    term_start=term_start,
                    term_end=term_end,
                    image=f"member_{member_data['name'].lower().replace(' ', '_')}.jpg"
                )
                db.session.add(board_member)
                print(f"Added board member {member_data['name']} for mosque {mosque.mosque_name}")
            else:
                print(f"Warning: Mosque not found for board member {member_data['name']}")

        try:
            db.session.commit()
            print("Successfully initialized all board members")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing board members: {e}")

    # Get all available terms
    terms = db.session.query(
        BoardMember.term_start,
        BoardMember.term_end
    ).distinct().group_by(BoardMember.term_start, BoardMember.term_end).all()

    # Get the requested term or default to current term
    term_start_str = request.args.get('term')
    if term_start_str:
        term_start = datetime.strptime(term_start_str, '%Y-%m-%d').date()
    else:
        # Default to current or most recent term
        current_date = date.today()
        latest_term = BoardMember.query.filter(
            BoardMember.term_end >= current_date
        ).order_by(BoardMember.term_start.desc()).first()

        if latest_term:
            term_start = latest_term.term_start
        else:
            term_start = date(current_date.year, 1, 1)

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

        # Remove existing board members for this term
        BoardMember.query.filter_by(term_start=term_start).delete()

        names = request.form.getlist('names[]')
        roles = request.form.getlist('roles[]')
        mosque_ids = request.form.getlist('mosque_ids[]')
        photos = request.files.getlist('photos[]')

        for i, (name, role, mosque_id) in enumerate(zip(names, roles, mosque_ids)):
            photo = photos[i] if i < len(photos) else None

            # Handle photo upload
            image_filename = None
            if photo and photo.filename and allowed_file(photo.filename):
                # Create board images directory if it doesn't exist
                board_dir = os.path.join('static', 'images', 'board')
                os.makedirs(board_dir, exist_ok=True)

                # Generate unique filename
                image_filename = f"board_member_{term_start}_{i+1}.jpg"
                photo.save(os.path.join(board_dir, image_filename))

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