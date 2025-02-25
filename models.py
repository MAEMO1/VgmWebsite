from datetime import datetime, date
import random
from app import db
from flask_login import UserMixin

class MosqueNotificationPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'visitor' or 'mosque'

    # Add mosque_preferences relationship
    mosque_preferences = db.relationship('MosqueNotificationPreference',
                                      foreign_keys='MosqueNotificationPreference.user_id',
                                      backref='user',
                                      lazy='dynamic')

    # Notification preferences for mosques
    notify_all_mosques = db.Column(db.Boolean, default=False)
    notify_vgm_only = db.Column(db.Boolean, default=False)

    # Event notification settings
    notify_event_changes = db.Column(db.Boolean, default=False)
    notify_event_reminders = db.Column(db.Boolean, default=False)
    notify_obituaries = db.Column(db.Boolean, default=False)
    notify_funeral_updates = db.Column(db.Boolean, default=False)

    # Mosque-specific fields
    mosque_name = db.Column(db.String(200))
    mosque_street = db.Column(db.String(100))
    mosque_number = db.Column(db.String(10))
    mosque_postal = db.Column(db.String(10))
    mosque_city = db.Column(db.String(100))
    mosque_phone = db.Column(db.String(20))
    mosque_image = db.Column(db.String(500))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_verified = db.Column(db.Boolean, default=False)
    verification_status = db.Column(db.String(20), default='pending')
    verification_note = db.Column(db.Text)

    # Add new relationships
    board_members = db.relationship('MosqueBoardMember', backref='mosque', lazy='dynamic')
    history_entries = db.relationship('MosqueHistory', backref='mosque', lazy='dynamic')
    photos = db.relationship('MosquePhoto', backref='mosque', lazy='dynamic')
    content_changes = db.relationship('ContentChangeLog', 
                                    foreign_keys='ContentChangeLog.mosque_id',
                                    backref='mosque', 
                                    lazy='dynamic')

    # Events relationships - One to Many
    events = db.relationship('Event', 
                           foreign_keys='Event.mosque_id',
                           backref='mosque',
                           lazy='dynamic')

    # Prayer times relationship - One to Many
    prayer_times = db.relationship('PrayerTime',
                                 backref='mosque',
                                 lazy='dynamic')

    # New fields for mosque profiles
    foundation_year = db.Column(db.Integer)
    mission_statement = db.Column(db.Text)
    vision_statement = db.Column(db.Text)
    activities = db.Column(db.Text)  # List of regular activities
    facilities = db.Column(db.Text)  # Available facilities
    languages = db.Column(db.String(200))  # Languages of services/khutbah
    capacity = db.Column(db.Integer)  # Prayer hall capacity
    accessibility_features = db.Column(db.Text)  # Accessibility information
    parking_info = db.Column(db.Text)  # Parking information
    public_transport = db.Column(db.Text)  # Public transport directions

    def get_full_address(self):
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

    # Event organization fields
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Direct mosque relationship
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # For admin organizers

    # New field for event flyer
    flyer_url = db.Column(db.String(500))  # URL to event flyer image

    # New fields for event categorization
    event_type = db.Column(db.String(20), nullable=False, default='individual')  # 'vgm', 'collaboration', 'individual'
    category = db.Column(db.String(50))  # 'ramadan', 'lecture', 'workshop', etc.
    is_featured = db.Column(db.Boolean, default=False)  # For highlighting important events
    featured_image = db.Column(db.String(500))  # URL to event image
    featured_until = db.Column(db.DateTime)  # How long to feature the event

    # Many to Many relationship for collaborating mosques
    collaborating_mosques = db.relationship('User',
                                       secondary='event_mosque_collaboration',
                                       backref=db.backref('collaborated_events', lazy='dynamic'))

    # One to Many relationships
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
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<PrayerTime {self.prayer_name} at {self.time}>'

