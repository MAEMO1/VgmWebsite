from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import or_, case, and_
from app import db
from models import Obituary, ObituaryNotification, User
from forms import ObituaryForm

obituaries = Blueprint('obituaries', __name__)

@obituaries.route('/')
def index():
    # Get current datetime
    now = datetime.now()

    # Get upcoming obituaries (future prayer times and dates)
    upcoming_obituaries = Obituary.query.filter(
        and_(
            Obituary.is_approved == True,
            or_(
                and_(Obituary.prayer_time.isnot(None), Obituary.prayer_time >= now),
                and_(Obituary.prayer_date.isnot(None), Obituary.prayer_date >= now.date())
            )
        )
    ).order_by(
        # Sort by prayer time first, then by prayer date
        Obituary.prayer_time.asc().nullslast(),
        Obituary.prayer_date.asc().nullslast()
    ).all()

    # Get recent obituaries (past 30 days, excluding those with future prayers)
    thirty_days_ago = now - timedelta(days=30)
    recent_obituaries = Obituary.query.filter(
        and_(
            Obituary.is_approved == True,
            Obituary.date_of_death >= thirty_days_ago,
            or_(
                and_(Obituary.prayer_time.isnot(None), Obituary.prayer_time < now),
                and_(Obituary.prayer_date.isnot(None), Obituary.prayer_date < now.date()),
                and_(Obituary.prayer_time.is_(None), Obituary.prayer_date.is_(None))
            )
        )
    ).order_by(
        Obituary.date_of_death.desc()
    ).all()

    return render_template('obituaries/index.html',
                         upcoming_obituaries=upcoming_obituaries,
                         recent_obituaries=recent_obituaries)

@obituaries.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    # Get all mosques for the form dropdown
    mosques = User.query.filter_by(user_type='mosque', is_verified=True).all()
    form = ObituaryForm()

    # Format mosque choices
    mosque_choices = [(str(mosque.id), mosque.username.replace('_', ' ').title()) for mosque in mosques]
    mosque_choices.append(('0', 'Andere locatie'))
    form.death_prayer_location.choices = mosque_choices

    if form.validate_on_submit():
        try:
            # Handle location first to determine death_prayer_location value
            death_prayer_location = None
            if form.death_prayer_location.data == '0':
                death_prayer_location = form.other_location_address.data
                mosque_id = None
                is_approved = True  # Auto-approve if no mosque involved
            else:
                mosque_id = int(form.death_prayer_location.data)
                mosque = User.query.get(mosque_id)
                death_prayer_location = mosque.username.replace('_', ' ').title()
                is_approved = current_user.is_admin  # Direct goedkeuring voor admins

            # Create the obituary
            obituary = Obituary(
                name=form.name.data,
                age=form.age.data,
                birth_place=form.birth_place.data,
                death_place=form.death_place.data,
                date_of_death=form.date_of_death.data,
                death_prayer_location=death_prayer_location,
                prayer_time=form.prayer_time.data if form.time_type.data == 'specific' else None,
                prayer_date=form.prayer_date.data if form.time_type.data == 'after_prayer' else None,
                prayer_after=form.after_prayer.data if form.time_type.data == 'after_prayer' else None,
                burial_location=form.burial_location.data,
                family_contact=form.family_contact.data,
                additional_notes=form.additional_notes.data,
                submitter_id=current_user.id,
                mosque_id=mosque_id,
                is_approved=is_approved
            )

            db.session.add(obituary)

            # Send notification to mosque if needed
            if mosque_id and not current_user.is_admin:
                notification = ObituaryNotification(
                    obituary_id=obituary.id,
                    user_id=mosque_id,
                    notification_type='verification_needed',
                    message=f'Nieuw overlijdensbericht ter verificatie: {obituary.name}'
                )
                db.session.add(notification)

            db.session.commit()

            if is_approved:
                flash('Overlijdensbericht is succesvol toegevoegd.', 'success')
            else:
                flash('Overlijdensbericht is ingediend en wacht op verificatie van de moskee.', 'info')

            return redirect(url_for('obituaries.index'))

        except Exception as e:
            db.session.rollback()
            flash('Er is een fout opgetreden bij het toevoegen van het overlijdensbericht. Probeer het opnieuw.', 'error')
            print(f"Error: {str(e)}")

    return render_template('obituaries/create.html', form=form)

