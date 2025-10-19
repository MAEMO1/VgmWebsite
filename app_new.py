#!/usr/bin/env python3
"""
VGM Website - Enhanced Backend with SQLAlchemy ORM
Production-ready implementation with PostgreSQL support
"""

import os
import logging
import secrets
import hashlib
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session, send_from_directory, g
from flask_cors import CORS
from werkzeug.utils import secure_filename
import jwt
import stripe
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

# Import our models
from models_new import db, User, Mosque, Event, BlogPost, MediaFile, Donation, FundraisingCampaign, PrayerTime

# Import structured logging
from logging_config import (
    get_logger, log_request_start, log_request_end, log_error, 
    log_security_event, log_business_event, log_performance
)

# Import Sentry for error tracking
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Import caching service
from cache_service import (
    cache, cache_mosques_list, get_cached_mosques_list, 
    cache_mosque_detail, get_cached_mosque_detail,
    invalidate_mosque_cache, invalidate_events_cache, invalidate_news_cache
)

def create_app():
    """Create Flask application with SQLAlchemy ORM"""
    app = Flask(__name__)
    
    # Initialize Sentry for error tracking
    sentry_dsn = os.environ.get('SENTRY_DSN')
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1,
            environment=os.environ.get('FLASK_ENV', 'development'),
        )
    
    # Configure secret key for sessions
    app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    
    # JWT Secret Key
    JWT_SECRET = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/vgm_website.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Initialize Rate Limiting
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    limiter.init_app(app)
    
    # Request logging middleware
    @app.before_request
    def before_request():
        log_request_start()
    
    @app.after_request
    def after_request(response):
        g.status_code = response.status_code
        log_request_end()
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        log_error(e, {
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr
        })
        return jsonify({'error': 'Internal server error'}), 500
    
    # Stripe configuration
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_...')
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Configure CORS properly
    default_origins = [
        'http://localhost:3000',
        'http://localhost:3001',
        'https://vgm-website.vercel.app',
        'https://frontend-maemo.vercel.app'
    ]
    cors_origins = os.environ.get('ALLOWED_ORIGINS', ','.join(default_origins)).split(',')
    cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

    CORS(
        app,
        origins=cors_origins,
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization', 'X-CSRF-Token'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    )
    
    # Helper functions
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def get_file_size(file):
        """Get file size in bytes"""
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Seek back to beginning
        return size
    
    def generate_jwt_token(user_id, role, token_type='access'):
        """Generate JWT token"""
        if token_type == 'access':
            exp_time = datetime.utcnow() + timedelta(minutes=15)  # Short-lived access token
        else:  # refresh token
            exp_time = datetime.utcnow() + timedelta(days=7)  # Long-lived refresh token
            
        payload = {
            'user_id': user_id,
            'role': role,
            'token_type': token_type,
            'exp': exp_time,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    
    def verify_jwt_token(token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    # Authentication middleware
    def require_auth(f):
        """Decorator to require authentication"""
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'No token provided'}), 401
            
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = verify_jwt_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Get user from database
            user = User.query.get(payload['user_id'])
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            request.user = user
            request.user_id = payload['user_id']
            request.user_role = payload['role']
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    # RBAC decorator using the proper RBAC engine
    def require_capability(capability, scope=None):
        """Decorator to require specific capability using RBAC engine"""
        def decorator(f):
            def decorated_function(*args, **kwargs):
                from rbac.rbac import has_capability
                
                # Extract mosque_id from kwargs if needed for scoped capabilities
                mosque_id = kwargs.get('mosque_id') if scope == 'own' else None
                
                if not has_capability(request.user, capability, mosque_id):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                return f(*args, **kwargs)
            decorated_function.__name__ = f.__name__
            return decorated_function
        return decorator
    
    # API Routes
    
    def check_database():
        """Check database connectivity"""
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            return True
        except Exception as e:
            log_error(e, {'check': 'database'})
            return False
    
    def check_stripe():
        """Check Stripe API connectivity"""
        try:
            stripe.Account.retrieve()
            return True
        except Exception as e:
            log_error(e, {'check': 'stripe'})
            return False
    
    def check_redis():
        """Check Redis connectivity (if configured)"""
        try:
            redis_url = os.environ.get('REDIS_URL')
            if not redis_url:
                return True  # Redis not required
            
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            return True
        except Exception as e:
            log_error(e, {'check': 'redis'})
            return False
    
    @app.route('/health')
    def health():
        """Basic health check endpoint"""
        return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})
    
    @app.route('/health/ready')
    def health_ready():
        """Readiness probe - checks if app is ready to serve traffic"""
        checks = {
            'database': check_database(),
            'stripe': check_stripe(),
            'redis': check_redis(),
        }
        
        all_healthy = all(checks.values())
        status = 'ready' if all_healthy else 'not_ready'
        
        response_data = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'checks': checks
        }
        
        status_code = 200 if all_healthy else 503
        
        if not all_healthy:
            log_error(Exception("Health check failed"), {'checks': checks})
        
        return jsonify(response_data), status_code
    
    @app.route('/health/live')
    def health_live():
        """Liveness probe - checks if app is alive"""
        return jsonify({'status': 'alive', 'timestamp': datetime.now().isoformat()})
    
    @app.route('/api/csrf', methods=['GET'])
    def get_csrf_token():
        """Get CSRF token for forms"""
        from flask_wtf.csrf import generate_csrf
        return jsonify({'csrf_token': generate_csrf()})
    
    # Authentication endpoints
    @app.route('/api/auth/login', methods=['POST'])
    @limiter.limit("5 per minute")
    def login():
        """User login endpoint"""
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({'error': 'Email and password required'}), 400
            
            # Find user by email
            user = User.query.filter_by(email=email).first()
            
            if not user or not user.check_password(password):
                log_security_event('login_failed', {
                    'email': email,
                    'reason': 'invalid_credentials',
                    'remote_addr': request.remote_addr
                })
                return jsonify({'error': 'Invalid credentials'}), 401
            
            if not user.is_active:
                log_security_event('login_failed', {
                    'email': email,
                    'reason': 'account_inactive',
                    'remote_addr': request.remote_addr
                })
                return jsonify({'error': 'Account is inactive'}), 401
            
            # Generate JWT tokens
            access_token = generate_jwt_token(user.id, user.role, 'access')
            refresh_token = generate_jwt_token(user.id, user.role, 'refresh')
            
            log_business_event('user_login', {
                'user_id': user.id,
                'email': user.email,
                'role': user.role
            })
            
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            })
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return jsonify({'error': 'Login failed'}), 500
    
    @app.route('/api/auth/refresh', methods=['POST'])
    def refresh_token():
        """Refresh access token using refresh token"""
        try:
            data = request.get_json()
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return jsonify({'error': 'Refresh token required'}), 400
            
            payload = verify_jwt_token(refresh_token)
            if not payload or payload.get('token_type') != 'refresh':
                return jsonify({'error': 'Invalid refresh token'}), 401
            
            # Get user from database
            user = User.query.get(payload['user_id'])
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            # Generate new access token
            new_access_token = generate_jwt_token(user.id, user.role, 'access')
            
            return jsonify({
                'access_token': new_access_token,
                'user': user.to_dict()
            })
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return jsonify({'error': 'Token refresh failed'}), 500
    
    @app.route('/api/auth/register', methods=['POST'])
    @limiter.limit("3 per minute")
    def register():
        """User registration endpoint"""
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            phone = data.get('phone')
            
            if not all([email, password, first_name, last_name]):
                return jsonify({'error': 'All required fields must be provided'}), 400
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'error': 'User already exists'}), 409
            
            # Create new user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='LID'  # Default role
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Generate JWT token
            token = generate_jwt_token(user.id, user.role)
            
            return jsonify({
                'token': token,
                'user': user.to_dict()
            }), 201
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            db.session.rollback()
            return jsonify({'error': 'Registration failed'}), 500
    
    # Payment endpoints
    @app.route('/api/payments/create-payment-intent', methods=['POST'])
    def create_payment_intent():
        """Create Stripe payment intent"""
        try:
            data = request.get_json()
            amount = data.get('amount')
            currency = data.get('currency', 'eur')
            donation_type = data.get('donation_type', 'general')
            mosque_id = data.get('mosque_id')
            campaign_id = data.get('campaign_id')
            
            if not amount or amount <= 0:
                return jsonify({'error': 'Valid amount required'}), 400
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                metadata={
                    'donation_type': donation_type,
                    'mosque_id': str(mosque_id) if mosque_id else '',
                    'campaign_id': str(campaign_id) if campaign_id else ''
                }
            )
            
            return jsonify({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            })
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return jsonify({'error': 'Payment processing failed'}), 500
        except Exception as e:
            logger.error(f"Payment intent error: {e}")
            return jsonify({'error': 'Payment processing failed'}), 500
    
    @app.route('/api/webhooks/stripe', methods=['POST'])
    def stripe_webhook():
        """Handle Stripe webhooks with signature verification"""
        try:
            payload = request.get_data()
            sig_header = request.headers.get('Stripe-Signature')
            webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
            
            if not webhook_secret:
                logger.error("Stripe webhook secret not configured")
                return jsonify({'error': 'Webhook not configured'}), 500
            
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            except ValueError as e:
                logger.error(f"Invalid payload: {e}")
                return jsonify({'error': 'Invalid payload'}), 400
            except stripe.error.SignatureVerificationError as e:
                logger.error(f"Invalid signature: {e}")
                return jsonify({'error': 'Invalid signature'}), 400
            
            # Handle the event
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                logger.info(f"Payment succeeded: {payment_intent['id']}")
                
                # Update donation status in database
                # This would typically update a donation record
                # based on the payment_intent metadata
                
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                logger.info(f"Payment failed: {payment_intent['id']}")
                
            else:
                logger.info(f"Unhandled event type: {event['type']}")
            
            return jsonify({'status': 'success'})
            
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return jsonify({'error': 'Webhook processing failed'}), 500
    
    # Mosques endpoints
    @app.route('/api/mosques', methods=['GET'])
    def get_mosques():
        """Get all active mosques"""
        try:
            # Try to get from cache first
            cached_mosques = get_cached_mosques_list()
            if cached_mosques:
                return jsonify(cached_mosques)
            
            # Fetch from database
            mosques = Mosque.query.filter_by(is_active=True).order_by(Mosque.name).all()
            mosques_data = [mosque.to_dict() for mosque in mosques]
            
            # Cache the result
            cache_mosques_list(mosques_data)
            
            return jsonify(mosques_data)
        except Exception as e:
            log_error(e, {'endpoint': 'get_mosques'})
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/mosques/<int:mosque_id>', methods=['GET'])
    def get_mosque(mosque_id):
        """Get specific mosque"""
        try:
            mosque = Mosque.query.get_or_404(mosque_id)
            if not mosque.is_active:
                return jsonify({'error': 'Mosque not found'}), 404
            return jsonify(mosque.to_dict())
        except Exception as e:
            logger.error(f"Error fetching mosque {mosque_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Events endpoints
    @app.route('/api/events', methods=['GET'])
    def get_events():
        """Get all active events"""
        try:
            events = Event.query.filter_by(is_active=True).order_by(Event.event_date, Event.event_time).all()
            return jsonify([event.to_dict() for event in events])
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return jsonify({'error': str(e)}), 500
    
    # News endpoints
    @app.route('/api/news', methods=['GET'])
    def get_news():
        """Get all published news"""
        try:
            news = BlogPost.query.filter_by(status='published').order_by(BlogPost.published_at.desc()).all()
            return jsonify([article.to_dict() for article in news])
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Analytics endpoints
    @app.route('/api/analytics/summary', methods=['GET'])
    @require_auth
    @require_capability('analytics.view_platform')
    def get_analytics_summary():
        """Get analytics summary"""
        try:
            # Mock analytics data - in production this would query actual analytics
            summary = {
                'total_users': User.query.count(),
                'total_mosques': Mosque.query.filter_by(is_active=True).count(),
                'total_events': Event.query.filter_by(is_active=True).count(),
                'total_donations': Donation.query.count(),
                'total_page_views': 0,  # Would be tracked separately
                'period_days': 30
            }
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/analytics/reports', methods=['GET'])
    @require_auth
    @require_capability('analytics.view_platform')
    def get_analytics_reports():
        """Get analytics reports"""
        try:
            report_type = request.args.get('type', 'overview')
            days = int(request.args.get('days', 30))
            
            if report_type == 'overview':
                report = {
                    'total_users': User.query.count(),
                    'total_mosques': Mosque.query.filter_by(is_active=True).count(),
                    'total_events': Event.query.filter_by(is_active=True).count(),
                    'total_donations': Donation.query.count(),
                    'total_page_views': 0,
                    'period_days': days
                }
            elif report_type == 'users':
                users = User.query.all()
                report = [user.to_dict() for user in users]
            elif report_type == 'mosques':
                mosques = Mosque.query.filter_by(is_active=True).all()
                report = [mosque.to_dict() for mosque in mosques]
            else:
                return jsonify({'error': 'Invalid report type'}), 400
            
            return jsonify(report)
        except Exception as e:
            logger.error(f"Error getting analytics reports: {e}")
            return jsonify({'error': str(e)}), 500
    
    # File upload endpoints
    @app.route('/api/upload', methods=['POST'])
    @require_auth
    @limiter.limit("10 per hour")
    def upload_file():
        """Upload a file"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'File type not allowed'}), 400
            
            # Get file info
            file_size = get_file_size(file)
            if file_size > MAX_CONTENT_LENGTH:
                return jsonify({'error': 'File too large'}), 400
            
            # Generate unique filename
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            secure_original_name = secure_filename(file.filename)
            
            # Save file
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            # Get additional data
            description = request.form.get('description', '')
            mosque_id = request.form.get('mosque_id')
            event_id = request.form.get('event_id')
            campaign_id = request.form.get('campaign_id')
            is_public = request.form.get('is_public', 'true').lower() == 'true'
            
            # Save file info to database
            media_file = MediaFile(
                filename=unique_filename,
                original_filename=secure_original_name,
                file_path=file_path,
                file_size=file_size,
                file_type=file_extension,
                mime_type=file.content_type,
                description=description,
                uploaded_by=request.user_id,
                mosque_id_ref=int(mosque_id) if mosque_id else None,
                event_id=int(event_id) if event_id else None,
                campaign_id=int(campaign_id) if campaign_id else None,
                is_public=is_public
            )
            
            db.session.add(media_file)
            db.session.commit()
            
            return jsonify({
                'id': media_file.id,
                'filename': media_file.filename,
                'original_filename': media_file.original_filename,
                'file_size': media_file.file_size,
                'file_type': media_file.file_type,
                'mime_type': media_file.mime_type,
                'description': media_file.description,
                'is_public': media_file.is_public,
                'created_at': media_file.created_at.isoformat() if media_file.created_at else None
            })
            
        except Exception as e:
            logger.error(f"Upload error: {e}")
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # Prayer times endpoints
    @app.route('/api/prayer-times', methods=['GET'])
    def get_prayer_times():
        """Get prayer times for a specific mosque and date"""
        try:
            mosque_id = request.args.get('mosque_id', type=int)
            date = request.args.get('date', datetime.now().date().isoformat())
            
            if not mosque_id:
                return jsonify({'error': 'Mosque ID required'}), 400
            
            # Try to get from cache first
            from cache_service import get_cached_prayer_times, cache_prayer_times
            cached_times = get_cached_prayer_times(mosque_id, date)
            if cached_times:
                return jsonify(cached_times)
            
            # Get from database
            prayer_time = PrayerTime.query.filter_by(
                mosque_id=mosque_id, 
                date=datetime.strptime(date, '%Y-%m-%d').date()
            ).first()
            
            if not prayer_time:
                # Calculate prayer times if not in database
                prayer_times = calculate_prayer_times(mosque_id, date)
                if prayer_times:
                    # Save to database
                    new_prayer_time = PrayerTime(
                        mosque_id=mosque_id,
                        date=datetime.strptime(date, '%Y-%m-%d').date(),
                        **prayer_times
                    )
                    db.session.add(new_prayer_time)
                    db.session.commit()
                    
                    # Cache the result
                    cache_prayer_times(mosque_id, date, prayer_times)
                    return jsonify(prayer_times)
                else:
                    return jsonify({'error': 'Prayer times not available'}), 404
            
            prayer_times = prayer_time.to_dict()
            cache_prayer_times(mosque_id, date, prayer_times)
            return jsonify(prayer_times)
            
        except Exception as e:
            log_error(e, {'endpoint': 'get_prayer_times'})
            return jsonify({'error': str(e)}), 500
    
    def calculate_prayer_times(mosque_id: int, date: str) -> dict:
        """Calculate prayer times for a mosque and date"""
        try:
            # Get mosque location
            mosque = Mosque.query.get(mosque_id)
            if not mosque or not mosque.latitude or not mosque.longitude:
                return None
            
            # Simple prayer time calculation (in production, use a proper library)
            # This is a simplified version - in production, use libraries like 'praytimes'
            latitude = float(mosque.latitude)
            longitude = float(mosque.longitude)
            
            # Basic calculation (this should be replaced with proper Islamic prayer time calculation)
            prayer_times = {
                'fajr': '05:30',
                'dhuhr': '12:30',
                'asr': '15:30',
                'maghrib': '18:30',
                'isha': '20:00'
            }
            
            return prayer_times
            
        except Exception as e:
            log_error(e, {'function': 'calculate_prayer_times'})
            return None
    
    # Advanced search endpoints
    @app.route('/api/search', methods=['GET'])
    def advanced_search():
        """Advanced search across all content types"""
        try:
            query = request.args.get('q', '')
            content_type = request.args.get('type', 'all')
            mosque_id = request.args.get('mosque_id')
            
            if not query:
                return jsonify({'error': 'Search query required'}), 400
            
            results = {
                'mosques': [],
                'events': [],
                'news': [],
                'total': 0
            }
            
            # Search mosques
            if content_type in ['all', 'mosques']:
                mosque_query = Mosque.query.filter(
                    Mosque.is_active == True,
                    Mosque.name.contains(query)
                )
                if mosque_id:
                    mosque_query = mosque_query.filter(Mosque.id == mosque_id)
                mosques = mosque_query.limit(10).all()
                results['mosques'] = [mosque.to_dict() for mosque in mosques]
            
            # Search events
            if content_type in ['all', 'events']:
                event_query = Event.query.filter(
                    Event.is_active == True,
                    Event.title.contains(query)
                )
                if mosque_id:
                    event_query = event_query.filter(Event.mosque_id == mosque_id)
                events = event_query.limit(10).all()
                results['events'] = [event.to_dict() for event in events]
            
            # Search news
            if content_type in ['all', 'news']:
                news_query = BlogPost.query.filter(
                    BlogPost.status == 'published',
                    BlogPost.title.contains(query)
                )
                news = news_query.limit(10).all()
                results['news'] = [article.to_dict() for article in news]
            
            results['total'] = len(results['mosques']) + len(results['events']) + len(results['news'])
            
            return jsonify(results)
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Create tables if they don't exist (for development)
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
