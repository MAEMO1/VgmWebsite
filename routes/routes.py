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
        phone = request.form.get('phone')

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
            mosque_phone=phone,
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

@routes.route('/memorandum')
def memorandum():
    """Temporarily disabled memorandum page"""
    flash(_('Deze pagina is momenteel niet beschikbaar.'), 'info')
    return redirect(url_for('main.index'))

@routes.route('/about')
def about():
    """Temporarily disabled about page"""
    flash(_('Deze pagina is momenteel niet beschikbaar.'), 'info')
    return redirect(url_for('main.index'))

@routes.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        flash(_('Thank you for your message. We will get back to you soon.'), 'success')
        return redirect(url_for('main.contact'))

    return render_template('contact.html')