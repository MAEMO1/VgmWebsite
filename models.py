from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'visitor' or 'mosque'

    # Mosque-specific fields
    mosque_name = db.Column(db.String(200))
    mosque_address = db.Column(db.String(300))
    mosque_street = db.Column(db.String(100))  # New field for street
    mosque_number = db.Column(db.String(10))   # New field for house number
    mosque_postal = db.Column(db.String(10))   # New field for postal code
    mosque_city = db.Column(db.String(100))    # New field for city
    mosque_phone = db.Column(db.String(20))
    mosque_image = db.Column(db.String(500))   # New field for mosque image URL
    latitude = db.Column(db.Float)             # New field for map coordinates
    longitude = db.Column(db.Float)            # New field for map coordinates
    is_verified = db.Column(db.Boolean, default=False)  # For mosque accounts

    # Notification preferences
    notify_new_events = db.Column(db.Boolean, default=True)
    notify_event_changes = db.Column(db.Boolean, default=True)
    notify_event_reminders = db.Column(db.Boolean, default=True)
    notify_obituaries = db.Column(db.Boolean, default=True)

    # Relationships
    notifications = db.relationship('EventNotification', backref='user', lazy='dynamic')
    event_registrations = db.relationship('EventRegistration', backref='user', lazy='dynamic')
    managed_events = db.relationship('Event', backref='organizer', lazy='dynamic')
    obituaries = db.relationship('Obituary', backref='mosque', lazy='dynamic')

    def get_full_address(self):
        """Return the full formatted address for the mosque"""
        if self.user_type == 'mosque':
            return f"{self.mosque_street} {self.mosque_number}, {self.mosque_postal} {self.mosque_city}"
        return None

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    max_participants = db.Column(db.Integer)
    registration_required = db.Column(db.Boolean, default=False)
    reminder_before = db.Column(db.Integer)  # Minutes before event to send reminder
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Link to mosque user

    # Relationships
    registrations = db.relationship('EventRegistration', backref='event', lazy='dynamic')
    notifications = db.relationship('EventNotification', backref='event', lazy='dynamic')

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='registered')  # registered, cancelled, attended

class EventNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    type = db.Column(db.String(50))  # new_event, event_update, reminder
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

class PrayerTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prayer_name = db.Column(db.String(20), nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Link to mosque user

class Obituary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_death = db.Column(db.Date, nullable=False)
    funeral_date = db.Column(db.DateTime)
    details = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Link to mosque user for verification

    # New fields for extended features
    age = db.Column(db.Integer)
    birth_place = db.Column(db.String(200))
    death_place = db.Column(db.String(200))
    burial_location = db.Column(db.String(200))
    family_contact = db.Column(db.String(200))
    prayer_time = db.Column(db.DateTime)
    death_prayer_location = db.Column(db.String(200))  # New field for place of death prayer
    cause_of_death = db.Column(db.String(200))
    additional_notes = db.Column(db.Text)

    # Notification tracking
    notifications_sent = db.Column(db.Boolean, default=False)
    reminder_sent = db.Column(db.Boolean, default=False)

class ObituaryNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    obituary_id = db.Column(db.Integer, db.ForeignKey('obituary.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_type = db.Column(db.String(50))  # 'new', 'update', 'reminder'
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    # Relationships
    obituary = db.relationship('Obituary', backref='notifications')
    user = db.relationship('User', backref='obituary_notifications')