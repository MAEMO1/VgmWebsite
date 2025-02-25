from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from models import Message, User
from datetime import datetime
from flask_babel import _

messages = Blueprint('messages', __name__, url_prefix='/messages')

@messages.route('/')
@login_required
def inbox():
    """Show user's inbox with received messages"""
    received_messages = Message.query.filter_by(
        recipient_id=current_user.id
    ).order_by(Message.created_at.desc()).all()

    sent_messages = Message.query.filter_by(
        sender_id=current_user.id
    ).order_by(Message.created_at.desc()).all()

    unread_count = Message.query.filter_by(
        recipient_id=current_user.id, 
        is_read=False
    ).count()

    return render_template('messages/inbox.html',
                         received_messages=received_messages,
                         sent_messages=sent_messages,
                         unread_count=unread_count)

@messages.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    """Compose and send a new message"""
    if request.method == 'POST':
        recipient_id = request.form.get('recipient_id')
        subject = request.form.get('subject')
        body = request.form.get('body')

        if not all([recipient_id, subject, body]):
            flash(_('Alle velden zijn verplicht.'), 'error')
            return redirect(url_for('messages.compose'))

        recipient = User.query.get(recipient_id)
        if not recipient:
            flash(_('Ontvanger niet gevonden.'), 'error')
            return redirect(url_for('messages.compose'))

        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            subject=subject,
            body=body
        )
        db.session.add(message)

        try:
            db.session.commit()
            flash(_('Bericht succesvol verzonden.'), 'success')
            return redirect(url_for('messages.inbox'))
        except Exception as e:
            db.session.rollback()
            flash(_('Fout bij het verzenden van het bericht.'), 'error')
            print(f"Error sending message: {e}")
            return redirect(url_for('messages.compose'))

    # For GET request, show compose form
    # Get list of possible recipients (mosque admins and VGM admins)
    recipients = User.query.filter(
        (User.user_type == 'mosque') | (User.is_admin == True)
    ).filter(User.id != current_user.id).all()

    return render_template('messages/compose.html', recipients=recipients)

@messages.route('/<int:message_id>')
@login_required
def view_message(message_id):
    """View a specific message"""
    message = Message.query.get_or_404(message_id)

    # Check if user has permission to view this message
    if message.recipient_id != current_user.id and message.sender_id != current_user.id:
        flash(_('U heeft geen toestemming om dit bericht te bekijken.'), 'error')
        return redirect(url_for('messages.inbox'))

    # Mark as read if current user is recipient
    if message.recipient_id == current_user.id and not message.is_read:
        message.is_read = True
        db.session.commit()

    return render_template('messages/view.html', message=message)

@messages.route('/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    """Delete a message"""
    message = Message.query.get_or_404(message_id)

    # Check if user has permission to delete this message
    if message.recipient_id != current_user.id and message.sender_id != current_user.id:
        flash(_('U heeft geen toestemming om dit bericht te verwijderen.'), 'error')
        return redirect(url_for('messages.inbox'))

    try:
        db.session.delete(message)
        db.session.commit()
        flash(_('Bericht succesvol verwijderd.'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Fout bij het verwijderen van het bericht.'), 'error')
        print(f"Error deleting message: {e}")

    return redirect(url_for('messages.inbox'))