from datetime import datetime, date, time
from flask_login import UserMixin
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    user_type = db.Column(db.String(20), nullable=False)  # 'visitor' or 'mosque'
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Mosque-specific fields
    mosque_name = db.Column(db.String(200))
    mosque_street = db.Column(db.String(100))
    mosque_number = db.Column(db.String(10))
    mosque_postal = db.Column(db.String(10))
    mosque_city = db.Column(db.String(100))
    mosque_phone = db.Column(db.String(20))
    mosque_email = db.Column(db.String(120))
    mosque_website = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # Additional information fields
    mission_statement = db.Column(db.Text)
    vision_statement = db.Column(db.Text)
    activities = db.Column(db.Text)
    facilities = db.Column(db.Text)
    languages = db.Column(db.String(200))
    accessibility_features = db.Column(db.Text)

    def get_full_address(self):
        if self.user_type == 'mosque':
            return f"{self.mosque_street} {self.mosque_number}, {self.mosque_postal} {self.mosque_city}"
        return None