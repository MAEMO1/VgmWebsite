import os
import logging
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
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
    app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_123")

    # Configure PostgreSQL database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
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

    # Configure login manager
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Log in om deze pagina te bekijken.'
    login_manager.login_message_category = 'info'

    with app.app_context():
        # Import routes after app context is created
        from routes import routes as main_routes
        from routes.event_routes import events
        from routes.obituary_routes import obituaries
        from routes.blog_routes import blog
        from routes.translation_routes import translation_bp
        from routes.message_routes import messages
        from routes.donation_routes import donations

        # Register blueprints
        app.register_blueprint(main_routes)
        app.register_blueprint(events, url_prefix='/events')
        app.register_blueprint(obituaries, url_prefix='/obituaries')
        app.register_blueprint(blog, url_prefix='/blog')
        app.register_blueprint(translation_bp)
        app.register_blueprint(messages, url_prefix='/messages')
        app.register_blueprint(donations)

        try:
            # Import models and create tables
            from models import User, Event, EventRegistration, EventNotification, PrayerTime, Obituary, ObituaryNotification, BlogPost, Message, FundraisingCampaign
            db.create_all()
            logger.info("Database tables created successfully")

            # Initialize mosques data
            from routes.routes import initialize_mosques
            initialize_mosques()
            logger.info("Mosques initialized successfully")

        except Exception as e:
            logger.error(f"Error during app initialization: {e}")
            raise

        return app

# Create the application instance
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