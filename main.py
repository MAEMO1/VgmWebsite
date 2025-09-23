import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from flask_babel import Babel
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
babel = Babel()

# Create the app
app = Flask(__name__)

# Configure the app
app.secret_key = os.environ.get("SESSION_SECRET")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,  # Enable connection health checks
    "pool_recycle": 300,    # Recycle connections every 5 minutes
    "pool_timeout": 30,     # Connection timeout after 30 seconds
    "pool_size": 20,        # Maximum number of connections
    "max_overflow": 5       # Allow 5 connections above pool_size when needed
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'nl'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'nl', 'ar']
app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Amsterdam'

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)

def get_locale():
    from flask import request, session
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(['en', 'nl', 'ar'])

babel.init_app(app, locale_selector=get_locale)

# Setup login manager
login_manager.login_view = 'main.login'
login_manager.login_message = 'Log in om deze pagina te bekijken.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    try:
        # Import models to register with SQLAlchemy
        from models import User, Event, EventRegistration, EventNotification, PrayerTime, Obituary, ObituaryNotification, BlogPost, Message, FundraisingCampaign
        # Create all database tables
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}", exc_info=True)
        logger.error("Stack trace:", exc_info=True)

    try:
        # Import routes after app context is created
        from routes import routes as main_routes
        from routes.event_routes import events
        from routes.obituary_routes import obituaries
        from routes.blog_routes import blog
        from routes.translation_routes import translation_bp
        from routes.message_routes import messages
        from routes.donation_routes import donations
        from routes.ramadan_routes import ramadan

        # Register blueprints
        app.register_blueprint(main_routes)
        app.register_blueprint(events, url_prefix='/events')
        app.register_blueprint(obituaries, url_prefix='/obituaries')
        app.register_blueprint(blog, url_prefix='/blog')
        app.register_blueprint(translation_bp)
        app.register_blueprint(messages, url_prefix='/messages')
        app.register_blueprint(donations)
        app.register_blueprint(ramadan, url_prefix='/ramadan')
    except Exception as e:
        logger.error(f"Error registering blueprints: {e}", exc_info=True)
        logger.error("Stack trace:", exc_info=True)

# Add default route
@app.route('/')
def home():
    return redirect(url_for('ramadan.iftar_map'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)