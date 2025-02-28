import os
from flask import Flask
from extensions import db, logger

app = Flask(__name__)
# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
# Initialize extensions
db.init_app(app)

@app.route('/')
def home():
    logger.debug("Handling home route")
    return 'Welcome to VGM Iftar Map!'

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)