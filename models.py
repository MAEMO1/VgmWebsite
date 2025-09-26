from datetime import datetime, date, time
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Time, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50), default='user')  # 'admin', 'mosque_admin', 'user'
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'))
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mosque = db.relationship('Mosque', backref='users')
    created_events = db.relationship('Event', backref='creator')
    uploaded_media = db.relationship('MediaFile', backref='uploader')
    created_blog_posts = db.relationship('BlogPost', backref='author')
    created_janazah_events = db.relationship('JanazahEvent', backref='creator')
    responded_contacts = db.relationship('ContactSubmission', backref='responder')

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
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
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
    fundraising_campaigns = db.relationship('FundraisingCampaign', backref='mosque', cascade='all, delete-orphan')
    contact_submissions = db.relationship('ContactSubmission', backref='mosque', cascade='all, delete-orphan')

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
    
    __table_args__ = (db.UniqueConstraint('mosque_id', 'date', name='unique_mosque_date'),)

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
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # 'image', 'video', 'document'
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlogPost(db.Model):
    """Blog posts/News model"""
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category = db.Column(db.String(100), default='news')  # 'news', 'announcement', 'reflection'
    featured_image = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
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
    
    # Relationships
    user = db.relationship('User', backref='sessions')

# Legacy models for backward compatibility
class IfterEvent(db.Model):
    """Simplified iftar event model for backward compatibility"""
    __tablename__ = 'ifter_events'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time)
    location = db.Column(db.String(200))
    is_family_friendly = db.Column(db.Boolean, default=True)
    capacity = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    mosque = db.relationship('Mosque', backref='ifter_events')

# Additional models for compatibility with existing routes
class MosqueImage(db.Model):
    """Legacy MosqueImage model for compatibility"""
    __tablename__ = 'mosque_images_legacy'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MosqueVideo(db.Model):
    """Legacy MosqueVideo model for compatibility"""
    __tablename__ = 'mosque_videos_legacy'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    video_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MosqueNotificationPreference(db.Model):
    """Legacy MosqueNotificationPreference model for compatibility"""
    __tablename__ = 'mosque_notification_preferences_legacy'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MosqueBoardMember(db.Model):
    """Legacy MosqueBoardMember model for compatibility"""
    __tablename__ = 'mosque_board_members_legacy'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MosquePhoto(db.Model):
    """Legacy MosquePhoto model for compatibility"""
    __tablename__ = 'mosque_photos_legacy'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    photo_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContentChangeLog(db.Model):
    """Legacy ContentChangeLog model for compatibility"""
    __tablename__ = 'content_change_logs_legacy'
    
    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String(50), nullable=False)
    content_id = db.Column(db.Integer, nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    change_description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventMosqueCollaboration(db.Model):
    """Legacy EventMosqueCollaboration model for compatibility"""
    __tablename__ = 'event_mosque_collaborations_legacy'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlogCategory(db.Model):
    """Legacy BlogCategory model for compatibility"""
    __tablename__ = 'blog_categories_legacy'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LearningContent(db.Model):
    """Legacy LearningContent model for compatibility"""
    __tablename__ = 'learning_content_legacy'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # 'video', 'article', 'audio'
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('blog_categories_legacy.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)

class PaymentConfig(db.Model):
    """Legacy PaymentConfig model for compatibility"""
    __tablename__ = 'payment_configs_legacy'
    
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # 'stripe', 'paypal', 'bank_transfer'
    config_data = db.Column(db.Text)  # JSON string with payment config
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)