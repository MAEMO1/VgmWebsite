import os
import logging
from flask import Flask, redirect, url_for

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

logger.info("Flask app created")

# Add test routes
@app.route('/')
def home():
    logger.debug("Handling home route")
    return redirect(url_for('test'))

@app.route('/test')
def test():
    logger.debug("Handling test route")
    return 'Flask app is working!'

if __name__ == "__main__":
    try:
        logger.info("Starting Flask app")
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        logger.exception("Error while running the Flask server:")
        raise