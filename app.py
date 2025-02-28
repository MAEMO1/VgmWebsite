import os
import logging
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask-SQLAlchemy with model class
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
babel = Babel()

def get_locale():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(['en', 'nl', 'ar'])

def create_app():
    # Create Flask app
    app = Flask(__name__)

    # Configure secret key
    app.secret_key = os.environ.get("SESSION_SECRET")

    # Configure PostgreSQL database with robust connection handling
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,  # Enable connection health checks
        "pool_recycle": 300,    # Recycle connections every 5 minutes
        "pool_timeout": 30,     # Connection timeout after 30 seconds
        "pool_size": 20,        # Maximum number of connections
        "max_overflow": 5       # Allow 5 connections above pool_size when needed
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Configure Babel
    app.config['BABEL_DEFAULT_LOCALE'] = 'nl'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'nl', 'ar']
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Amsterdam'

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    with app.app_context():
        # Import models to register with SQLAlchemy
        from models import User, IfterEvent, Event, EventRegistration, EventNotification, PrayerTime, Obituary, ObituaryNotification, BlogPost, Message, FundraisingCampaign

        # Create database tables
        db.create_all()

        # Register blueprints
        from routes import routes as main_routes
        from routes.event_routes import events
        from routes.obituary_routes import obituaries
        from routes.blog_routes import blog
        from routes.translation_routes import translation_bp
        from routes.message_routes import messages
        from routes.donation_routes import donations
        from routes.ramadan_routes import ramadan

        app.register_blueprint(main_routes)
        app.register_blueprint(events, url_prefix='/events')
        app.register_blueprint(obituaries, url_prefix='/obituaries')
        app.register_blueprint(blog, url_prefix='/blog')
        app.register_blueprint(translation_bp)
        app.register_blueprint(messages, url_prefix='/messages')
        app.register_blueprint(donations)
        app.register_blueprint(ramadan, url_prefix='/ramadan')


        # Add default route.  This should ideally be in routes.py but we'll add it here to make the edited code work.
        @app.route('/')
        def home():
            from flask import redirect, url_for
            return redirect(url_for('ramadan.iftar_map'))


    return app

# Create application instance
app = create_app()

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

if __name__ == "__main__":
    # Always serve on port 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)