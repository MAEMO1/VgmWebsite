from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import Event, Obituary, PrayerTime, User
from datetime import datetime

@app.route('/')
def index():
    events = Event.query.order_by(Event.date).limit(3).all()
    prayer_times = PrayerTime.query.filter_by(date=datetime.today().date()).all()
    return render_template('index.html', events=events, prayer_times=prayer_times)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('index'))

@app.route('/prayer-times')
def prayer_times():
    times = PrayerTime.query.filter_by(date=datetime.today().date()).all()
    return render_template('prayer_times.html', times=times)

@app.route('/events')
def events():
    events = Event.query.order_by(Event.date).all()
    return render_template('events.html', events=events)

@app.route('/obituaries')
def obituaries():
    obituaries = Obituary.query.filter_by(is_approved=True).order_by(Obituary.created_at.desc()).all()
    return render_template('obituaries.html', obituaries=obituaries)

@app.route('/obituaries/submit', methods=['GET', 'POST'])
def submit_obituary():
    if request.method == 'POST':
        obituary = Obituary(
            name=request.form['name'],
            date_of_death=datetime.strptime(request.form['date_of_death'], '%Y-%m-%d'),
            funeral_date=datetime.strptime(request.form['funeral_date'], '%Y-%m-%d %H:%M'),
            details=request.form['details']
        )
        db.session.add(obituary)
        db.session.commit()
        flash('Obituary submitted for approval', 'success')
        return redirect(url_for('obituaries'))
    return render_template('obituaries.html', form=True)

@app.route('/admin/obituaries')
@login_required
def admin_obituaries():
    if not current_user.is_admin:
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    pending = Obituary.query.filter_by(is_approved=False).all()
    return render_template('admin/obituary_approval.html', obituaries=pending)

@app.route('/contact')
def contact():
    return render_template('contact.html')