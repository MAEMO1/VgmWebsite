from datetime import datetime, date, time
from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    user_type = db.Column(db.String(20), nullable=False)  # 'visitor' or 'mosque'
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)

    # Mosque-specific fields
    mosque_name = db.Column(db.String(200))
    mosque_street = db.Column(db.String(100))
    mosque_number = db.Column(db.String(10))
    mosque_postal = db.Column(db.String(10))
    mosque_city = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

class IfterEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time)
    location = db.Column(db.String(200))
    is_family_friendly = db.Column(db.Boolean, default=True)
    capacity = db.Column(db.Integer)

    # Relationship
    mosque = db.relationship('User', backref='ifter_events')

class BoardMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    term_start = db.Column(db.Date, nullable=False)
    term_end = db.Column(db.Date, nullable=False)
    image = db.Column(db.String(200))

    # Relationship
    mosque = db.relationship('User', backref='board_members')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationship
    mosque = db.relationship('User', backref='events')

class PrayerTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    prayer_name = db.Column(db.String(20), nullable=False)
    time = db.Column(db.Time, nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationship
    mosque = db.relationship('User', backref='prayer_times')

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationship
    author = db.relationship('User', backref='blog_posts')

class MosqueImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationship
    mosque = db.relationship('User', backref='images')

class MosqueVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationship
    mosque = db.relationship('User', backref='videos')

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    donor = db.relationship('User', foreign_keys=[donor_id], backref='donations_made')
    mosque = db.relationship('User', foreign_keys=[mosque_id], backref='donations_received')

class MosqueNotificationPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    enabled = db.Column(db.Boolean, default=True)

    # Relationship
    mosque = db.relationship('User', backref='notification_preferences')

class MosqueBoardMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    photo_url = db.Column(db.String(500))

    # Relationship
    mosque = db.relationship('User', backref='mosque_board_members')

class MosqueHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    photo_url = db.Column(db.String(500))

    # Relationship
    mosque = db.relationship('User', backref='history_entries')

class MosquePhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    is_featured = db.Column(db.Boolean, default=False)

    # Relationship
    mosque = db.relationship('User', backref='photos')

class ContentChangeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)
    change_type = db.Column(db.String(20), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)

    # Relationships
    mosque = db.relationship('User', foreign_keys=[mosque_id], backref='content_changes')
    changed_by = db.relationship('User', foreign_keys=[changed_by_id], backref='changes_made')

class EventMosqueCollaboration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(50))

    # Relationships
    event = db.relationship('Event', backref='collaborations')
    mosque = db.relationship('User', backref='event_collaborations')

class FundraisingCampaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    goal_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationship
    mosque = db.relationship('User', backref='fundraising_campaigns')