from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from models import User, Event, PrayerTime, Obituary
from datetime import datetime
from flask_babel import _
from . import routes

@routes.route('/')
def index():
    try:
        events = Event.query.filter(
            Event.date >= datetime.utcnow()
        ).order_by(Event.date).limit(3).all()

        today = datetime.today().date()
        prayer_times = PrayerTime.query.filter_by(date=today).all()

        return render_template('index.html', events=events, prayer_times=prayer_times)
    except Exception as e:
        return render_template('index.html', events=[], prayer_times=[])

@routes.route('/prayer-times')
def prayer_times():
    times = PrayerTime.query.filter_by(date=datetime.today().date()).all()
    return render_template('prayer_times.html', times=times)

@routes.route('/contact')
def contact():
    return render_template('contact.html')

@routes.route('/obituaries')
def obituaries():
    obituaries = Obituary.query.filter_by(is_approved=True).order_by(Obituary.date_of_death.desc()).all()
    return render_template('obituaries.html', obituaries=obituaries)

@routes.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('register.html')

@routes.route('/register/visitor', methods=['GET', 'POST'])
def register_visitor():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('main.register_visitor'))

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return redirect(url_for('main.register_visitor'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('main.register_visitor'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            user_type='visitor'
        )
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register_visitor.html')

@routes.route('/register/mosque', methods=['GET', 'POST'])
def register_mosque():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        mosque_name = request.form.get('mosque_name')
        mosque_address = request.form.get('mosque_address')
        mosque_phone = request.form.get('mosque_phone')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('main.register_mosque'))

        if User.query.filter_by(mosque_name=mosque_name).first():
            flash('A mosque with this name is already registered.', 'error')
            return redirect(url_for('main.register_mosque'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('main.register_mosque'))

        user = User(
            username=mosque_name,
            email=email,
            password_hash=generate_password_hash(password),
            user_type='mosque',
            mosque_name=mosque_name,
            mosque_address=mosque_address,
            mosque_phone=mosque_phone,
            is_verified=False
        )
        db.session.add(user)
        db.session.commit()

        flash('Registration submitted! Please wait for administrator verification.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register_mosque.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            if user.user_type == 'mosque' and not user.is_verified:
                flash('Your mosque account is pending verification.', 'warning')
                return redirect(url_for('main.login'))

            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('main.index'))

@routes.route('/language/<language>')
def set_language(language):
    if language not in ['en', 'nl', 'ar']:
        return redirect(url_for('main.index'))

    session['language'] = language
    return redirect(request.referrer or url_for('main.index'))