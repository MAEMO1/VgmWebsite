import os
import logging
from flask import Flask, redirect, url_for
from extensions import db, login_manager, babel

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

    # Configure login
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Log in om deze pagina te bekijken.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    # Register routes
    @app.route('/')
    def home():
        return redirect(url_for('main.index'))

    @app.route('/test')
    def test():
        return 'De applicatie werkt!'

    # Import and register blueprints
    from routes import routes as main_routes
    app.register_blueprint(main_routes)

    return app

# Create the application instance
app = create_app()

# Initialize database tables
with app.app_context():
    from models import User
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)