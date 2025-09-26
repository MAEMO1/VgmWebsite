import os
import logging
import secrets
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Time, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship

# Import models
from models import db, User, Mosque, Event, BlogPost, IfterEvent

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> Flask:
    """Create Flask application with proper structure"""
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
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    CORS(app)
    
    # Liveness endpoint – mag NOOIT de DB aanraken
    @app.route("/health")
    def health():
        return jsonify(status="ok"), 200
    
    # Optioneel: snelle rooktest
    @app.route("/")
    def index():
        return "VgmWebsite backend is up", 200
    
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

    # API Endpoints
    @app.route('/api/mosques', methods=['GET'])
    def get_mosques():
        """Get all active mosques"""
        try:
            mosques = Mosque.query.filter_by(is_active=True).all()
            return jsonify([{
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
            } for mosque in mosques]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/mosques/<int:mosque_id>', methods=['GET'])
    def get_mosque(mosque_id):
        """Get specific mosque by ID"""
        try:
            mosque = Mosque.query.get_or_404(mosque_id)
            return jsonify({
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
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/events', methods=['GET'])
    def get_events():
        """Get all active events"""
        try:
            events = Event.query.filter_by(is_active=True).all()
            return jsonify([{
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'event_date': event.start_date.isoformat() if event.start_date else None,
                'event_time': event.start_date.strftime('%H:%M') if event.start_date else None,
                'location': event.location,
                'mosque_id': event.mosque_id,
                'organizer_name': event.organizer_name,
                'max_participants': event.max_participants
            } for event in events]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/events/<int:event_id>', methods=['GET'])
    def get_event(event_id):
        """Get specific event by ID"""
        try:
            event = Event.query.get_or_404(event_id)
            return jsonify({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'event_date': event.start_date.isoformat() if event.start_date else None,
                'event_time': event.start_date.strftime('%H:%M') if event.start_date else None,
                'location': event.location,
                'mosque_id': event.mosque_id,
                'organizer_name': event.organizer_name,
                'max_participants': event.max_participants
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/news', methods=['GET'])
    def get_news():
        """Get all published news posts"""
        try:
            news_posts = BlogPost.query.filter_by(status='published').order_by(BlogPost.published_at.desc()).all()
            return jsonify([{
                'id': news.id,
                'title': news.title,
                'content': news.content,
                'excerpt': news.excerpt,
                'author_id': news.author_id,
                'published_at': news.published_at.isoformat() if news.published_at else None,
                'featured_image': news.featured_image,
                'tags': news.tags
            } for news in news_posts]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/news/<int:news_id>', methods=['GET'])
    def get_news_article(news_id):
        """Get specific news article by ID"""
        try:
            news = BlogPost.query.get_or_404(news_id)
            return jsonify({
                'id': news.id,
                'title': news.title,
                'content': news.content,
                'excerpt': news.excerpt,
                'author_id': news.author_id,
                'published_at': news.published_at.isoformat() if news.published_at else None,
                'featured_image': news.featured_image,
                'tags': news.tags
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/ramadan/iftar-events', methods=['GET'])
    def get_iftar_events():
        """Get all iftar events"""
        try:
            events = IfterEvent.query.all()
            return jsonify([{
                'id': event.id,
                'date': event.date.isoformat() if event.date else None,
                'time': event.time.strftime('%H:%M') if event.time else None,
                'mosque_id': event.mosque_id,
                'description': event.description,
                'capacity': event.capacity,
                'is_family_friendly': event.is_family_friendly
            } for event in events]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # CSRF token endpoint
    @app.route('/api/csrf', methods=['GET'])
    def get_csrf_token():
        """Generate and return CSRF token for frontend"""
        csrf_token = secrets.token_urlsafe(32)
        session['csrf_token'] = csrf_token
        return jsonify({'csrf_token': csrf_token}), 200
    
    # CSRF protection middleware - temporarily disabled for testing
    # @app.before_request
    # def csrf_protect():
    #     """Protect against CSRF attacks for state-changing requests"""
    #     if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
    #         # Skip CSRF check for certain endpoints
    #         if request.endpoint in ['get_csrf_token', 'health', 'database_health_check', 'index', 'get_mosques', 'get_mosque', 'get_events', 'get_event', 'get_news', 'get_news_article', 'get_iftar_events']:
    #             return
    #         
    #         # Check CSRF token
    #         csrf_token = request.headers.get('X-CSRF-Token')
    #         session_token = session.get('csrf_token')
    #         
    #         if not csrf_token or not session_token or csrf_token != session_token:
    #             return jsonify({'error': 'Invalid CSRF token'}), 403
    
    return app

# WSGI export voor gunicorn
app = create_app()

# Initialize database tables
def init_database():
    """Initialize database tables with error handling"""
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Add sample data if database is empty
            if User.query.count() == 0:
                # Create admin user
                admin_user = User(
                    email='admin@vgm.be',
                    password_hash=generate_password_hash('admin123'),
                    first_name='Admin',
                    last_name='VGM',
                    role='admin',
                    is_active=True,
                    email_verified=True
                )
                db.session.add(admin_user)
                
                # Create sample mosque
                sample_mosque = Mosque(
                    name='Centrale Moskee Gent',
                    address='Kortrijksesteenweg 123, 9000 Gent',
                    phone='+32 9 123 45 67',
                    email='info@centrale-moskee-gent.be',
                    capacity=500,
                    established_year=1985,
                    imam_name='Imam Ahmed',
                    description='De grootste moskee in Gent met uitgebreide faciliteiten.',
                    latitude=51.0543,
                    longitude=3.7174,
                    is_active=True
                )
                db.session.add(sample_mosque)
                
                # Create sample event
                sample_event = Event(
                    title='Vrijdaggebed',
                    description='Wekelijks vrijdaggebed met khutbah in het Nederlands.',
                    event_date=datetime.now().date(),
                    event_time=datetime.now().time(),
                    location='Centrale Moskee Gent',
                    mosque_id=1,
                    created_by=1,
                    is_active=True
                )
                db.session.add(sample_event)
                
                # Create sample news post
                sample_news = BlogPost(
                    title='Welkom bij VGM',
                    content='Welkom bij de Vereniging van Gentse Moskeeën. We zijn blij u te verwelkomen op onze nieuwe website.',
                    excerpt='Welkom bij de Vereniging van Gentse Moskeeën.',
                    author_id=1,
                    published_at=datetime.now(),
                    is_published=True
                )
                db.session.add(sample_news)
                
                db.session.commit()
                logger.info("Sample data created successfully")
                
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Don't crash the app, just log the error
        pass

# Initialize database when app starts
with app.app_context():
    init_database()

# JWT Secret Key
JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)