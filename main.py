import os
import logging
from flask import Flask, render_template, request
from extensions import db, babel, logger
from flask_babel import _

# create the app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure database with SQLite fallback
database_url = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'nl'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Amsterdam'

# Initialize extensions
db.init_app(app)
babel.init_app(app)

# Make the translation function available in templates
@app.context_processor
def utility_processor():
    return {'_': _}

@app.route('/')
def home():
    logger.debug("Handling home route")
    try:
        return render_template('base.html', content="Welcome to VGM!")
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        return "Error loading home page", 500

@app.route('/test')
def test():
    logger.debug("Handling test route")
    try:
        # Test database connection
        with db.engine.connect() as conn:
            logger.info("Database connection successful")
        return render_template('base.html', 
                             content="Database connection successful!")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return render_template('base.html',
                             content="Database connection failed!"), 500

# Temporarily comment out blueprint registration until we fix the model issues
"""
try:
    from routes.ramadan_routes import ramadan
    app.register_blueprint(ramadan, url_prefix='/ramadan')
    logger.info("Successfully registered ramadan blueprint")
except Exception as e:
    logger.error(f"Failed to register ramadan blueprint: {e}")
"""

if __name__ == "__main__":
    logger.info("Starting Flask application")
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)