import os
import logging
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask-SQLAlchemy with model class
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
babel = Babel()

def get_locale():
    # Try to get language from the session
    if 'language' in session:
        return session['language']
    # Otherwise try to guess the language from the user accept header
    return request.accept_languages.best_match(['en', 'nl', 'ar'])

def create_app():
    # Create Flask app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_123")  # Default for development

    # Configure PostgreSQL database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Configure Babel
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'nl', 'ar']
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    login_manager.login_view = 'login'

    with app.app_context():
        # Import routes after app context is created
        from routes import routes as main_routes
        from routes.event_routes import events
        from routes.obituary_routes import obituaries
        from routes.blog_routes import blog
        from routes.translation_routes import translation_bp  # Add translation routes

        # Register blueprints
        app.register_blueprint(main_routes)
        app.register_blueprint(events, url_prefix='/events')
        app.register_blueprint(obituaries, url_prefix='/obituaries')
        app.register_blueprint(blog, url_prefix='/blog')
        app.register_blueprint(translation_bp)  # Register translation blueprint

        # Import models to ensure they're registered with SQLAlchemy
        from models import User, Event, EventRegistration, EventNotification, PrayerTime, Obituary, ObituaryNotification, BlogPost
        db.create_all()
        logging.info("Database tables created successfully")

        # Initialize mosques data
        from routes.routes import initialize_mosques
        initialize_mosques()
        logging.info("Mosques initialized successfully")

        return app

# Create the application instance
app = create_app()

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))