from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from models import Obituary, ObituaryNotification, User

obituaries = Blueprint('obituaries', __name__, url_prefix='/obituaries')

@obituaries.route('/')
def obituary_list():
    obituaries = Obituary.query.filter_by(is_approved=True).order_by(Obituary.date_of_death.desc()).all()
    return render_template('obituaries.html', obituaries=obituaries)

@obituaries.route('/submit', methods=['POST'])
@login_required
def submit_obituary():
    if current_user.user_type != 'mosque':
        flash('Only mosque administrators can submit obituaries.', 'error')
        return redirect(url_for('obituaries.obituary_list'))

    try:
        obituary = Obituary(
            name=request.form['name'],
            age=int(request.form['age']) if request.form['age'] else None,
            birth_place=request.form['birth_place'],
            death_place=request.form['death_place'],
            date_of_death=datetime.strptime(request.form['date_of_death'], '%Y-%m-%d'),
            funeral_date=datetime.strptime(request.form['funeral_date'], '%Y-%m-%dT%H:%M') if request.form['funeral_date'] else None,
            prayer_time=datetime.strptime(request.form['prayer_time'], '%Y-%m-%dT%H:%M') if request.form['prayer_time'] else None,
            death_prayer_location=request.form['death_prayer_location'],
            burial_location=request.form['burial_location'],
            family_contact=request.form['family_contact'],
            details=request.form['details'],
            additional_notes=request.form['additional_notes'],
            mosque_id=current_user.id,
            is_approved=True  # Auto-approve if submitted by mosque
        )
        db.session.add(obituary)
        db.session.commit()

        # Send notifications to subscribed users
        users = User.query.filter_by(notify_obituaries=True).all()
        for user in users:
            notification = ObituaryNotification(
                obituary_id=obituary.id,
                user_id=user.id,
                notification_type='new',
                message=f'New obituary posted: {obituary.name}'
            )
            db.session.add(notification)
        db.session.commit()

        flash('Obituary submitted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error submitting obituary. Please try again.', 'error')

    return redirect(url_for('obituaries.obituary_list'))

@obituaries.route('/<int:obituary_id>/subscribe', methods=['POST'])
@login_required
def subscribe_notifications(obituary_id):
    try:
        notification = ObituaryNotification(
            obituary_id=obituary_id,
            user_id=current_user.id,
            notification_type='subscription',
            message='Subscribed to obituary updates'
        )
        db.session.add(notification)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@obituaries.route('/preferences', methods=['POST'])
@login_required
def update_preferences():
    current_user.notify_obituaries = bool(request.form.get('notify_obituaries'))
    db.session.commit()
    flash('Notification preferences updated successfully.', 'success')
    return redirect(url_for('obituaries.obituary_list'))