"""
SQLAlchemy ORM models for VGM Website
This replaces the raw SQLite queries in app.py with proper ORM models
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50), default='user')  # 'GAST', 'LID', 'MOSKEE_BEHEERDER', 'BEHEERDER'
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'))
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mosque = db.relationship('Mosque', backref='users')
    created_events = db.relationship('Event', backref='creator')
    uploaded_files = db.relationship('MediaFile', backref='uploader')
    created_campaigns = db.relationship('FundraisingCampaign', backref='creator')
    created_janazah = db.relationship('JanazahEvent', backref='creator')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def manages_mosque(self, mosque_id):
        """Check if user manages a specific mosque"""
        return (self.role == 'MOSKEE_BEHEERDER' and self.mosque_id == mosque_id) or self.role == 'BEHEERDER'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'role': self.role,
            'mosque_id': self.mosque_id,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Mosque(db.Model):
    """Mosque model"""
    __tablename__ = 'mosques'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    website = db.Column(db.String(255))
    capacity = db.Column(db.Integer)
    established_year = db.Column(db.Integer)
    imam_name = db.Column(db.String(255))
    description = db.Column(db.Text)
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    features = db.relationship('MosqueFeature', backref='mosque', cascade='all, delete-orphan')
    prayer_times = db.relationship('PrayerTime', backref='mosque', cascade='all, delete-orphan')
    events = db.relationship('Event', backref='mosque', cascade='all, delete-orphan')
    board_members = db.relationship('BoardMember', backref='mosque', cascade='all, delete-orphan')
    history = db.relationship('MosqueHistory', backref='mosque', cascade='all, delete-orphan')
    media_files = db.relationship('MediaFile', backref='mosque', cascade='all, delete-orphan')
    janazah_events = db.relationship('JanazahEvent', backref='mosque', cascade='all, delete-orphan')
    donations = db.relationship('Donation', backref='mosque', cascade='all, delete-orphan')
    campaigns = db.relationship('FundraisingCampaign', backref='mosque', cascade='all, delete-orphan')
    contact_submissions = db.relationship('ContactSubmission', backref='mosque')
    access_requests = db.relationship('MosqueAccessRequest', backref='mosque')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'capacity': self.capacity,
            'established_year': self.established_year,
            'imam_name': self.imam_name,
            'description': self.description,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MosqueFeature(db.Model):
    """Mosque features model"""
    __tablename__ = 'mosque_features'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    feature_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PrayerTime(db.Model):
    """Prayer times model"""
    __tablename__ = 'prayer_times'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    fajr = db.Column(db.Time, nullable=False)
    dhuhr = db.Column(db.Time, nullable=False)
    asr = db.Column(db.Time, nullable=False)
    maghrib = db.Column(db.Time, nullable=False)
    isha = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('mosque_id', 'date'),)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'mosque_id': self.mosque_id,
            'date': self.date.isoformat() if self.date else None,
            'fajr': self.fajr.isoformat() if self.fajr else None,
            'dhuhr': self.dhuhr.isoformat() if self.dhuhr else None,
            'asr': self.asr.isoformat() if self.asr else None,
            'maghrib': self.maghrib.isoformat() if self.maghrib else None,
            'isha': self.isha.isoformat() if self.isha else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Event(db.Model):
    """Events model"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=False)
    event_type = db.Column(db.String(50), default='event')  # 'prayer', 'event', 'lecture', 'community'
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_pattern = db.Column(db.String(50))  # 'weekly', 'monthly', 'yearly'
    max_attendees = db.Column(db.Integer)
    current_attendees = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'mosque_id': self.mosque_id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'event_time': self.event_time.isoformat() if self.event_time else None,
            'event_type': self.event_type,
            'is_recurring': self.is_recurring,
            'recurring_pattern': self.recurring_pattern,
            'max_attendees': self.max_attendees,
            'current_attendees': self.current_attendees,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'mosque_name': self.mosque.name if self.mosque else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class BoardMember(db.Model):
    """Board members model"""
    __tablename__ = 'board_members'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MosqueHistory(db.Model):
    """Mosque history model"""
    __tablename__ = 'mosque_history'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    event_title = db.Column(db.String(255), nullable=False)
    event_description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MediaFile(db.Model):
    """Media files model"""
    __tablename__ = 'media_files'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50), nullable=False)  # 'image', 'video', 'document'
    mime_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer)
    campaign_id = db.Column(db.Integer)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BlogPost(db.Model):
    """News/Blog posts model"""
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category = db.Column(db.String(100), default='news')  # 'news', 'announcement', 'reflection'
    featured_image = db.Column(db.String(500))
    status = db.Column(db.String(50), default='draft')  # 'draft', 'published'
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='blog_posts')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'author_id': self.author_id,
            'first_name': self.author.first_name if self.author else None,
            'last_name': self.author.last_name if self.author else None,
            'category': self.category,
            'featured_image': self.featured_image,
            'status': self.status,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class JanazahEvent(db.Model):
    """Janazah (funeral prayers) model"""
    __tablename__ = 'janazah_events'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    deceased_name = db.Column(db.String(255), nullable=False)
    deceased_age = db.Column(db.Integer)
    deceased_date = db.Column(db.Date, nullable=False)
    prayer_date = db.Column(db.Date, nullable=False)
    prayer_time = db.Column(db.Time, nullable=False)
    burial_location = db.Column(db.String(255))
    contact_person = db.Column(db.String(255))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(255))
    notes = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Donation(db.Model):
    """Donations model"""
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('fundraising_campaigns.id'))
    donor_name = db.Column(db.String(255))
    donor_email = db.Column(db.String(255))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50))  # 'stripe', 'paypal', 'bank_transfer'
    payment_status = db.Column(db.String(50), default='pending')  # 'pending', 'completed', 'failed'
    transaction_id = db.Column(db.String(255))
    is_anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = db.relationship('FundraisingCampaign', backref='donations')


class FundraisingCampaign(db.Model):
    """Fundraising campaigns model"""
    __tablename__ = 'fundraising_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    target_amount = db.Column(db.Numeric(10, 2))
    current_amount = db.Column(db.Numeric(10, 2), default=0)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ContactSubmission(db.Model):
    """Contact form submissions model"""
    __tablename__ = 'contact_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'))
    status = db.Column(db.String(50), default='new')  # 'new', 'in_progress', 'resolved'
    responded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSession(db.Model):
    """User sessions model for authentication"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PasswordResetToken(db.Model):
    """Password reset tokens model"""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MosqueAccessRequest(db.Model):
    """Mosque administrator access requests model"""
    __tablename__ = 'mosque_access_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'))
    mosque_name = db.Column(db.String(255))
    motivation = db.Column(db.Text)
    contact_email = db.Column(db.String(255))
    contact_phone = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')
    admin_notes = db.Column(db.Text)
    processed_at = db.Column(db.DateTime)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Create indexes for better performance
Index('idx_mosques_active', Mosque.is_active)
Index('idx_events_mosque_date', Event.mosque_id, Event.event_date)
Index('idx_prayer_times_mosque_date', PrayerTime.mosque_id, PrayerTime.date)
Index('idx_blog_posts_published', BlogPost.status, BlogPost.published_at)
Index('idx_janazah_events_date', JanazahEvent.prayer_date)
Index('idx_donations_mosque', Donation.mosque_id)
Index('idx_contact_submissions_status', ContactSubmission.status)
Index('idx_password_reset_tokens_user', PasswordResetToken.user_id)
Index('idx_mosque_access_requests_status', MosqueAccessRequest.status)
