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
    
    # Notification preferences
    event_notifications = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=True)
    
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
    notifications_received = db.relationship('Notification', backref='recipient', lazy=True)
    
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
    event_type = db.Column(db.String(20), nullable=False, default='individual')  # 'individual', 'vgm', or 'collaboration'
    is_collaboration = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Recurrence fields
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_type = db.Column(db.String(20))  # 'daily', 'weekly', 'monthly'
    recurrence_end_date = db.Column(db.DateTime)
    parent_event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)
    
    # Relationships
    registrations = db.relationship('EventRegistration', backref='event', lazy=True)
    recurring_events = db.relationship('Event', backref=db.backref('parent_event', remote_side=[id]))

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='registered')  # registered, cancelled, attended
    
    # Add unique constraint to prevent duplicate registrations
    __table_args__ = (db.UniqueConstraint('event_id', 'user_id', name='_event_user_uc'),)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Event
    event = db.relationship('Event')

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    donor_name = db.Column(db.String(100))
    donor_email = db.Column(db.String(120))
    is_anonymous = db.Column(db.Boolean, default=False)
    is_monthly = db.Column(db.Boolean, default=False)
    payment_method = db.Column(db.String(20), nullable=False)
    payment_status = db.Column(db.String(20), default='pending')
    payment_initiated_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_completed_at = db.Column(db.DateTime)

    # Relationship with campaign if donation is for a specific campaign
    campaign_id = db.Column(db.Integer, db.ForeignKey('fundraising_campaign.id'), nullable=True)
    campaign = db.relationship('FundraisingCampaign', backref='donations')

class FundraisingCampaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    goal_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_progress(self):
        """Calculate percentage of goal reached"""
        if self.goal_amount == 0:
            return 0
        return (self.current_amount / self.goal_amount) * 100