import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask-SQLAlchemy with model class
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

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

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    with app.app_context():
        # Import routes after app context is created
        from routes import routes as main_routes
        from routes.event_routes import events

        # Register blueprints
        app.register_blueprint(main_routes)
        app.register_blueprint(events, url_prefix='/events')

        # Import models to ensure they're registered with SQLAlchemy
        from models import User, Event, EventRegistration, EventNotification, PrayerTime, Obituary
        db.create_all()
        logging.info("Database tables created successfully")

        return app

# Create the application instance
app = create_app()

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))