import os
import logging
from flask import Flask, redirect, url_for
from extensions import db, login_manager, babel, migrate

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Configure secret key
    app.secret_key = os.environ.get("SESSION_SECRET")

    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300
    }

    # Configure babel
    app.config['BABEL_DEFAULT_LOCALE'] = 'nl'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Amsterdam'

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate

    # Configure login
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Log in om deze pagina te bekijken.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    with app.app_context():
        # Import routes
        from routes.main_routes import main
        from routes.event_routes import events
        from routes.auth_routes import auth
        from routes.blog_routes import blog
        from routes.donation_routes import donations

        # Register blueprints
        app.register_blueprint(main)
        app.register_blueprint(events)
        app.register_blueprint(auth)
        app.register_blueprint(blog)
        app.register_blueprint(donations)

        # Create database tables if they don't exist
        db.create_all()

    return app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)