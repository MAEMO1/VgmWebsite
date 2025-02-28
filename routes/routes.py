import calendar
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_babel import _
from models import User
from extensions import db

routes = Blueprint('main', __name__)

def allowed_file(filename, allowed_extensions={'png', 'jpg', 'jpeg'}):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(_('Succesvol ingelogd!'), 'success')
            return redirect(url_for('main.index'))

        flash(_('Ongeldige email of wachtwoord.'), 'error')
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
            flash(_('Email bestaat al.'), 'error')
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
        flash(_('Registratie succesvol!'), 'success')
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

        if User.query.filter_by(email=email).first():
            flash(_('Email bestaat al.'), 'error')
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
            is_verified=False
        )
        db.session.add(mosque)
        db.session.commit()

        login_user(mosque)
        flash(_('Moskee registratie succesvol! Wacht op verificatie door een beheerder.'), 'success')
        return redirect(url_for('main.index'))

    return render_template('register_mosque.html')

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('U bent uitgelogd.'), 'info')
    return redirect(url_for('main.index'))

@routes.route('/')
def index():
    return render_template('index.html')

@routes.route('/mosques')
def mosques():
    mosque_users = User.query.filter_by(user_type='mosque', is_verified=True).all()
    return render_template('mosques.html', mosques=mosque_users)

@routes.route('/about')
def about():
    return render_template('about.html')

@routes.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        flash(_('Bedankt voor uw bericht. We nemen zo spoedig mogelijk contact met u op.'), 'success')
        return redirect(url_for('main.contact'))

    return render_template('contact.html')

@routes.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash(_('U heeft geen toegang tot deze pagina.'), 'error')
        return redirect(url_for('main.index'))
    return render_template('admin/index.html')

@routes.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@routes.route('/set_language/<language>')
def set_language(language):
    from flask import session
    session['language'] = language
    return redirect(request.referrer or url_for('main.index'))

@routes.route('/mosque/<int:mosque_id>')
def mosque_detail(mosque_id):
    mosque = User.query.filter_by(id=mosque_id, user_type='mosque', is_verified=True).first_or_404()
    return render_template('mosque_detail.html', mosque=mosque)

@routes.route('/mosque/<int:mosque_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_mosque(mosque_id):
    mosque = User.query.filter_by(id=mosque_id, user_type='mosque').first_or_404()

    # Check if user has permission to edit
    if not current_user.is_admin and current_user.id != mosque_id:
        flash(_('U heeft geen toegang tot deze pagina.'), 'error')
        return redirect(url_for('main.mosque_detail', mosque_id=mosque_id))

    if request.method == 'POST':
        # Update basic information
        mosque.mosque_name = request.form.get('mosque_name')
        mosque.mosque_street = request.form.get('street')
        mosque.mosque_number = request.form.get('number')
        mosque.mosque_postal = request.form.get('postal')
        mosque.mosque_city = request.form.get('city')
        mosque.mosque_phone = request.form.get('phone')
        mosque.mosque_email = request.form.get('email')
        mosque.mosque_website = request.form.get('website')

        # Optional fields
        mosque.mission_statement = request.form.get('mission_statement')
        mosque.vision_statement = request.form.get('vision_statement')
        mosque.activities = request.form.get('activities')
        mosque.facilities = request.form.get('facilities')
        mosque.languages = request.form.get('languages')
        mosque.accessibility_features = request.form.get('accessibility_features')

        try:
            db.session.commit()
            flash(_('Moskee informatie succesvol bijgewerkt.'), 'success')
            return redirect(url_for('main.mosque_detail', mosque_id=mosque_id))
        except Exception as e:
            db.session.rollback()
            flash(_('Er is een fout opgetreden bij het bijwerken van de moskee informatie.'), 'error')

    return render_template('edit_mosque.html', mosque=mosque)