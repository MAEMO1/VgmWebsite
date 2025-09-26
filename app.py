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
    db = SQLAlchemy(app)
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
    
    # CSRF token endpoint
    @app.route('/api/csrf', methods=['GET'])
    def get_csrf_token():
        """Generate and return CSRF token for frontend"""
        csrf_token = secrets.token_urlsafe(32)
        session['csrf_token'] = csrf_token
        return jsonify({'csrf_token': csrf_token}), 200
    
    # CSRF protection middleware
    @app.before_request
    def csrf_protect():
        """Protect against CSRF attacks for state-changing requests"""
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Skip CSRF check for certain endpoints
            if request.endpoint in ['get_csrf_token', 'health', 'database_health_check']:
                return
            
            # Check CSRF token
            csrf_token = request.headers.get('X-CSRF-Token')
            session_token = session.get('csrf_token')
            
            if not csrf_token or not session_token or csrf_token != session_token:
                return jsonify({'error': 'Invalid CSRF token'}), 403
    
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
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Don't crash the app, just log the error
        pass

# Try to initialize database, but don't crash if it fails
# Comment out for now to allow app to start
# init_database()

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