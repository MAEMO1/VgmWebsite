from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from models import Obituary, ObituaryNotification, User
from forms import ObituaryForm

obituaries = Blueprint('obituaries', __name__)

@obituaries.route('/')
def index():
    obituaries = Obituary.query.filter_by(is_approved=True).order_by(Obituary.date_of_death.desc()).all()
    return render_template('obituaries/index.html', obituaries=obituaries)

@obituaries.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    # Get all mosques for the form dropdown
    mosques = User.query.filter_by(user_type='mosque', is_verified=True).all()
    form = ObituaryForm()
    form.mosque_id.choices = [(mosque.id, mosque.username) for mosque in mosques]

    if form.validate_on_submit():
        try:
            obituary = Obituary(
                name=form.name.data,
                age=form.age.data,
                birth_place=form.birth_place.data,
                death_place=form.death_place.data,
                date_of_death=form.date_of_death.data,
                prayer_time=form.prayer_time.data,
                death_prayer_location=form.death_prayer_location.data,
                burial_location=form.burial_location.data,
                family_contact=form.family_contact.data,
                additional_notes=form.additional_notes.data,
                mosque_id=form.mosque_id.data,
                submitter_id=current_user.id,
                is_approved=current_user.is_admin or (current_user.user_type == 'mosque' and current_user.id == form.mosque_id.data)
            )

            db.session.add(obituary)
            db.session.commit()

            # Send notification to the selected mosque for verification if needed
            if not obituary.is_approved:
                notification = ObituaryNotification(
                    obituary_id=obituary.id,
                    user_id=obituary.mosque_id,
                    notification_type='verification_needed',
                    message=f'Nieuw overlijdensbericht ter verificatie: {obituary.name}'
                )
                db.session.add(notification)
                db.session.commit()

                flash('Overlijdensbericht is ingediend en wacht op verificatie door de moskee.', 'info')
            else:
                flash('Overlijdensbericht is succesvol toegevoegd.', 'success')

            return redirect(url_for('obituaries.index'))
        except Exception as e:
            db.session.rollback()
            flash('Er is een fout opgetreden bij het toevoegen van het overlijdensbericht. Probeer het opnieuw.', 'error')
            print(f"Error: {str(e)}")  # For debugging

    return render_template('obituaries/create.html', form=form)

@obituaries.route('/<int:obituary_id>/verify', methods=['POST'])
@login_required
def verify_obituary(obituary_id):
    if not (current_user.is_admin or current_user.user_type == 'mosque'):
        flash('U heeft geen toestemming om overlijdensberichten te verifiëren.', 'error')
        return redirect(url_for('obituaries.index'))

    obituary = Obituary.query.get_or_404(obituary_id)

    # Check if user has permission to verify this obituary
    if not (current_user.is_admin or current_user.id == obituary.mosque_id):
        flash('U heeft geen toestemming om dit overlijdensbericht te verifiëren.', 'error')
        return redirect(url_for('obituaries.index'))

    try:
        obituary.is_approved = True
        db.session.commit()

        # Send notification to the submitter
        notification = ObituaryNotification(
            obituary_id=obituary.id,
            user_id=obituary.submitter_id,  # Send to the person who submitted the obituary
            notification_type='verified',
            message=f'Uw overlijdensbericht voor {obituary.name} is geverifieerd.'
        )
        db.session.add(notification)
        db.session.commit()

        flash('Overlijdensbericht is geverifieerd.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Er is een fout opgetreden bij het verifiëren van het overlijdensbericht.', 'error')

    return redirect(url_for('obituaries.index'))

@obituaries.route('/pending')
@login_required
def pending_obituaries():
    if not (current_user.is_admin or current_user.user_type == 'mosque'):
        flash('U heeft geen toegang tot deze pagina.', 'error')
        return redirect(url_for('obituaries.index'))

    # If mosque user, show only their pending obituaries
    if current_user.user_type == 'mosque':
        pending = Obituary.query.filter_by(
            is_approved=False,
            mosque_id=current_user.id
        ).order_by(Obituary.date_of_death.desc()).all()
    else:  # Admin sees all pending obituaries
        pending = Obituary.query.filter_by(
            is_approved=False
        ).order_by(Obituary.date_of_death.desc()).all()

    return render_template('obituaries/pending.html', obituaries=pending)

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
    flash('Voorkeuren voor notificaties zijn bijgewerkt.', 'success')
    return redirect(url_for('obituaries.index'))