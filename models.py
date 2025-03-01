from datetime import datetime
from flask_login import UserMixin
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    user_type = db.Column(db.String(20), nullable=False)  # 'visitor' or 'mosque'
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Mosque-specific fields
    mosque_name = db.Column(db.String(200))
    mosque_street = db.Column(db.String(100))
    mosque_number = db.Column(db.String(10))
    mosque_postal = db.Column(db.String(10))
    mosque_city = db.Column(db.String(100))
    mosque_phone = db.Column(db.String(20))
    mosque_email = db.Column(db.String(120))
    mosque_website = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # Additional information fields
    mission_statement = db.Column(db.Text)
    vision_statement = db.Column(db.Text)
    activities = db.Column(db.Text)
    facilities = db.Column(db.Text)
    languages = db.Column(db.String(200))
    accessibility_features = db.Column(db.Text)

    # Relationships
    events = db.relationship('Event', backref='organizer', lazy=True)

    def get_full_address(self):
        if self.user_type == 'mosque':
            return f"{self.mosque_street} {self.mosque_number}, {self.mosque_postal} {self.mosque_city}"
        return None

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    max_participants = db.Column(db.Integer)
    registration_required = db.Column(db.Boolean, default=False)
    is_collaboration = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship for event registrations
    registrations = db.relationship('EventRegistration', backref='event', lazy=True)

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='registered')  # registered, cancelled, attended

    # Add unique constraint to prevent duplicate registrations
    __table_args__ = (db.UniqueConstraint('event_id', 'user_id', name='_event_user_uc'),)