from datetime import datetime, date
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'visitor' or 'mosque'

    # Event notification settings
    notify_new_events = db.Column(db.Boolean, default=False)
    notify_event_changes = db.Column(db.Boolean, default=False)
    notify_event_reminders = db.Column(db.Boolean, default=False)

    # Obituary notification settings
    notify_obituaries = db.Column(db.Boolean, default=False)
    notify_funeral_updates = db.Column(db.Boolean, default=False)

    # Mosque-specific fields
    mosque_name = db.Column(db.String(200))
    mosque_street = db.Column(db.String(100))  # Street name
    mosque_number = db.Column(db.String(10))   # House number
    mosque_postal = db.Column(db.String(10))   # Postal code
    mosque_city = db.Column(db.String(100))    # City
    mosque_phone = db.Column(db.String(20))
    mosque_image = db.Column(db.String(500))   # URL to mosque image
    latitude = db.Column(db.Float)             # Geographical coordinates
    longitude = db.Column(db.Float)            # Geographical coordinates
    is_verified = db.Column(db.Boolean, default=False)
    verification_status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    verification_note = db.Column(db.Text)  # Admin feedback for verification

    # Donation-related fields
    donation_enabled = db.Column(db.Boolean, default=False)
    donation_iban = db.Column(db.String(34))  # IBAN number for donations
    donation_description = db.Column(db.Text)  # Description of what donations are used for
    donation_goal = db.Column(db.Float)  # Optional donation goal
    donation_goal_description = db.Column(db.Text)  # Description of the donation goal

    # Contact fields
    mosque_email = db.Column(db.String(120))   # Public contact email
    mosque_website = db.Column(db.String(200)) # Mosque website
    mosque_fax = db.Column(db.String(20))      # Fax number
    emergency_contact = db.Column(db.String(100)) # Emergency contact name
    emergency_phone = db.Column(db.String(20))  # Emergency contact number

    # Social media links
    facebook_url = db.Column(db.String(200))
    twitter_url = db.Column(db.String(200))
    instagram_url = db.Column(db.String(200))
    youtube_url = db.Column(db.String(200))
    whatsapp_number = db.Column(db.String(20))

    history = db.Column(db.Text)
    establishment_year = db.Column(db.Integer)
    friday_prayer_time = db.Column(db.Time)

    # Relationships remain unchanged
    images = db.relationship('MosqueImage', backref='mosque', lazy='dynamic')
    videos = db.relationship('MosqueVideo', backref='mosque', lazy='dynamic')
    prayer_times = db.relationship('PrayerTime', backref='mosque', lazy='dynamic')
    events = db.relationship('Event', backref='mosque', lazy='dynamic')
    authored_posts = db.relationship('BlogPost', backref='author', lazy='dynamic')

    def get_full_address(self):
        """Return the full formatted address for the mosque"""
        if self.user_type == 'mosque':
            return f"{self.mosque_street} {self.mosque_number}, {self.mosque_postal} {self.mosque_city}"
        return None

class MosqueImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(200))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

class MosqueVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

class EventMosqueCollaboration(db.Model):
    """Association table for mosque collaborations on events"""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(50))  # e.g., 'host', 'co-organizer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

    # New field for event flyer
    flyer_url = db.Column(db.String(500))  # URL to event flyer image

    # New fields for event categorization
    event_type = db.Column(db.String(20), nullable=False, default='individual')  # 'vgm', 'collaboration', 'individual'
    is_featured = db.Column(db.Boolean, default=False)  # For highlighting important events
    featured_image = db.Column(db.String(500))  # URL to event image
    featured_until = db.Column(db.DateTime)  # How long to feature the event

    # Relationships
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Primary organizer (mosque or VGM)
    collaborating_mosques = db.relationship('User',
                                          secondary='event_mosque_collaboration',
                                          backref=db.backref('collaborated_events', lazy='dynamic'))

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

    age = db.Column(db.Integer)
    birth_place = db.Column(db.String(200))
    death_place = db.Column(db.String(200))
    burial_location = db.Column(db.String(200))
    family_contact = db.Column(db.String(200))
    prayer_time = db.Column(db.DateTime)
    death_prayer_location = db.Column(db.String(200))  # Place of death prayer
    cause_of_death = db.Column(db.String(200))
    additional_notes = db.Column(db.Text)

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

    obituary = db.relationship('Obituary', backref='notifications')
    user = db.relationship('User', backref='obituary_notifications')

class BoardMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image = db.Column(db.String(200))
    term_start = db.Column(db.Date, nullable=False)
    term_end = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with mosque
    mosque = db.relationship('User', backref='board_positions')

    def __repr__(self):
        return f'<BoardMember {self.name} ({self.role})>'

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(500))  # Optional featured image
    slug = db.Column(db.String(200), unique=True, nullable=False)
    excerpt = db.Column(db.Text)  # Short description for preview

    def __repr__(self):
        return f'<BlogPost {self.title}>'

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    donor_name = db.Column(db.String(100))  # Optional, can be anonymous
    donor_email = db.Column(db.String(120))  # Optional, for receipt
    message = db.Column(db.Text)  # Optional message from donor
    date = db.Column(db.DateTime, default=datetime.utcnow)
    is_anonymous = db.Column(db.Boolean, default=False)

    # For mosque-specific donations
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # If mosque_id is NULL, it's a VGM donation

    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed'
    transaction_id = db.Column(db.String(100))  # Payment provider transaction ID