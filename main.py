import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from flask_babel import Babel

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
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['BABEL_DEFAULT_LOCALE'] = 'nl'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Amsterdam'

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
babel.init_app(app)

# Setup login manager
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models here so they are registered with SQLAlchemy
    import models  # noqa: F401
    # Create all database tables
    db.create_all()

# Register blueprints
from routes.ramadan_routes import ramadan
app.register_blueprint(ramadan, url_prefix='/ramadan')

# Add default route
@app.route('/')
def home():
    return redirect(url_for('ramadan.iftar_map'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)