@obituaries.route('/<int:obituary_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_obituary(obituary_id):
    obituary = Obituary.query.get_or_404(obituary_id)

    # Check if user has permission to edit
    if not (current_user.is_admin or current_user.id == obituary.mosque_id or current_user.id == obituary.submitter_id):
        flash('U heeft geen toestemming om dit overlijdensbericht te bewerken.', 'error')
        return redirect(url_for('obituaries.index'))

    mosques = User.query.filter_by(user_type='mosque', is_verified=True).all()
    form = ObituaryForm(obj=obituary)

    # Format mosque choices
    mosque_choices = [(str(mosque.id), mosque.username.replace('_', ' ').title()) for mosque in mosques]
    mosque_choices.append(('0', 'Andere locatie'))
    form.death_prayer_location.choices = mosque_choices

    if form.validate_on_submit():
        try:
            # Handle location changes
            if form.death_prayer_location.data == '0':
                obituary.death_prayer_location = form.other_location_address.data
                obituary.mosque_id = None
                obituary.is_approved = True
            else:
                new_mosque_id = int(form.death_prayer_location.data)
                mosque = User.query.get(new_mosque_id)
                obituary.death_prayer_location = mosque.username.replace('_', ' ').title()

                # Only update mosque_id and approval status if it changed
                if new_mosque_id != obituary.mosque_id:
                    obituary.mosque_id = new_mosque_id
                    if not current_user.is_admin:
                        obituary.is_approved = False
                        # Notify new mosque
                        notification = ObituaryNotification(
                            obituary_id=obituary.id,
                            user_id=new_mosque_id,
                            notification_type='verification_needed',
                            message=f'Overlijdensbericht ter verificatie: {obituary.name}'
                        )
                        db.session.add(notification)

            # Update other fields
            obituary.name = form.name.data
            obituary.age = form.age.data
            obituary.birth_place = form.birth_place.data
            obituary.death_place = form.death_place.data
            obituary.date_of_death = form.date_of_death.data
            obituary.prayer_time = form.prayer_time.data if form.time_type.data == 'specific' else None
            obituary.prayer_date = form.prayer_date.data if form.time_type.data == 'after_prayer' else None
            obituary.prayer_after = form.after_prayer.data if form.time_type.data == 'after_prayer' else None
            obituary.burial_location = form.burial_location.data
            obituary.family_contact = form.family_contact.data
            obituary.additional_notes = form.additional_notes.data

            db.session.commit()
            flash('Overlijdensbericht is succesvol bijgewerkt.', 'success')
            return redirect(url_for('obituaries.index'))

        except Exception as e:
            db.session.rollback()
            flash('Er is een fout opgetreden bij het bijwerken van het overlijdensbericht.', 'error')
            print(f"Error: {str(e)}")

    # Pre-fill the form
    if obituary.mosque_id:
        form.death_prayer_location.data = str(obituary.mosque_id)
    else:
        form.death_prayer_location.data = '0'
        form.other_location_address.data = obituary.death_prayer_location

    return render_template('obituaries/edit.html', form=form, obituary=obituary)

@obituaries.route('/<int:obituary_id>/verify', methods=['POST'])
@login_required
def verify_obituary(obituary_id):
    obituary = Obituary.query.get_or_404(obituary_id)

    # Check if user has permission to verify
    if not (current_user.is_admin or current_user.id == obituary.mosque_id):
        flash('U heeft geen toestemming om dit overlijdensbericht te verifiëren.', 'error')
        return redirect(url_for('obituaries.index'))

    try:
        obituary.is_approved = True
        db.session.commit()
        flash('Overlijdensbericht is geverifieerd.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Er is een fout opgetreden bij het verifiëren van het overlijdensbericht.', 'error')

    return redirect(url_for('obituaries.index'))

@obituaries.route('/<int:obituary_id>/delete', methods=['POST'])
@login_required
def delete_obituary(obituary_id):
    if not current_user.is_admin:
        flash('U heeft geen toestemming om overlijdensberichten te verwijderen.', 'error')
        return redirect(url_for('obituaries.index'))

    obituary = Obituary.query.get_or_404(obituary_id)

    try:
        db.session.delete(obituary)
        db.session.commit()
        flash('Overlijdensbericht is succesvol verwijderd.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Er is een fout opgetreden bij het verwijderen van het overlijdensbericht.', 'error')
        print(f"Error: {str(e)}")

    return redirect(url_for('obituaries.index'))