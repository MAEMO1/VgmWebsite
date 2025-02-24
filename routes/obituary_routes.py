from flask import Blueprint, render_template, request, redirect, url_for, flash
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

    # Format mosque names and add "Andere" option
    mosque_choices = [(str(mosque.id), mosque.username.replace('_', ' ').title()) for mosque in mosques]
    mosque_choices.append(('andere', 'Andere'))
    form.death_prayer_location.choices = mosque_choices

    # Set choices for after prayer selection
    form.after_prayer.choices = [
        ('fajr', 'Na Fajr (Ochtendgebed)'),
        ('dhuhr', 'Na Dhuhr (Middaggebed)'),
        ('asr', 'Na Asr (Namiddaggebed)'),
        ('maghrib', 'Na Maghrib (Zonsonderganggebed)'),
        ('isha', 'Na Isha (Avondgebed)'),
        ('jumuah', 'Na Jumuah (Vrijdaggebed)')
    ]

    # Set choices for time type
    form.time_type.choices = [
        ('specific', 'Specifiek Tijdstip'),
        ('after_prayer', 'Na een Gebed')
    ]

    if form.validate_on_submit():
        try:
            # Create the obituary
            obituary = Obituary(
                name=form.name.data,
                age=form.age.data,
                birth_place=form.birth_place.data,
                death_place=form.death_place.data,
                date_of_death=form.date_of_death.data,
                prayer_time=form.prayer_time.data if form.time_type.data == 'specific' else None,
                prayer_after=form.after_prayer.data if form.time_type.data == 'after_prayer' else None,
                burial_location=form.burial_location.data,
                family_contact=form.family_contact.data,
                additional_notes=form.additional_notes.data,
                submitter_id=current_user.id,
                is_approved=False  # Always require verification
            )

            # Handle location
            if form.death_prayer_location.data == 'andere':
                obituary.death_prayer_location = form.other_location_address.data
                obituary.mosque_id = None  # No mosque associated
            else:
                mosque_id = int(form.death_prayer_location.data)
                obituary.mosque_id = mosque_id
                obituary.death_prayer_location = User.query.get(mosque_id).username.replace('_', ' ').title()

            db.session.add(obituary)
            db.session.commit()

            # Send notifications
            # To mosques
            if obituary.mosque_id:
                notification = ObituaryNotification(
                    obituary_id=obituary.id,
                    user_id=obituary.mosque_id,
                    notification_type='verification_needed',
                    message=f'Nieuw overlijdensbericht ter verificatie: {obituary.name}'
                )
                db.session.add(notification)

            # To admins
            admins = User.query.filter_by(is_admin=True).all()
            for admin in admins:
                notification = ObituaryNotification(
                    obituary_id=obituary.id,
                    user_id=admin.id,
                    notification_type='verification_needed',
                    message=f'Nieuw overlijdensbericht ter verificatie: {obituary.name}'
                )
                db.session.add(notification)

            db.session.commit()
            flash('Overlijdensbericht is ingediend en wacht op verificatie.', 'info')
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

    # Get modification data
    new_mosque_id = request.form.get('new_mosque_id')
    if new_mosque_id and current_user.is_admin:
        # Handle mosque change
        old_mosque_id = obituary.mosque_id
        obituary.mosque_id = int(new_mosque_id)

        # Notify new mosque
        notification = ObituaryNotification(
            obituary_id=obituary.id,
            user_id=new_mosque_id,
            notification_type='mosque_changed',
            message=f'U bent aangeduid voor het dodengebed van {obituary.name}'
        )
        db.session.add(notification)

        # Notify original mosque if exists
        if old_mosque_id:
            notification = ObituaryNotification(
                obituary_id=obituary.id,
                user_id=old_mosque_id,
                notification_type='mosque_changed',
                message=f'Een andere moskee is aangeduid voor het dodengebed van {obituary.name}'
            )
            db.session.add(notification)

        # Notify submitter
        notification = ObituaryNotification(
            obituary_id=obituary.id,
            user_id=obituary.submitter_id,
            notification_type='mosque_changed',
            message=f'De moskee voor het dodengebed is gewijzigd'
        )
        db.session.add(notification)

    try:
        obituary.is_approved = True
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

    # Get all mosques for the modification form
    mosques = User.query.filter_by(user_type='mosque', is_verified=True).all()
    return render_template('obituaries/pending.html', obituaries=pending, mosques=mosques)

@obituaries.route('/<int:obituary_id>/subscribe', methods=['POST'])
@login_required
def subscribe_notifications(obituary_id):
    try:
        notification = ObituaryNotification(
            obituary_id=obituary_id,
            user_id=current_user.id,
            notification_type='subscription',
            message='Geabonneerd op updates voor dit overlijdensbericht'
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

@obituaries.route('/<int:obituary_id>/delete', methods=['POST'])
@login_required
def delete_obituary(obituary_id):
    if not current_user.is_admin:
        flash('U heeft geen toestemming om overlijdensberichten te verwijderen.', 'error')
        return redirect(url_for('obituaries.index'))

    obituary = Obituary.query.get_or_404(obituary_id)

    try:
        # Notify related parties about deletion
        if obituary.mosque_id:
            notification = ObituaryNotification(
                user_id=obituary.mosque_id,
                notification_type='deletion',
                message=f'Overlijdensbericht voor {obituary.name} is verwijderd door een administrator'
            )
            db.session.add(notification)

        # Notify submitter
        if obituary.submitter_id:
            notification = ObituaryNotification(
                user_id=obituary.submitter_id,
                notification_type='deletion',
                message=f'Uw overlijdensbericht voor {obituary.name} is verwijderd door een administrator'
            )
            db.session.add(notification)

        # Delete the obituary
        db.session.delete(obituary)
        db.session.commit()
        flash('Overlijdensbericht is succesvol verwijderd.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Er is een fout opgetreden bij het verwijderen van het overlijdensbericht.', 'error')
        print(f"Error: {str(e)}")

    return redirect(url_for('obituaries.index'))