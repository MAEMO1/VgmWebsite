import os
from flask import Flask, redirect, url_for
from extensions import db, babel, logger

def create_app():
    # Create Flask app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
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

    # Add test route
    @app.route('/test')
    def test():
        logger.debug("Handling test route")
        try:
            # Test database connection
            with db.engine.connect() as conn:
                logger.info("Database connection successful")
            return 'Flask app and database are working!'
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return 'Flask app is working, but database connection failed!', 500

    with app.app_context():
        # Import models
        import models

        # Create database tables
        db.create_all()
        logger.info("Database tables created successfully")

        # Register blueprints
        from routes.ramadan_routes import ramadan
        app.register_blueprint(ramadan, url_prefix='/ramadan')

        # Add default route
        @app.route('/')
        def home():
            logger.debug("Handling home route")
            return redirect(url_for('ramadan.iftar_map'))

    return app

# Create application instance
app = create_app()

if __name__ == "__main__":
    logger.info("Starting Flask app")
    app.run(host="0.0.0.0", port=5000, debug=True)