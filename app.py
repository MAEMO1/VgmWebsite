import os
import logging
from flask import Flask, request, session, redirect, url_for
from extensions import db, login_manager, babel

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_locale():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(['en', 'nl', 'ar'])

# Create Flask app
app = Flask(__name__)

try:
    # Configure secret key
    if not os.environ.get("SESSION_SECRET"):
        logger.warning("SESSION_SECRET not set, using a default value")
        app.secret_key = "default-secret-key"
    else:
        app.secret_key = os.environ.get("SESSION_SECRET")
        logger.info("Session secret key configured successfully")

    # Configure PostgreSQL database
    logger.debug("Database URL: %s", os.environ.get("DATABASE_URL", "Not set"))
    if not os.environ.get("DATABASE_URL"):
        logger.error("DATABASE_URL environment variable is not set")
        raise ValueError("DATABASE_URL must be set")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    logger.info("Database configuration completed")

    # Configure Babel
    app.config['BABEL_DEFAULT_LOCALE'] = 'nl'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'nl', 'ar']
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Amsterdam'
    logger.info("Babel configuration completed")

    # Initialize extensions
    try:
        db.init_app(app)
        logger.info("SQLAlchemy initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize SQLAlchemy: {e}", exc_info=True)
        raise

    try:
        login_manager.init_app(app)
        logger.info("Login manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize login manager: {e}", exc_info=True)
        raise

    try:
        babel.init_app(app, locale_selector=get_locale)
        logger.info("Babel initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Babel: {e}", exc_info=True)
        raise

    # Configure login manager
    login_manager.login_view = 'ramadan.index'
    login_manager.login_message = 'Log in om deze pagina te bekijken.'
    login_manager.login_message_category = 'info'

    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        try:
            from models import User
            return User.query.get(int(user_id))
        except Exception as e:
            logger.error(f"Error in user loader: {e}", exc_info=True)
            return None

    with app.app_context():
        try:
            # Import models here so they are registered with SQLAlchemy
            import models
            logger.info("Models imported successfully")
        except Exception as e:
            logger.error(f"Failed to import models: {e}", exc_info=True)
            raise

        try:
            # Create all database tables
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}", exc_info=True)
            raise

        try:
            # Register blueprints
            from routes.ramadan_routes import ramadan
            app.register_blueprint(ramadan, url_prefix='/ramadan')
            logger.info("Blueprints registered successfully")
        except Exception as e:
            logger.error(f"Failed to register blueprints: {e}", exc_info=True)
            raise

        # Add default route
        @app.route('/')
        def home():
            logger.debug("Home route accessed, redirecting to ramadan.index")
            return redirect(url_for('ramadan.index'))

except Exception as e:
    logger.error(f"Failed to initialize application: {e}", exc_info=True)
    raise

if __name__ == "__main__":
    # Always serve on port 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)