class Obituary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_death = db.Column(db.Date, nullable=False)
    funeral_date = db.Column(db.DateTime)
    details = db.Column(db.Text)
    age = db.Column(db.Integer)
    birth_place = db.Column(db.String(200))
    death_place = db.Column(db.String(200))
    prayer_time = db.Column(db.DateTime)
    prayer_date = db.Column(db.Date)  # New field for storing the date when prayer is after a specific prayer
    prayer_after = db.Column(db.String(20))  # stores which prayer: fajr, dhuhr, asr, etc.
    death_prayer_location = db.Column(db.String(200))  # Place of death prayer
    burial_location = db.Column(db.String(200))
    additional_notes = db.Column(db.Text)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Link to mosque user for verification
    submitter_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Link to user who submitted

    # New required fields for submitter information - temporarily nullable
    submitter_name = db.Column(db.String(100), nullable=True)
    submitter_phone = db.Column(db.String(20), nullable=True)

    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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

class MosqueBoardMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    photo_url = db.Column(db.String(500))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MosqueHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MosquePhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # e.g., 'events', 'building', 'community'
    url = db.Column(db.String(500), nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    taken_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentChangeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # 'profile', 'history', 'board_member', etc.
    content_id = db.Column(db.Integer)  # ID of the changed content
    change_type = db.Column(db.String(20), nullable=False)  # 'create', 'update', 'delete'
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)
    is_approved = db.Column(db.Boolean, default=False)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlogCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('blog_category.id'), nullable=True)
    posts = db.relationship('BlogPost', secondary='post_categories', back_populates='categories')

    # Self-referential relationship for parent-child categories
    subcategories = db.relationship('BlogCategory',
        backref=db.backref('parent', remote_side=[id]),
        cascade="all, delete-orphan")

post_categories = db.Table('post_categories',
    db.Column('post_id', db.Integer, db.ForeignKey('blog_post.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('blog_category.id'), primary_key=True)
)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(500))  # Featured image
    video_url = db.Column(db.String(500))  # Video URL (YouTube, Vimeo, etc.)
    video_platform = db.Column(db.String(50))  # 'youtube', 'vimeo', etc.
    video_thumbnail = db.Column(db.String(500))  # Thumbnail for video
    has_video = db.Column(db.Boolean, default=False)  # Quick check if post contains video
    slug = db.Column(db.String(200), unique=True, nullable=False)
    excerpt = db.Column(db.Text)  # Short description for preview
    is_featured = db.Column(db.Boolean, default=False)  # For highlighting important articles
    reading_time = db.Column(db.Integer)  # Estimated reading time in minutes

    # Add categories relationship
    categories = db.relationship('BlogCategory', secondary='post_categories', back_populates='posts')

    def __repr__(self):
        return f'<BlogPost {self.title}>'

    def calculate_reading_time(self):
        """Calculate estimated reading time based on content length"""
        words_per_minute = 200
        word_count = len(self.content.split())
        minutes = round(word_count / words_per_minute)
        return max(1, minutes)  # Minimum 1 minute reading time

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    donor_name = db.Column(db.String(100))  # Optional, can be anonymous
    donor_email = db.Column(db.String(120))  # Optional, for receipt
    message = db.Column(db.Text)  # Optional message from donor
    date = db.Column(db.DateTime, default=datetime.utcnow)
    is_anonymous = db.Column(db.Boolean, default=False)
    is_monthly = db.Column(db.Boolean, default=False)  # For recurring donations

    # Payment specific fields
    payment_method = db.Column(db.String(50), nullable=False)  # 'bank_transfer', 'paypal', 'apple_pay', 'bancontact', 'ideal'
    payment_status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed', 'refunded'
    transaction_id = db.Column(db.String(100))  # Payment provider transaction ID
    payment_reference = db.Column(db.String(50))  # For bank transfers

    # For mosque-specific donations
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # If mosque_id is NULL, it's a VGM donation

    # Payment provider specific IDs
    stripe_payment_intent_id = db.Column(db.String(100))  # For Stripe payments (Apple Pay, Bancontact, iDEAL)
    paypal_payment_id = db.Column(db.String(100))  # For PayPal payments

    # Timestamps for payment tracking
    payment_initiated_at = db.Column(db.DateTime)
    payment_completed_at = db.Column(db.DateTime)
    campaign_id = db.Column(db.Integer, db.ForeignKey('fundraising_campaign.id'))

    def __init__(self, **kwargs):
        super(Donation, self).__init__(**kwargs)
        if self.payment_method == 'bank_transfer':
            self.payment_reference = self.generate_payment_reference()

    def generate_payment_reference(self):
        """Generate a unique payment reference for bank transfers"""
        # Format: VGM-YYYYMMDD-XXXX where X is random
        date_part = datetime.utcnow().strftime('%Y%m%d')
        random_part = ''.join(random.choices('0123456789', k=4))
        return f'VGM-{date_part}-{random_part}'

class PaymentConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), unique=True, nullable=False)  # 'stripe', 'paypal', etc.
    is_active = db.Column(db.Boolean, default=True)
    config = db.Column(db.JSON)  # Store provider-specific configuration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

    def __repr__(self):
        return f'<Message {self.subject}>'

class LearningContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    topic = db.Column(db.String(50), nullable=False)  # plichtenleer, geloofsleer, etc.
    subtopic = db.Column(db.String(100), nullable=False)  # Shahada, Gebed, etc.
    order = db.Column(db.Integer)  # For ordering content within a subtopic
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Video fields
    video_url = db.Column(db.String(500))  # URL to video (YouTube, Vimeo)
    video_platform = db.Column(db.String(50))  # 'youtube', 'vimeo', etc.
    has_video = db.Column(db.Boolean, default=False)

    # Relationship with the author
    author = db.relationship('User', backref=db.backref('learning_content', lazy='dynamic'))

    def __repr__(self):
        return f'<LearningContent {self.title}>'

class FundraisingCampaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    goal_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(500))  # Optional campaign image

    donations = db.relationship('Donation', backref='campaign', lazy='dynamic')

    def calculate_progress(self):
        """Calculate percentage of goal reached"""
        if self.goal_amount == 0:
            return 0
        return min(100, (self.current_amount / self.goal_amount) * 100)

    def __repr__(self):
        return f'<FundraisingCampaign {self.title}>'

# Add new IfterEvent model after the Event model
class IfterEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time)
    location = db.Column(db.String(200))
    women_entrance = db.Column(db.String(200))  # New field for women's entrance
    capacity = db.Column(db.Integer)
    is_family_friendly = db.Column(db.Boolean, default=True)
    registration_required = db.Column(db.Boolean, default=False)
    registration_deadline = db.Column(db.DateTime)
    dietary_options = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

    # Recurring event fields
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_type = db.Column(db.String(20))  # 'daily' or 'weekly'
    recurrence_end_date = db.Column(db.Date)  # When the recurring event ends

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    mosque = db.relationship('User', backref='ifter_events')
    registrations = db.relationship('IfterRegistration', backref='ifter_event', lazy='dynamic')

class IfterRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ifter_event_id = db.Column(db.Integer, db.ForeignKey('ifter_event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    number_of_people = db.Column(db.Integer, default=1)
    dietary_requirements = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='registered')  # registered, cancelled, attended


class RamadanQuranResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    arabic_text = db.Column(db.Text)
    translation = db.Column(db.Text)
    explanation = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50))  # e.g., 'quran', 'dua', 'dhikr'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with author
    author = db.relationship('User', backref=db.backref('quran_resources', lazy='dynamic'))

class RamadanVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(500))  # URL to video (YouTube, Vimeo)
    thumbnail_url = db.Column(db.String(500))
    duration = db.Column(db.String(20))  # Duration in format "HH:MM:SS"
    speaker = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with author
    author = db.relationship('User', backref=db.backref('ramadan_videos', lazy='dynamic'))

class RamadanProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(500))
    category = db.Column(db.String(50))  # e.g., 'lecture', 'workshop', 'gathering'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with organizer
    organizer = db.relationship('User', backref=db.backref('ramadan_programs', lazy='dynamic'))