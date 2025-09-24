import os
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Time, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configure secret key
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///vgm_website.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# For development/testing, use SQLite
if os.getenv('FLASK_ENV') == 'development':
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///vgm_website.db'

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

# Define models directly in app.py
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
    
    # Relationship
    mosque = db.relationship('Mosque', backref='users')

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
    
    # Relationship
    mosque = db.relationship('Mosque', backref='prayer_times')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('mosque_id', 'date', name='unique_mosque_date'),)

class Event(db.Model):
    """Event model"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50), nullable=False)  # 'religious', 'educational', 'social', 'community'
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    location = db.Column(db.String(255))
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'))
    organizer_name = db.Column(db.String(255))
    organizer_email = db.Column(db.String(255))
    organizer_phone = db.Column(db.String(20))
    max_participants = db.Column(db.Integer)
    registration_required = db.Column(db.Boolean, default=False)
    registration_deadline = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    mosque = db.relationship('Mosque', backref='events')

class EventRegistration(db.Model):
    """Event registration model"""
    __tablename__ = 'event_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='confirmed')  # 'confirmed', 'cancelled', 'waitlist'
    notes = db.Column(db.Text)
    
    # Relationships
    event = db.relationship('Event', backref='registrations')
    user = db.relationship('User', backref='event_registrations')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('event_id', 'user_id', name='unique_event_user'),)

class FundraisingCampaign(db.Model):
    """Fundraising campaign model"""
    __tablename__ = 'fundraising_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    campaign_type = db.Column(db.String(50), nullable=False)  # 'mosque_construction', 'maintenance', 'education', 'charity', 'emergency'
    target_amount = db.Column(db.Numeric(10, 2), nullable=False)
    current_amount = db.Column(db.Numeric(10, 2), default=0)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'))
    organizer_name = db.Column(db.String(255))
    organizer_email = db.Column(db.String(255))
    organizer_phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    mosque = db.relationship('Mosque', backref='fundraising_campaigns')

class Donation(db.Model):
    """Donation model"""
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('fundraising_campaigns.id'), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    donation_type = db.Column(db.String(20), default='one_time')  # 'one_time', 'monthly', 'yearly'
    payment_method = db.Column(db.String(20), default='bank_transfer')  # 'bank_transfer', 'cash', 'online'
    payment_status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed', 'refunded'
    donor_name = db.Column(db.String(255))
    donor_email = db.Column(db.String(255))
    donor_phone = db.Column(db.String(20))
    is_anonymous = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    donation_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = db.relationship('FundraisingCampaign', backref='donations')
    donor = db.relationship('User', backref='donations')

class ContactSubmission(db.Model):
    """Contact form submission model"""
    __tablename__ = 'contact_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submission_type = db.Column(db.String(50), default='general')  # 'general', 'mosque_info', 'event_inquiry', 'donation', 'complaint', 'suggestion'
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'))
    status = db.Column(db.String(20), default='new')  # 'new', 'in_progress', 'resolved', 'closed'
    priority = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'urgent'
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    response = db.Column(db.Text)
    response_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mosque = db.relationship('Mosque', backref='contact_submissions')
    assigned_user = db.relationship('User', backref='assigned_contacts')

class BlogPost(db.Model):
    """Blog post/news article model"""
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    excerpt = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    featured_image = db.Column(db.String(500))
    post_type = db.Column(db.String(50), default='news')  # 'news', 'announcement', 'reflection', 'event', 'mosque_update'
    category = db.Column(db.String(100), default='general')  # 'general', 'events', 'mosques', 'education', 'community', 'ramadan', 'hajj'
    tags = db.Column(db.String(500))  # Comma-separated tags
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'))
    status = db.Column(db.String(20), default='draft')  # 'draft', 'published', 'archived'
    is_featured = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='blog_posts')
    mosque = db.relationship('Mosque', backref='blog_posts')

class JanazahEvent(db.Model):
    """Janazah (funeral prayer) event model"""
    __tablename__ = 'janazah_events'
    
    id = db.Column(db.Integer, primary_key=True)
    deceased_name = db.Column(db.String(255), nullable=False)
    deceased_age = db.Column(db.Integer)
    deceased_gender = db.Column(db.String(10))  # 'male', 'female'
    deceased_date = db.Column(db.Date, nullable=False)  # Date of death
    prayer_date = db.Column(db.Date, nullable=False)  # Date of janazah prayer
    prayer_time = db.Column(db.Time, nullable=False)  # Time of janazah prayer
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosques.id'), nullable=False)
    burial_location = db.Column(db.String(255))
    burial_time = db.Column(db.Time)
    contact_person = db.Column(db.String(255))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(255))
    family_notes = db.Column(db.Text)  # Special requests from family
    admin_notes = db.Column(db.Text)  # Internal admin notes
    status = db.Column(db.String(20), default='confirmed')  # 'pending', 'confirmed', 'completed', 'cancelled'
    is_public = db.Column(db.Boolean, default=True)  # Whether to show publicly
    is_urgent = db.Column(db.Boolean, default=False)  # Urgent janazah
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Who reported this
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mosque = db.relationship('Mosque', backref='janazah_events')
    reporter = db.relationship('User', backref='reported_janazah')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database tables
with app.app_context():
    db.create_all()

# JWT Secret Key
JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            role=data.get('role', 'user'),
            mosque_id=data.get('mosque_id'),
            is_active=True,
            email_verified=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            },
            'token': token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Login user
        login_user(user, remember=data.get('remember', False))
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'mosque_id': user.mosque_id
            },
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    try:
        return jsonify({
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
                'phone': current_user.phone,
                'role': current_user.role,
                'mosque_id': current_user.mosque_id,
                'is_active': current_user.is_active,
                'email_verified': current_user.email_verified,
                'created_at': current_user.created_at.isoformat() if current_user.created_at else None
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/health')
def health_check():
    try:
        return {'status': 'healthy', 'service': 'running'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500

# Database health check endpoint
@app.route('/health/db')
def database_health_check():
    try:
        # Test basic query
        result = User.query.count()
        return {
            'status': 'healthy',
            'users_count': result,
            'database_url': app.config['SQLALCHEMY_DATABASE_URI']
        }, 200
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'database_url': app.config['SQLALCHEMY_DATABASE_URI']
        }, 500

# Mosque Management API Endpoints

@app.route('/api/mosques', methods=['GET'])
def get_mosques():
    """Get all mosques"""
    try:
        mosques = Mosque.query.filter_by(is_active=True).all()
        return jsonify({
            'mosques': [{
                'id': mosque.id,
                'name': mosque.name,
                'address': mosque.address,
                'phone': mosque.phone,
                'email': mosque.email,
                'website': mosque.website,
                'capacity': mosque.capacity,
                'established_year': mosque.established_year,
                'imam_name': mosque.imam_name,
                'description': mosque.description,
                'latitude': mosque.latitude,
                'longitude': mosque.longitude,
                'created_at': mosque.created_at.isoformat() if mosque.created_at else None
            } for mosque in mosques]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mosques/<int:mosque_id>', methods=['GET'])
def get_mosque(mosque_id):
    """Get a specific mosque by ID"""
    try:
        mosque = Mosque.query.get_or_404(mosque_id)
        return jsonify({
            'mosque': {
                'id': mosque.id,
                'name': mosque.name,
                'address': mosque.address,
                'phone': mosque.phone,
                'email': mosque.email,
                'website': mosque.website,
                'capacity': mosque.capacity,
                'established_year': mosque.established_year,
                'imam_name': mosque.imam_name,
                'description': mosque.description,
                'latitude': mosque.latitude,
                'longitude': mosque.longitude,
                'created_at': mosque.created_at.isoformat() if mosque.created_at else None
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mosques', methods=['POST'])
@login_required
def create_mosque():
    """Create a new mosque"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new mosque
        mosque = Mosque(
            name=data['name'],
            address=data['address'],
            phone=data.get('phone'),
            email=data.get('email'),
            website=data.get('website'),
            capacity=data.get('capacity'),
            established_year=data.get('established_year'),
            imam_name=data.get('imam_name'),
            description=data.get('description'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            is_active=True
        )
        
        db.session.add(mosque)
        db.session.commit()
        
        return jsonify({
            'message': 'Mosque created successfully',
            'mosque': {
                'id': mosque.id,
                'name': mosque.name,
                'address': mosque.address,
                'phone': mosque.phone,
                'email': mosque.email,
                'website': mosque.website,
                'capacity': mosque.capacity,
                'established_year': mosque.established_year,
                'imam_name': mosque.imam_name,
                'description': mosque.description,
                'latitude': mosque.latitude,
                'longitude': mosque.longitude
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/mosques/<int:mosque_id>', methods=['PUT'])
@login_required
def update_mosque(mosque_id):
    """Update a mosque"""
    try:
        mosque = Mosque.query.get_or_404(mosque_id)
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            mosque.name = data['name']
        if 'address' in data:
            mosque.address = data['address']
        if 'phone' in data:
            mosque.phone = data['phone']
        if 'email' in data:
            mosque.email = data['email']
        if 'website' in data:
            mosque.website = data['website']
        if 'capacity' in data:
            mosque.capacity = data['capacity']
        if 'established_year' in data:
            mosque.established_year = data['established_year']
        if 'imam_name' in data:
            mosque.imam_name = data['imam_name']
        if 'description' in data:
            mosque.description = data['description']
        if 'latitude' in data:
            mosque.latitude = data['latitude']
        if 'longitude' in data:
            mosque.longitude = data['longitude']
        
        mosque.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Mosque updated successfully',
            'mosque': {
                'id': mosque.id,
                'name': mosque.name,
                'address': mosque.address,
                'phone': mosque.phone,
                'email': mosque.email,
                'website': mosque.website,
                'capacity': mosque.capacity,
                'established_year': mosque.established_year,
                'imam_name': mosque.imam_name,
                'description': mosque.description,
                'latitude': mosque.latitude,
                'longitude': mosque.longitude
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/mosques/<int:mosque_id>', methods=['DELETE'])
@login_required
def delete_mosque(mosque_id):
    """Delete a mosque (soft delete)"""
    try:
        mosque = Mosque.query.get_or_404(mosque_id)
        mosque.is_active = False
        mosque.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Mosque deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Prayer Times API Endpoints

@app.route('/api/mosques/<int:mosque_id>/prayer-times', methods=['GET'])
def get_mosque_prayer_times(mosque_id):
    """Get prayer times for a specific mosque"""
    try:
        mosque = Mosque.query.get_or_404(mosque_id)
        
        # Get query parameters
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = PrayerTime.query.filter_by(mosque_id=mosque_id)
        
        if date_from:
            query = query.filter(PrayerTime.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        if date_to:
            query = query.filter(PrayerTime.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        
        prayer_times = query.order_by(PrayerTime.date).all()
        
        return jsonify({
            'mosque': {
                'id': mosque.id,
                'name': mosque.name,
                'address': mosque.address
            },
            'prayer_times': [{
                'id': pt.id,
                'date': pt.date.isoformat(),
                'fajr': pt.fajr.strftime('%H:%M'),
                'dhuhr': pt.dhuhr.strftime('%H:%M'),
                'asr': pt.asr.strftime('%H:%M'),
                'maghrib': pt.maghrib.strftime('%H:%M'),
                'isha': pt.isha.strftime('%H:%M'),
                'created_at': pt.created_at.isoformat() if pt.created_at else None
            } for pt in prayer_times]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mosques/<int:mosque_id>/prayer-times', methods=['POST'])
@login_required
def create_prayer_times(mosque_id):
    """Create prayer times for a specific mosque"""
    try:
        mosque = Mosque.query.get_or_404(mosque_id)
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['date', 'fajr', 'dhuhr', 'asr', 'maghrib', 'isha']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse date and times
        prayer_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        fajr_time = datetime.strptime(data['fajr'], '%H:%M').time()
        dhuhr_time = datetime.strptime(data['dhuhr'], '%H:%M').time()
        asr_time = datetime.strptime(data['asr'], '%H:%M').time()
        maghrib_time = datetime.strptime(data['maghrib'], '%H:%M').time()
        isha_time = datetime.strptime(data['isha'], '%H:%M').time()
        
        # Check if prayer times already exist for this date
        existing = PrayerTime.query.filter_by(mosque_id=mosque_id, date=prayer_date).first()
        if existing:
            return jsonify({'error': 'Prayer times already exist for this date'}), 400
        
        # Create new prayer times
        prayer_time = PrayerTime(
            mosque_id=mosque_id,
            date=prayer_date,
            fajr=fajr_time,
            dhuhr=dhuhr_time,
            asr=asr_time,
            maghrib=maghrib_time,
            isha=isha_time
        )
        
        db.session.add(prayer_time)
        db.session.commit()
        
        return jsonify({
            'message': 'Prayer times created successfully',
            'prayer_time': {
                'id': prayer_time.id,
                'mosque_id': prayer_time.mosque_id,
                'date': prayer_time.date.isoformat(),
                'fajr': prayer_time.fajr.strftime('%H:%M'),
                'dhuhr': prayer_time.dhuhr.strftime('%H:%M'),
                'asr': prayer_time.asr.strftime('%H:%M'),
                'maghrib': prayer_time.maghrib.strftime('%H:%M'),
                'isha': prayer_time.isha.strftime('%H:%M')
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/mosques/<int:mosque_id>/prayer-times/<int:prayer_time_id>', methods=['PUT'])
@login_required
def update_prayer_times(mosque_id, prayer_time_id):
    """Update prayer times for a specific mosque"""
    try:
        mosque = Mosque.query.get_or_404(mosque_id)
        prayer_time = PrayerTime.query.filter_by(id=prayer_time_id, mosque_id=mosque_id).first_or_404()
        data = request.get_json()
        
        # Update fields
        if 'date' in data:
            prayer_time.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'fajr' in data:
            prayer_time.fajr = datetime.strptime(data['fajr'], '%H:%M').time()
        if 'dhuhr' in data:
            prayer_time.dhuhr = datetime.strptime(data['dhuhr'], '%H:%M').time()
        if 'asr' in data:
            prayer_time.asr = datetime.strptime(data['asr'], '%H:%M').time()
        if 'maghrib' in data:
            prayer_time.maghrib = datetime.strptime(data['maghrib'], '%H:%M').time()
        if 'isha' in data:
            prayer_time.isha = datetime.strptime(data['isha'], '%H:%M').time()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Prayer times updated successfully',
            'prayer_time': {
                'id': prayer_time.id,
                'mosque_id': prayer_time.mosque_id,
                'date': prayer_time.date.isoformat(),
                'fajr': prayer_time.fajr.strftime('%H:%M'),
                'dhuhr': prayer_time.dhuhr.strftime('%H:%M'),
                'asr': prayer_time.asr.strftime('%H:%M'),
                'maghrib': prayer_time.maghrib.strftime('%H:%M'),
                'isha': prayer_time.isha.strftime('%H:%M')
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/mosques/<int:mosque_id>/prayer-times/<int:prayer_time_id>', methods=['DELETE'])
@login_required
def delete_prayer_times(mosque_id, prayer_time_id):
    """Delete prayer times for a specific mosque"""
    try:
        mosque = Mosque.query.get_or_404(mosque_id)
        prayer_time = PrayerTime.query.filter_by(id=prayer_time_id, mosque_id=mosque_id).first_or_404()
        
        db.session.delete(prayer_time)
        db.session.commit()
        
        return jsonify({'message': 'Prayer times deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/prayer-times/today', methods=['GET'])
def get_today_prayer_times():
    """Get today's prayer times for all mosques"""
    try:
        today = datetime.now().date()
        prayer_times = PrayerTime.query.filter_by(date=today).all()
        
        # Group by mosque
        mosques_data = {}
        for pt in prayer_times:
            if pt.mosque_id not in mosques_data:
                mosques_data[pt.mosque_id] = {
                    'mosque': {
                        'id': pt.mosque.id,
                        'name': pt.mosque.name,
                        'address': pt.mosque.address
                    },
                    'prayer_times': {}
                }
            
            mosques_data[pt.mosque_id]['prayer_times'] = {
                'fajr': pt.fajr.strftime('%H:%M'),
                'dhuhr': pt.dhuhr.strftime('%H:%M'),
                'asr': pt.asr.strftime('%H:%M'),
                'maghrib': pt.maghrib.strftime('%H:%M'),
                'isha': pt.isha.strftime('%H:%M')
            }
        
        return jsonify({
            'date': today.isoformat(),
            'mosques': list(mosques_data.values())
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Events Management API Endpoints

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events"""
    try:
        # Get query parameters
        event_type = request.args.get('type')
        mosque_id = request.args.get('mosque_id')
        upcoming_only = request.args.get('upcoming_only', 'false').lower() == 'true'
        
        query = Event.query.filter_by(is_active=True)
        
        if event_type:
            query = query.filter_by(event_type=event_type)
        if mosque_id:
            query = query.filter_by(mosque_id=mosque_id)
        if upcoming_only:
            query = query.filter(Event.start_date >= datetime.now())
        
        events = query.order_by(Event.start_date).all()
        
        return jsonify({
            'events': [{
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'event_type': event.event_type,
                'start_date': event.start_date.isoformat(),
                'end_date': event.end_date.isoformat() if event.end_date else None,
                'location': event.location,
                'mosque': {
                    'id': event.mosque.id,
                    'name': event.mosque.name,
                    'address': event.mosque.address
                } if event.mosque else None,
                'organizer_name': event.organizer_name,
                'organizer_email': event.organizer_email,
                'organizer_phone': event.organizer_phone,
                'max_participants': event.max_participants,
                'registration_required': event.registration_required,
                'registration_deadline': event.registration_deadline.isoformat() if event.registration_deadline else None,
                'created_at': event.created_at.isoformat() if event.created_at else None
            } for event in events]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get a specific event by ID"""
    try:
        event = Event.query.get_or_404(event_id)
        
        # Get registration count
        registration_count = EventRegistration.query.filter_by(event_id=event_id, status='confirmed').count()
        
        return jsonify({
            'event': {
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'event_type': event.event_type,
                'start_date': event.start_date.isoformat(),
                'end_date': event.end_date.isoformat() if event.end_date else None,
                'location': event.location,
                'mosque': {
                    'id': event.mosque.id,
                    'name': event.mosque.name,
                    'address': event.mosque.address
                } if event.mosque else None,
                'organizer_name': event.organizer_name,
                'organizer_email': event.organizer_email,
                'organizer_phone': event.organizer_phone,
                'max_participants': event.max_participants,
                'registration_required': event.registration_required,
                'registration_deadline': event.registration_deadline.isoformat() if event.registration_deadline else None,
                'registration_count': registration_count,
                'created_at': event.created_at.isoformat() if event.created_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events', methods=['POST'])
@login_required
def create_event():
    """Create a new event"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'event_type', 'start_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse dates
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        end_date = None
        if data.get('end_date'):
            end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        
        registration_deadline = None
        if data.get('registration_deadline'):
            registration_deadline = datetime.fromisoformat(data['registration_deadline'].replace('Z', '+00:00'))
        
        # Create new event
        event = Event(
            title=data['title'],
            description=data.get('description'),
            event_type=data['event_type'],
            start_date=start_date,
            end_date=end_date,
            location=data.get('location'),
            mosque_id=data.get('mosque_id'),
            organizer_name=data.get('organizer_name'),
            organizer_email=data.get('organizer_email'),
            organizer_phone=data.get('organizer_phone'),
            max_participants=data.get('max_participants'),
            registration_required=data.get('registration_required', False),
            registration_deadline=registration_deadline,
            is_active=True
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'message': 'Event created successfully',
            'event': {
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'event_type': event.event_type,
                'start_date': event.start_date.isoformat(),
                'end_date': event.end_date.isoformat() if event.end_date else None,
                'location': event.location,
                'mosque_id': event.mosque_id,
                'organizer_name': event.organizer_name,
                'organizer_email': event.organizer_email,
                'organizer_phone': event.organizer_phone,
                'max_participants': event.max_participants,
                'registration_required': event.registration_required,
                'registration_deadline': event.registration_deadline.isoformat() if event.registration_deadline else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['PUT'])
@login_required
def update_event(event_id):
    """Update an event"""
    try:
        event = Event.query.get_or_404(event_id)
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'event_type' in data:
            event.event_type = data['event_type']
        if 'start_date' in data:
            event.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        if 'end_date' in data:
            event.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')) if data['end_date'] else None
        if 'location' in data:
            event.location = data['location']
        if 'mosque_id' in data:
            event.mosque_id = data['mosque_id']
        if 'organizer_name' in data:
            event.organizer_name = data['organizer_name']
        if 'organizer_email' in data:
            event.organizer_email = data['organizer_email']
        if 'organizer_phone' in data:
            event.organizer_phone = data['organizer_phone']
        if 'max_participants' in data:
            event.max_participants = data['max_participants']
        if 'registration_required' in data:
            event.registration_required = data['registration_required']
        if 'registration_deadline' in data:
            event.registration_deadline = datetime.fromisoformat(data['registration_deadline'].replace('Z', '+00:00')) if data['registration_deadline'] else None
        
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Event updated successfully',
            'event': {
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'event_type': event.event_type,
                'start_date': event.start_date.isoformat(),
                'end_date': event.end_date.isoformat() if event.end_date else None,
                'location': event.location,
                'mosque_id': event.mosque_id,
                'organizer_name': event.organizer_name,
                'organizer_email': event.organizer_email,
                'organizer_phone': event.organizer_phone,
                'max_participants': event.max_participants,
                'registration_required': event.registration_required,
                'registration_deadline': event.registration_deadline.isoformat() if event.registration_deadline else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    """Delete an event (soft delete)"""
    try:
        event = Event.query.get_or_404(event_id)
        event.is_active = False
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Event deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>/register', methods=['POST'])
@login_required
def register_for_event(event_id):
    """Register for an event"""
    try:
        event = Event.query.get_or_404(event_id)
        
        if not event.registration_required:
            return jsonify({'error': 'Registration not required for this event'}), 400
        
        if event.registration_deadline and datetime.now() > event.registration_deadline:
            return jsonify({'error': 'Registration deadline has passed'}), 400
        
        # Check if user is already registered
        existing_registration = EventRegistration.query.filter_by(event_id=event_id, user_id=current_user.id).first()
        if existing_registration:
            return jsonify({'error': 'You are already registered for this event'}), 400
        
        # Check if event is full
        if event.max_participants:
            current_registrations = EventRegistration.query.filter_by(event_id=event_id, status='confirmed').count()
            if current_registrations >= event.max_participants:
                return jsonify({'error': 'Event is full'}), 400
        
        # Create registration
        registration = EventRegistration(
            event_id=event_id,
            user_id=current_user.id,
            status='confirmed'
        )
        
        db.session.add(registration)
        db.session.commit()
        
        return jsonify({
            'message': 'Successfully registered for event',
            'registration': {
                'id': registration.id,
                'event_id': registration.event_id,
                'user_id': registration.user_id,
                'status': registration.status,
                'registration_date': registration.registration_date.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>/unregister', methods=['POST'])
@login_required
def unregister_from_event(event_id):
    """Unregister from an event"""
    try:
        event = Event.query.get_or_404(event_id)
        
        registration = EventRegistration.query.filter_by(event_id=event_id, user_id=current_user.id).first()
        if not registration:
            return jsonify({'error': 'You are not registered for this event'}), 400
        
        registration.status = 'cancelled'
        db.session.commit()
        
        return jsonify({'message': 'Successfully unregistered from event'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>/registrations', methods=['GET'])
@login_required
def get_event_registrations(event_id):
    """Get registrations for an event"""
    try:
        event = Event.query.get_or_404(event_id)
        registrations = EventRegistration.query.filter_by(event_id=event_id).all()
        
        return jsonify({
            'event': {
                'id': event.id,
                'title': event.title,
                'max_participants': event.max_participants
            },
            'registrations': [{
                'id': reg.id,
                'user': {
                    'id': reg.user.id,
                    'first_name': reg.user.first_name,
                    'last_name': reg.user.last_name,
                    'email': reg.user.email
                },
                'status': reg.status,
                'registration_date': reg.registration_date.isoformat(),
                'notes': reg.notes
            } for reg in registrations]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Donations Management API Endpoints

@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    """Get all fundraising campaigns"""
    try:
        # Get query parameters
        campaign_type = request.args.get('type')
        mosque_id = request.args.get('mosque_id')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = FundraisingCampaign.query
        
        if active_only:
            query = query.filter_by(is_active=True)
        if campaign_type:
            query = query.filter_by(campaign_type=campaign_type)
        if mosque_id:
            query = query.filter_by(mosque_id=mosque_id)
        
        campaigns = query.order_by(FundraisingCampaign.created_at.desc()).all()
        
        return jsonify({
            'campaigns': [{
                'id': campaign.id,
                'title': campaign.title,
                'description': campaign.description,
                'campaign_type': campaign.campaign_type,
                'target_amount': float(campaign.target_amount),
                'current_amount': float(campaign.current_amount),
                'progress_percentage': float((campaign.current_amount / campaign.target_amount) * 100) if campaign.target_amount > 0 else 0,
                'start_date': campaign.start_date.isoformat(),
                'end_date': campaign.end_date.isoformat() if campaign.end_date else None,
                'mosque': {
                    'id': campaign.mosque.id,
                    'name': campaign.mosque.name,
                    'address': campaign.mosque.address
                } if campaign.mosque else None,
                'organizer_name': campaign.organizer_name,
                'organizer_email': campaign.organizer_email,
                'organizer_phone': campaign.organizer_phone,
                'is_active': campaign.is_active,
                'created_at': campaign.created_at.isoformat() if campaign.created_at else None
            } for campaign in campaigns]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get a specific campaign by ID"""
    try:
        campaign = FundraisingCampaign.query.get_or_404(campaign_id)
        
        # Get donation count
        donation_count = Donation.query.filter_by(campaign_id=campaign_id, payment_status='completed').count()
        
        return jsonify({
            'campaign': {
                'id': campaign.id,
                'title': campaign.title,
                'description': campaign.description,
                'campaign_type': campaign.campaign_type,
                'target_amount': float(campaign.target_amount),
                'current_amount': float(campaign.current_amount),
                'progress_percentage': float((campaign.current_amount / campaign.target_amount) * 100) if campaign.target_amount > 0 else 0,
                'start_date': campaign.start_date.isoformat(),
                'end_date': campaign.end_date.isoformat() if campaign.end_date else None,
                'mosque': {
                    'id': campaign.mosque.id,
                    'name': campaign.mosque.name,
                    'address': campaign.mosque.address
                } if campaign.mosque else None,
                'organizer_name': campaign.organizer_name,
                'organizer_email': campaign.organizer_email,
                'organizer_phone': campaign.organizer_phone,
                'donation_count': donation_count,
                'is_active': campaign.is_active,
                'created_at': campaign.created_at.isoformat() if campaign.created_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns', methods=['POST'])
@login_required
def create_campaign():
    """Create a new fundraising campaign"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'campaign_type', 'target_amount', 'start_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse dates
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        end_date = None
        if data.get('end_date'):
            end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        
        # Create new campaign
        campaign = FundraisingCampaign(
            title=data['title'],
            description=data.get('description'),
            campaign_type=data['campaign_type'],
            target_amount=data['target_amount'],
            current_amount=0,
            start_date=start_date,
            end_date=end_date,
            mosque_id=data.get('mosque_id'),
            organizer_name=data.get('organizer_name'),
            organizer_email=data.get('organizer_email'),
            organizer_phone=data.get('organizer_phone'),
            is_active=True
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        return jsonify({
            'message': 'Campaign created successfully',
            'campaign': {
                'id': campaign.id,
                'title': campaign.title,
                'description': campaign.description,
                'campaign_type': campaign.campaign_type,
                'target_amount': float(campaign.target_amount),
                'current_amount': float(campaign.current_amount),
                'start_date': campaign.start_date.isoformat(),
                'end_date': campaign.end_date.isoformat() if campaign.end_date else None,
                'mosque_id': campaign.mosque_id,
                'organizer_name': campaign.organizer_name,
                'organizer_email': campaign.organizer_email,
                'organizer_phone': campaign.organizer_phone
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns/<int:campaign_id>', methods=['PUT'])
@login_required
def update_campaign(campaign_id):
    """Update a campaign"""
    try:
        campaign = FundraisingCampaign.query.get_or_404(campaign_id)
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            campaign.title = data['title']
        if 'description' in data:
            campaign.description = data['description']
        if 'campaign_type' in data:
            campaign.campaign_type = data['campaign_type']
        if 'target_amount' in data:
            campaign.target_amount = data['target_amount']
        if 'start_date' in data:
            campaign.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        if 'end_date' in data:
            campaign.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')) if data['end_date'] else None
        if 'mosque_id' in data:
            campaign.mosque_id = data['mosque_id']
        if 'organizer_name' in data:
            campaign.organizer_name = data['organizer_name']
        if 'organizer_email' in data:
            campaign.organizer_email = data['organizer_email']
        if 'organizer_phone' in data:
            campaign.organizer_phone = data['organizer_phone']
        
        campaign.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Campaign updated successfully',
            'campaign': {
                'id': campaign.id,
                'title': campaign.title,
                'description': campaign.description,
                'campaign_type': campaign.campaign_type,
                'target_amount': float(campaign.target_amount),
                'current_amount': float(campaign.current_amount),
                'start_date': campaign.start_date.isoformat(),
                'end_date': campaign.end_date.isoformat() if campaign.end_date else None,
                'mosque_id': campaign.mosque_id,
                'organizer_name': campaign.organizer_name,
                'organizer_email': campaign.organizer_email,
                'organizer_phone': campaign.organizer_phone
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns/<int:campaign_id>', methods=['DELETE'])
@login_required
def delete_campaign(campaign_id):
    """Delete a campaign (soft delete)"""
    try:
        campaign = FundraisingCampaign.query.get_or_404(campaign_id)
        campaign.is_active = False
        campaign.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Campaign deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns/<int:campaign_id>/donate', methods=['POST'])
def make_donation(campaign_id):
    """Make a donation to a campaign"""
    try:
        campaign = FundraisingCampaign.query.get_or_404(campaign_id)
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if campaign is active
        if not campaign.is_active:
            return jsonify({'error': 'Campaign is not active'}), 400
        
        # Check if campaign has ended
        if campaign.end_date and datetime.now() > campaign.end_date:
            return jsonify({'error': 'Campaign has ended'}), 400
        
        # Create donation
        donation = Donation(
            campaign_id=campaign_id,
            donor_id=data.get('donor_id'),
            amount=data['amount'],
            donation_type=data.get('donation_type', 'one_time'),
            payment_method=data.get('payment_method', 'bank_transfer'),
            payment_status='pending',
            donor_name=data.get('donor_name'),
            donor_email=data.get('donor_email'),
            donor_phone=data.get('donor_phone'),
            is_anonymous=data.get('is_anonymous', False),
            notes=data.get('notes')
        )
        
        db.session.add(donation)
        db.session.commit()
        
        return jsonify({
            'message': 'Donation created successfully',
            'donation': {
                'id': donation.id,
                'campaign_id': donation.campaign_id,
                'amount': float(donation.amount),
                'donation_type': donation.donation_type,
                'payment_method': donation.payment_method,
                'payment_status': donation.payment_status,
                'donor_name': donation.donor_name,
                'donor_email': donation.donor_email,
                'donor_phone': donation.donor_phone,
                'is_anonymous': donation.is_anonymous,
                'notes': donation.notes,
                'donation_date': donation.donation_date.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns/<int:campaign_id>/donations', methods=['GET'])
def get_campaign_donations(campaign_id):
    """Get donations for a specific campaign"""
    try:
        campaign = FundraisingCampaign.query.get_or_404(campaign_id)
        donations = Donation.query.filter_by(campaign_id=campaign_id).order_by(Donation.donation_date.desc()).all()
        
        return jsonify({
            'campaign': {
                'id': campaign.id,
                'title': campaign.title,
                'target_amount': float(campaign.target_amount),
                'current_amount': float(campaign.current_amount)
            },
            'donations': [{
                'id': donation.id,
                'amount': float(donation.amount),
                'donation_type': donation.donation_type,
                'payment_method': donation.payment_method,
                'payment_status': donation.payment_status,
                'donor_name': donation.donor_name if not donation.is_anonymous else 'Anonymous',
                'donor_email': donation.donor_email if not donation.is_anonymous else None,
                'is_anonymous': donation.is_anonymous,
                'notes': donation.notes,
                'donation_date': donation.donation_date.isoformat()
            } for donation in donations]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/donations/<int:donation_id>/status', methods=['PUT'])
@login_required
def update_donation_status(donation_id):
    """Update donation payment status"""
    try:
        donation = Donation.query.get_or_404(donation_id)
        data = request.get_json()
        
        if 'payment_status' not in data:
            return jsonify({'error': 'payment_status is required'}), 400
        
        old_status = donation.payment_status
        new_status = data['payment_status']
        
        donation.payment_status = new_status
        db.session.commit()
        
        # Update campaign current amount if payment completed
        if old_status != 'completed' and new_status == 'completed':
            campaign = FundraisingCampaign.query.get(donation.campaign_id)
            campaign.current_amount += donation.amount
            db.session.commit()
        elif old_status == 'completed' and new_status != 'completed':
            # Subtract amount if payment was completed but now isn't
            campaign = FundraisingCampaign.query.get(donation.campaign_id)
            campaign.current_amount -= donation.amount
            db.session.commit()
        
        return jsonify({
            'message': 'Donation status updated successfully',
            'donation': {
                'id': donation.id,
                'payment_status': donation.payment_status,
                'amount': float(donation.amount)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Contact Form API Endpoints

@app.route('/api/contact', methods=['POST'])
def submit_contact_form():
    """Submit contact form"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Basic email validation
        email = data['email']
        if '@' not in email or '.' not in email.split('@')[1]:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Create contact submission
        submission = ContactSubmission(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            subject=data['subject'],
            message=data['message'],
            submission_type=data.get('submission_type', 'general'),
            mosque_id=data.get('mosque_id'),
            status='new',
            priority=data.get('priority', 'medium')
        )
        
        db.session.add(submission)
        db.session.commit()
        
        return jsonify({
            'message': 'Contact form submitted successfully',
            'submission': {
                'id': submission.id,
                'name': submission.name,
                'email': submission.email,
                'subject': submission.subject,
                'submission_type': submission.submission_type,
                'status': submission.status,
                'priority': submission.priority,
                'created_at': submission.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact', methods=['GET'])
@login_required
def get_contact_submissions():
    """Get all contact submissions (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get query parameters
        status = request.args.get('status')
        submission_type = request.args.get('type')
        priority = request.args.get('priority')
        mosque_id = request.args.get('mosque_id')
        
        query = ContactSubmission.query
        
        if status:
            query = query.filter_by(status=status)
        if submission_type:
            query = query.filter_by(submission_type=submission_type)
        if priority:
            query = query.filter_by(priority=priority)
        if mosque_id:
            query = query.filter_by(mosque_id=mosque_id)
        
        submissions = query.order_by(ContactSubmission.created_at.desc()).all()
        
        return jsonify({
            'submissions': [{
                'id': submission.id,
                'name': submission.name,
                'email': submission.email,
                'phone': submission.phone,
                'subject': submission.subject,
                'message': submission.message,
                'submission_type': submission.submission_type,
                'mosque': {
                    'id': submission.mosque.id,
                    'name': submission.mosque.name,
                    'address': submission.mosque.address
                } if submission.mosque else None,
                'status': submission.status,
                'priority': submission.priority,
                'assigned_to': {
                    'id': submission.assigned_user.id,
                    'name': f"{submission.assigned_user.first_name} {submission.assigned_user.last_name}",
                    'email': submission.assigned_user.email
                } if submission.assigned_user else None,
                'response': submission.response,
                'response_date': submission.response_date.isoformat() if submission.response_date else None,
                'created_at': submission.created_at.isoformat(),
                'updated_at': submission.updated_at.isoformat()
            } for submission in submissions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact/<int:submission_id>', methods=['GET'])
@login_required
def get_contact_submission(submission_id):
    """Get a specific contact submission"""
    try:
        submission = ContactSubmission.query.get_or_404(submission_id)
        
        # Check if user is admin or assigned to this submission
        if current_user.role != 'admin' and submission.assigned_to != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'submission': {
                'id': submission.id,
                'name': submission.name,
                'email': submission.email,
                'phone': submission.phone,
                'subject': submission.subject,
                'message': submission.message,
                'submission_type': submission.submission_type,
                'mosque': {
                    'id': submission.mosque.id,
                    'name': submission.mosque.name,
                    'address': submission.mosque.address
                } if submission.mosque else None,
                'status': submission.status,
                'priority': submission.priority,
                'assigned_to': {
                    'id': submission.assigned_user.id,
                    'name': f"{submission.assigned_user.first_name} {submission.assigned_user.last_name}",
                    'email': submission.assigned_user.email
                } if submission.assigned_user else None,
                'response': submission.response,
                'response_date': submission.response_date.isoformat() if submission.response_date else None,
                'created_at': submission.created_at.isoformat(),
                'updated_at': submission.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact/<int:submission_id>', methods=['PUT'])
@login_required
def update_contact_submission(submission_id):
    """Update contact submission status, priority, assignment, or response"""
    try:
        submission = ContactSubmission.query.get_or_404(submission_id)
        
        # Check if user is admin or assigned to this submission
        if current_user.role != 'admin' and submission.assigned_to != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'status' in data:
            submission.status = data['status']
        if 'priority' in data:
            submission.priority = data['priority']
        if 'assigned_to' in data:
            submission.assigned_to = data['assigned_to']
        if 'response' in data:
            submission.response = data['response']
            submission.response_date = datetime.utcnow()
        
        submission.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Contact submission updated successfully',
            'submission': {
                'id': submission.id,
                'status': submission.status,
                'priority': submission.priority,
                'assigned_to': submission.assigned_to,
                'response': submission.response,
                'response_date': submission.response_date.isoformat() if submission.response_date else None,
                'updated_at': submission.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact/<int:submission_id>', methods=['DELETE'])
@login_required
def delete_contact_submission(submission_id):
    """Delete contact submission (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        submission = ContactSubmission.query.get_or_404(submission_id)
        db.session.delete(submission)
        db.session.commit()
        
        return jsonify({'message': 'Contact submission deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact/stats', methods=['GET'])
@login_required
def get_contact_stats():
    """Get contact form statistics (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get statistics
        total_submissions = ContactSubmission.query.count()
        new_submissions = ContactSubmission.query.filter_by(status='new').count()
        in_progress_submissions = ContactSubmission.query.filter_by(status='in_progress').count()
        resolved_submissions = ContactSubmission.query.filter_by(status='resolved').count()
        
        # Get submissions by type
        submissions_by_type = db.session.query(
            ContactSubmission.submission_type,
            db.func.count(ContactSubmission.id)
        ).group_by(ContactSubmission.submission_type).all()
        
        # Get submissions by priority
        submissions_by_priority = db.session.query(
            ContactSubmission.priority,
            db.func.count(ContactSubmission.id)
        ).group_by(ContactSubmission.priority).all()
        
        return jsonify({
            'stats': {
                'total_submissions': total_submissions,
                'new_submissions': new_submissions,
                'in_progress_submissions': in_progress_submissions,
                'resolved_submissions': resolved_submissions
            },
            'by_type': {item[0]: item[1] for item in submissions_by_type},
            'by_priority': {item[0]: item[1] for item in submissions_by_priority}
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# News/Blog API Endpoints

@app.route('/api/blog', methods=['GET'])
def get_blog_posts():
    """Get all blog posts"""
    try:
        # Get query parameters
        post_type = request.args.get('type')
        category = request.args.get('category')
        status = request.args.get('status', 'published')
        featured = request.args.get('featured')
        pinned = request.args.get('pinned')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = BlogPost.query
        
        if status:
            query = query.filter_by(status=status)
        if post_type:
            query = query.filter_by(post_type=post_type)
        if category:
            query = query.filter_by(category=category)
        if featured:
            query = query.filter_by(is_featured=True)
        if pinned:
            query = query.filter_by(is_pinned=True)
        
        # Order by pinned first, then published date
        query = query.order_by(BlogPost.is_pinned.desc(), BlogPost.published_at.desc())
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        posts = query.all()
        
        return jsonify({
            'posts': [{
                'id': post.id,
                'title': post.title,
                'slug': post.slug,
                'excerpt': post.excerpt,
                'content': post.content,
                'featured_image': post.featured_image,
                'post_type': post.post_type,
                'category': post.category,
                'tags': post.tags.split(',') if post.tags else [],
                'author': {
                    'id': post.author.id,
                    'name': f"{post.author.first_name} {post.author.last_name}",
                    'email': post.author.email
                },
                'mosque': {
                    'id': post.mosque.id,
                    'name': post.mosque.name,
                    'address': post.mosque.address
                } if post.mosque else None,
                'status': post.status,
                'is_featured': post.is_featured,
                'is_pinned': post.is_pinned,
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'view_count': post.view_count,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat()
            } for post in posts]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blog/<int:post_id>', methods=['GET'])
def get_blog_post(post_id):
    """Get a specific blog post by ID"""
    try:
        post = BlogPost.query.get_or_404(post_id)
        
        # Increment view count
        post.view_count += 1
        db.session.commit()
        
        return jsonify({
            'post': {
                'id': post.id,
                'title': post.title,
                'slug': post.slug,
                'excerpt': post.excerpt,
                'content': post.content,
                'featured_image': post.featured_image,
                'post_type': post.post_type,
                'category': post.category,
                'tags': post.tags.split(',') if post.tags else [],
                'author': {
                    'id': post.author.id,
                    'name': f"{post.author.first_name} {post.author.last_name}",
                    'email': post.author.email
                },
                'mosque': {
                    'id': post.mosque.id,
                    'name': post.mosque.name,
                    'address': post.mosque.address
                } if post.mosque else None,
                'status': post.status,
                'is_featured': post.is_featured,
                'is_pinned': post.is_pinned,
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'view_count': post.view_count,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blog/slug/<slug>', methods=['GET'])
def get_blog_post_by_slug(slug):
    """Get a specific blog post by slug"""
    try:
        post = BlogPost.query.filter_by(slug=slug).first_or_404()
        
        # Increment view count
        post.view_count += 1
        db.session.commit()
        
        return jsonify({
            'post': {
                'id': post.id,
                'title': post.title,
                'slug': post.slug,
                'excerpt': post.excerpt,
                'content': post.content,
                'featured_image': post.featured_image,
                'post_type': post.post_type,
                'category': post.category,
                'tags': post.tags.split(',') if post.tags else [],
                'author': {
                    'id': post.author.id,
                    'name': f"{post.author.first_name} {post.author.last_name}",
                    'email': post.author.email
                },
                'mosque': {
                    'id': post.mosque.id,
                    'name': post.mosque.name,
                    'address': post.mosque.address
                } if post.mosque else None,
                'status': post.status,
                'is_featured': post.is_featured,
                'is_pinned': post.is_pinned,
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'view_count': post.view_count,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blog', methods=['POST'])
@login_required
def create_blog_post():
    """Create a new blog post"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate slug from title
        slug = data['title'].lower().replace(' ', '-').replace('_', '-')
        # Remove special characters except hyphens
        import re
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        
        # Ensure slug is unique
        original_slug = slug
        counter = 1
        while BlogPost.query.filter_by(slug=slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Create new blog post
        post = BlogPost(
            title=data['title'],
            slug=slug,
            excerpt=data.get('excerpt'),
            content=data['content'],
            featured_image=data.get('featured_image'),
            post_type=data.get('post_type', 'news'),
            category=data.get('category', 'general'),
            tags=data.get('tags', ''),
            author_id=current_user.id,
            mosque_id=data.get('mosque_id'),
            status=data.get('status', 'draft'),
            is_featured=data.get('is_featured', False),
            is_pinned=data.get('is_pinned', False)
        )
        
        # Set published_at if status is published
        if post.status == 'published':
            post.published_at = datetime.utcnow()
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'message': 'Blog post created successfully',
            'post': {
                'id': post.id,
                'title': post.title,
                'slug': post.slug,
                'excerpt': post.excerpt,
                'content': post.content,
                'featured_image': post.featured_image,
                'post_type': post.post_type,
                'category': post.category,
                'tags': post.tags.split(',') if post.tags else [],
                'author_id': post.author_id,
                'mosque_id': post.mosque_id,
                'status': post.status,
                'is_featured': post.is_featured,
                'is_pinned': post.is_pinned,
                'published_at': post.published_at.isoformat() if post.published_at else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/blog/<int:post_id>', methods=['PUT'])
@login_required
def update_blog_post(post_id):
    """Update a blog post"""
    try:
        post = BlogPost.query.get_or_404(post_id)
        
        # Check if user is author or admin
        if current_user.id != post.author_id and current_user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            post.title = data['title']
            # Update slug if title changed
            slug = data['title'].lower().replace(' ', '-').replace('_', '-')
            import re
            slug = re.sub(r'[^a-z0-9\-]', '', slug)
            original_slug = slug
            counter = 1
            while BlogPost.query.filter_by(slug=slug).filter(BlogPost.id != post_id).first():
                slug = f"{original_slug}-{counter}"
                counter += 1
            post.slug = slug
        
        if 'excerpt' in data:
            post.excerpt = data['excerpt']
        if 'content' in data:
            post.content = data['content']
        if 'featured_image' in data:
            post.featured_image = data['featured_image']
        if 'post_type' in data:
            post.post_type = data['post_type']
        if 'category' in data:
            post.category = data['category']
        if 'tags' in data:
            post.tags = data['tags']
        if 'mosque_id' in data:
            post.mosque_id = data['mosque_id']
        if 'status' in data:
            old_status = post.status
            post.status = data['status']
            # Set published_at if status changed to published
            if old_status != 'published' and data['status'] == 'published':
                post.published_at = datetime.utcnow()
        if 'is_featured' in data:
            post.is_featured = data['is_featured']
        if 'is_pinned' in data:
            post.is_pinned = data['is_pinned']
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Blog post updated successfully',
            'post': {
                'id': post.id,
                'title': post.title,
                'slug': post.slug,
                'excerpt': post.excerpt,
                'content': post.content,
                'featured_image': post.featured_image,
                'post_type': post.post_type,
                'category': post.category,
                'tags': post.tags.split(',') if post.tags else [],
                'author_id': post.author_id,
                'mosque_id': post.mosque_id,
                'status': post.status,
                'is_featured': post.is_featured,
                'is_pinned': post.is_pinned,
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'updated_at': post.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/blog/<int:post_id>', methods=['DELETE'])
@login_required
def delete_blog_post(post_id):
    """Delete a blog post"""
    try:
        post = BlogPost.query.get_or_404(post_id)
        
        # Check if user is author or admin
        if current_user.id != post.author_id and current_user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Blog post deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/blog/stats', methods=['GET'])
@login_required
def get_blog_stats():
    """Get blog statistics (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get statistics
        total_posts = BlogPost.query.count()
        published_posts = BlogPost.query.filter_by(status='published').count()
        draft_posts = BlogPost.query.filter_by(status='draft').count()
        featured_posts = BlogPost.query.filter_by(is_featured=True).count()
        
        # Get posts by type
        posts_by_type = db.session.query(
            BlogPost.post_type,
            db.func.count(BlogPost.id)
        ).group_by(BlogPost.post_type).all()
        
        # Get posts by category
        posts_by_category = db.session.query(
            BlogPost.category,
            db.func.count(BlogPost.id)
        ).group_by(BlogPost.category).all()
        
        # Get total views
        total_views = db.session.query(db.func.sum(BlogPost.view_count)).scalar() or 0
        
        return jsonify({
            'stats': {
                'total_posts': total_posts,
                'published_posts': published_posts,
                'draft_posts': draft_posts,
                'featured_posts': featured_posts,
                'total_views': total_views
            },
            'by_type': {item[0]: item[1] for item in posts_by_type},
            'by_category': {item[0]: item[1] for item in posts_by_category}
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Janazah Management API Endpoints

@app.route('/api/janazah', methods=['GET'])
def get_janazah_events():
    """Get all janazah events"""
    try:
        # Get query parameters
        mosque_id = request.args.get('mosque_id', type=int)
        status = request.args.get('status')
        is_public = request.args.get('is_public', 'true').lower() == 'true'
        is_urgent = request.args.get('is_urgent')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = JanazahEvent.query
        
        if mosque_id:
            query = query.filter_by(mosque_id=mosque_id)
        if status:
            query = query.filter_by(status=status)
        if is_public:
            query = query.filter_by(is_public=True)
        if is_urgent:
            query = query.filter_by(is_urgent=True)
        if date_from:
            query = query.filter(JanazahEvent.prayer_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        if date_to:
            query = query.filter(JanazahEvent.prayer_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        
        # Order by urgent first, then prayer date
        query = query.order_by(JanazahEvent.is_urgent.desc(), JanazahEvent.prayer_date.asc(), JanazahEvent.prayer_time.asc())
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        events = query.all()
        
        return jsonify({
            'events': [{
                'id': event.id,
                'deceased_name': event.deceased_name,
                'deceased_age': event.deceased_age,
                'deceased_gender': event.deceased_gender,
                'deceased_date': event.deceased_date.isoformat() if event.deceased_date else None,
                'prayer_date': event.prayer_date.isoformat() if event.prayer_date else None,
                'prayer_time': event.prayer_time.strftime('%H:%M') if event.prayer_time else None,
                'mosque': {
                    'id': event.mosque.id,
                    'name': event.mosque.name,
                    'address': event.mosque.address
                },
                'burial_location': event.burial_location,
                'burial_time': event.burial_time.strftime('%H:%M') if event.burial_time else None,
                'contact_person': event.contact_person,
                'contact_phone': event.contact_phone,
                'contact_email': event.contact_email,
                'family_notes': event.family_notes,
                'status': event.status,
                'is_public': event.is_public,
                'is_urgent': event.is_urgent,
                'reporter': {
                    'id': event.reporter.id,
                    'name': f"{event.reporter.first_name} {event.reporter.last_name}",
                    'email': event.reporter.email
                } if event.reporter else None,
                'created_at': event.created_at.isoformat(),
                'updated_at': event.updated_at.isoformat()
            } for event in events]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/janazah/<int:event_id>', methods=['GET'])
def get_janazah_event(event_id):
    """Get a specific janazah event by ID"""
    try:
        event = JanazahEvent.query.get_or_404(event_id)
        
        return jsonify({
            'event': {
                'id': event.id,
                'deceased_name': event.deceased_name,
                'deceased_age': event.deceased_age,
                'deceased_gender': event.deceased_gender,
                'deceased_date': event.deceased_date.isoformat() if event.deceased_date else None,
                'prayer_date': event.prayer_date.isoformat() if event.prayer_date else None,
                'prayer_time': event.prayer_time.strftime('%H:%M') if event.prayer_time else None,
                'mosque': {
                    'id': event.mosque.id,
                    'name': event.mosque.name,
                    'address': event.mosque.address
                },
                'burial_location': event.burial_location,
                'burial_time': event.burial_time.strftime('%H:%M') if event.burial_time else None,
                'contact_person': event.contact_person,
                'contact_phone': event.contact_phone,
                'contact_email': event.contact_email,
                'family_notes': event.family_notes,
                'admin_notes': event.admin_notes,
                'status': event.status,
                'is_public': event.is_public,
                'is_urgent': event.is_urgent,
                'reporter': {
                    'id': event.reporter.id,
                    'name': f"{event.reporter.first_name} {event.reporter.last_name}",
                    'email': event.reporter.email
                } if event.reporter else None,
                'created_at': event.created_at.isoformat(),
                'updated_at': event.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/janazah', methods=['POST'])
@login_required
def create_janazah_event():
    """Create a new janazah event"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['deceased_name', 'deceased_date', 'prayer_date', 'prayer_time', 'mosque_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new janazah event
        event = JanazahEvent(
            deceased_name=data['deceased_name'],
            deceased_age=data.get('deceased_age'),
            deceased_gender=data.get('deceased_gender'),
            deceased_date=datetime.strptime(data['deceased_date'], '%Y-%m-%d').date(),
            prayer_date=datetime.strptime(data['prayer_date'], '%Y-%m-%d').date(),
            prayer_time=datetime.strptime(data['prayer_time'], '%H:%M').time(),
            mosque_id=data['mosque_id'],
            burial_location=data.get('burial_location'),
            burial_time=datetime.strptime(data['burial_time'], '%H:%M').time() if data.get('burial_time') else None,
            contact_person=data.get('contact_person'),
            contact_phone=data.get('contact_phone'),
            contact_email=data.get('contact_email'),
            family_notes=data.get('family_notes'),
            admin_notes=data.get('admin_notes'),
            status=data.get('status', 'confirmed'),
            is_public=data.get('is_public', True),
            is_urgent=data.get('is_urgent', False),
            reported_by=current_user.id
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'message': 'Janazah event created successfully',
            'event': {
                'id': event.id,
                'deceased_name': event.deceased_name,
                'deceased_age': event.deceased_age,
                'deceased_gender': event.deceased_gender,
                'deceased_date': event.deceased_date.isoformat() if event.deceased_date else None,
                'prayer_date': event.prayer_date.isoformat() if event.prayer_date else None,
                'prayer_time': event.prayer_time.strftime('%H:%M') if event.prayer_time else None,
                'mosque_id': event.mosque_id,
                'burial_location': event.burial_location,
                'burial_time': event.burial_time.strftime('%H:%M') if event.burial_time else None,
                'contact_person': event.contact_person,
                'contact_phone': event.contact_phone,
                'contact_email': event.contact_email,
                'family_notes': event.family_notes,
                'status': event.status,
                'is_public': event.is_public,
                'is_urgent': event.is_urgent,
                'reported_by': event.reported_by
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/janazah/<int:event_id>', methods=['PUT'])
@login_required
def update_janazah_event(event_id):
    """Update a janazah event"""
    try:
        event = JanazahEvent.query.get_or_404(event_id)
        
        # Check if user is reporter, admin, or mosque admin
        if (current_user.id != event.reported_by and 
            current_user.role != 'admin' and 
            current_user.role != 'mosque_admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'deceased_name' in data:
            event.deceased_name = data['deceased_name']
        if 'deceased_age' in data:
            event.deceased_age = data['deceased_age']
        if 'deceased_gender' in data:
            event.deceased_gender = data['deceased_gender']
        if 'deceased_date' in data:
            event.deceased_date = datetime.strptime(data['deceased_date'], '%Y-%m-%d').date()
        if 'prayer_date' in data:
            event.prayer_date = datetime.strptime(data['prayer_date'], '%Y-%m-%d').date()
        if 'prayer_time' in data:
            event.prayer_time = datetime.strptime(data['prayer_time'], '%H:%M').time()
        if 'mosque_id' in data:
            event.mosque_id = data['mosque_id']
        if 'burial_location' in data:
            event.burial_location = data['burial_location']
        if 'burial_time' in data:
            event.burial_time = datetime.strptime(data['burial_time'], '%H:%M').time() if data['burial_time'] else None
        if 'contact_person' in data:
            event.contact_person = data['contact_person']
        if 'contact_phone' in data:
            event.contact_phone = data['contact_phone']
        if 'contact_email' in data:
            event.contact_email = data['contact_email']
        if 'family_notes' in data:
            event.family_notes = data['family_notes']
        if 'admin_notes' in data:
            event.admin_notes = data['admin_notes']
        if 'status' in data:
            event.status = data['status']
        if 'is_public' in data:
            event.is_public = data['is_public']
        if 'is_urgent' in data:
            event.is_urgent = data['is_urgent']
        
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Janazah event updated successfully',
            'event': {
                'id': event.id,
                'deceased_name': event.deceased_name,
                'deceased_age': event.deceased_age,
                'deceased_gender': event.deceased_gender,
                'deceased_date': event.deceased_date.isoformat() if event.deceased_date else None,
                'prayer_date': event.prayer_date.isoformat() if event.prayer_date else None,
                'prayer_time': event.prayer_time.strftime('%H:%M') if event.prayer_time else None,
                'mosque_id': event.mosque_id,
                'burial_location': event.burial_location,
                'burial_time': event.burial_time.strftime('%H:%M') if event.burial_time else None,
                'contact_person': event.contact_person,
                'contact_phone': event.contact_phone,
                'contact_email': event.contact_email,
                'family_notes': event.family_notes,
                'admin_notes': event.admin_notes,
                'status': event.status,
                'is_public': event.is_public,
                'is_urgent': event.is_urgent,
                'updated_at': event.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/janazah/<int:event_id>', methods=['DELETE'])
@login_required
def delete_janazah_event(event_id):
    """Delete a janazah event"""
    try:
        event = JanazahEvent.query.get_or_404(event_id)
        
        # Check if user is reporter, admin, or mosque admin
        if (current_user.id != event.reported_by and 
            current_user.role != 'admin' and 
            current_user.role != 'mosque_admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({'message': 'Janazah event deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/janazah/stats', methods=['GET'])
@login_required
def get_janazah_stats():
    """Get janazah statistics (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get statistics
        total_events = JanazahEvent.query.count()
        pending_events = JanazahEvent.query.filter_by(status='pending').count()
        confirmed_events = JanazahEvent.query.filter_by(status='confirmed').count()
        completed_events = JanazahEvent.query.filter_by(status='completed').count()
        urgent_events = JanazahEvent.query.filter_by(is_urgent=True).count()
        
        # Get events by mosque
        events_by_mosque = db.session.query(
            Mosque.name,
            db.func.count(JanazahEvent.id)
        ).join(JanazahEvent).group_by(Mosque.id, Mosque.name).all()
        
        # Get events by status
        events_by_status = db.session.query(
            JanazahEvent.status,
            db.func.count(JanazahEvent.id)
        ).group_by(JanazahEvent.status).all()
        
        return jsonify({
            'stats': {
                'total_events': total_events,
                'pending_events': pending_events,
                'confirmed_events': confirmed_events,
                'completed_events': completed_events,
                'urgent_events': urgent_events
            },
            'by_mosque': {item[0]: item[1] for item in events_by_mosque},
            'by_status': {item[0]: item[1] for item in events_by_status}
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Management API Endpoints

@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    """Get all users (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get query parameters
        role = request.args.get('role')
        mosque_id = request.args.get('mosque_id', type=int)
        is_active = request.args.get('is_active')
        email_verified = request.args.get('email_verified')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        if mosque_id:
            query = query.filter_by(mosque_id=mosque_id)
        if is_active:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        if email_verified:
            query = query.filter_by(email_verified=email_verified.lower() == 'true')
        
        # Order by created_at desc
        query = query.order_by(User.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        users = query.all()
        
        return jsonify({
            'users': [{
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'role': user.role,
                'mosque': {
                    'id': user.mosque.id,
                    'name': user.mosque.name,
                    'address': user.mosque.address
                } if user.mosque else None,
                'is_active': user.is_active,
                'email_verified': user.email_verified,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            } for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get a specific user by ID"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Check if user can view this profile
        if (current_user.id != user.id and 
            current_user.role != 'admin' and 
            current_user.role != 'mosque_admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'role': user.role,
                'mosque': {
                    'id': user.mosque.id,
                    'name': user.mosque.name,
                    'address': user.mosque.address
                } if user.mosque else None,
                'is_active': user.is_active,
                'email_verified': user.email_verified,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """Update a user profile"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Check if user can update this profile
        if (current_user.id != user.id and 
            current_user.role != 'admin' and 
            current_user.role != 'mosque_admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'email' in data and data['email'] != user.email:
            # Check if email is already taken
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': 'Email already exists'}), 400
            user.email = data['email']
            user.email_verified = False  # Reset verification if email changed
        
        # Admin-only fields
        if current_user.role == 'admin':
            if 'role' in data:
                user.role = data['role']
            if 'mosque_id' in data:
                user.mosque_id = data['mosque_id']
            if 'is_active' in data:
                user.is_active = data['is_active']
            if 'email_verified' in data:
                user.email_verified = data['email_verified']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'role': user.role,
                'mosque_id': user.mosque_id,
                'is_active': user.is_active,
                'email_verified': user.email_verified,
                'updated_at': user.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        user = User.query.get_or_404(user_id)
        
        # Prevent admin from deleting themselves
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/change-password', methods=['POST'])
@login_required
def change_user_password(user_id):
    """Change user password"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Check if user can change this password
        if (current_user.id != user.id and 
            current_user.role != 'admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('new_password'):
            return jsonify({'error': 'New password is required'}), 400
        
        # If not admin, require current password
        if current_user.id == user.id:
            if not data.get('current_password'):
                return jsonify({'error': 'Current password is required'}), 400
            
            # Verify current password
            if not check_password_hash(user.password_hash, data['current_password']):
                return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Update password
        user.password_hash = generate_password_hash(data['new_password'])
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get user statistics (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        verified_users = User.query.filter_by(email_verified=True).count()
        admin_users = User.query.filter_by(role='admin').count()
        mosque_admin_users = User.query.filter_by(role='mosque_admin').count()
        regular_users = User.query.filter_by(role='user').count()
        
        # Get users by mosque
        users_by_mosque = db.session.query(
            Mosque.name,
            db.func.count(User.id)
        ).join(User).group_by(Mosque.id, Mosque.name).all()
        
        # Get users by role
        users_by_role = db.session.query(
            User.role,
            db.func.count(User.id)
        ).group_by(User.role).all()
        
        # Get recent registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = User.query.filter(User.created_at >= thirty_days_ago).count()
        
        return jsonify({
            'stats': {
                'total_users': total_users,
                'active_users': active_users,
                'verified_users': verified_users,
                'admin_users': admin_users,
                'mosque_admin_users': mosque_admin_users,
                'regular_users': regular_users,
                'recent_registrations': recent_registrations
            },
            'by_mosque': {item[0]: item[1] for item in users_by_mosque},
            'by_role': {item[0]: item[1] for item in users_by_role}
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/mosque', methods=['POST'])
@login_required
def assign_user_to_mosque(user_id):
    """Assign user to a mosque (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data.get('mosque_id'):
            return jsonify({'error': 'mosque_id is required'}), 400
        
        mosque = Mosque.query.get_or_404(data['mosque_id'])
        
        user.mosque_id = mosque.id
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'User assigned to mosque successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'mosque': {
                    'id': mosque.id,
                    'name': mosque.name,
                    'address': mosque.address
                }
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/role', methods=['POST'])
@login_required
def change_user_role(user_id):
    """Change user role (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data.get('role'):
            return jsonify({'error': 'role is required'}), 400
        
        valid_roles = ['user', 'mosque_admin', 'admin']
        if data['role'] not in valid_roles:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Prevent admin from changing their own role
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot change your own role'}), 400
        
        user.role = data['role']
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'User role changed successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Always serve on port 5001
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)