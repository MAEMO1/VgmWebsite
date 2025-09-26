#!/usr/bin/env python3
"""
VGM Website - Enhanced Backend with Payment Processing
P2 Implementation: Stripe Integration
"""

import os
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import jwt
import stripe

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask application with payment processing"""
    app = Flask(__name__)
    
    # Configure secret key for sessions
    app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    
    # JWT Secret Key
    JWT_SECRET = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))
    
    # Stripe configuration
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_...')
    
    # Configure CORS properly
    CORS(app, 
         origins=['http://localhost:3000', 'http://localhost:3001', 'https://vgm-website.vercel.app'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-CSRF-Token'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Database helper functions
    def get_db_connection():
        """Get database connection"""
        conn = sqlite3.connect('instance/vgm_website.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    def hash_password(password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(password, hashed):
        """Verify password against hash"""
        return hash_password(password) == hashed
    
    def generate_jwt_token(user_id, role):
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    
    def verify_jwt_token(token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def init_database():
        """Initialize database with payment tables"""
        conn = get_db_connection()
        
        # Create existing tables
        conn.execute('''
            CREATE TABLE IF NOT EXISTS mosques (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                website TEXT,
                capacity INTEGER,
                established_year INTEGER,
                imam_name TEXT,
                description TEXT,
                latitude REAL,
                longitude REAL,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                event_date DATE NOT NULL,
                event_time TIME NOT NULL,
                mosque_id INTEGER,
                event_type TEXT DEFAULT 'event',
                max_attendees INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_by INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mosque_id) REFERENCES mosques (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                excerpt TEXT,
                author_id INTEGER,
                published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'published',
                featured_image TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT,
                role TEXT DEFAULT 'user',
                mosque_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                email_verified BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mosque_id) REFERENCES mosques (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Payment tables
        conn.execute('''
            CREATE TABLE IF NOT EXISTS donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                donor_name TEXT NOT NULL,
                donor_email TEXT,
                donor_phone TEXT,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'EUR',
                donation_type TEXT DEFAULT 'general',
                mosque_id INTEGER,
                campaign_id INTEGER,
                stripe_payment_intent_id TEXT,
                status TEXT DEFAULT 'pending',
                payment_method TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mosque_id) REFERENCES mosques (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                mosque_id INTEGER,
                created_by INTEGER,
                status TEXT DEFAULT 'active',
                start_date DATE,
                end_date DATE,
                featured_image TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mosque_id) REFERENCES mosques (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS payment_methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                stripe_payment_method_id TEXT UNIQUE,
                card_brand TEXT,
                card_last_four TEXT,
                is_default BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Insert sample data if tables are empty
        if conn.execute('SELECT COUNT(*) FROM mosques').fetchone()[0] == 0:
            # Sample mosques
            mosques_data = [
                ('Moskee Salahaddien', 'Sint-Pietersnieuwstraat 120, 9000 Gent', '+32 9 123 45 67', 'info@salahaddien.be', 'www.salahaddien.be', 500, 1985, 'Sheikh Ahmed Al-Mansouri', 'Moskee Salahaddien is een van de oudste en grootste moskeeën in Gent.', 51.0543, 3.7174),
                ('Moskee Al-Fath', 'Korte Meer 11, 9000 Gent', '+32 9 234 56 78', 'info@alfath.be', 'www.alfath.be', 350, 1992, 'Sheikh Ibrahim Al-Turk', 'Moskee Al-Fath is gelegen in het centrum van Gent en richt zich op educatie en gemeenschapsopbouw.', 51.0538, 3.7251),
                ('Moskee Selimiye', 'Kasteellaan 15, 9000 Gent', '+32 9 345 67 89', 'info@selimiye.be', 'www.selimiye.be', 300, 1998, 'Sheikh Omar Al-Belgiki', 'Een moderne moskee met uitgebreide jeugdprogramma\'s en gemeenschapsactiviteiten.', 51.0501, 3.7089)
            ]
            
            conn.executemany('''
                INSERT INTO mosques (name, address, phone, email, website, capacity, established_year, imam_name, description, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', mosques_data)
            
            # Sample users
            users_data = [
                ('admin@vgm.be', hash_password('admin123'), 'Admin', 'VGM', '+32 9 000 00 00', 'admin', 1, 1, 1),
                ('imam@salahaddien.be', hash_password('imam123'), 'Ahmed', 'Al-Mansouri', '+32 9 123 45 67', 'mosque_admin', 1, 1, 1),
                ('user@example.com', hash_password('user123'), 'Mohamed', 'Omar', '+32 9 111 11 11', 'user', 1, 1, 1)
            ]
            
            conn.executemany('''
                INSERT INTO users (email, password_hash, first_name, last_name, phone, role, mosque_id, is_active, email_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', users_data)
            
            # Sample campaigns
            campaigns_data = [
                ('Moskee Renovatie', 'Renovatie van de hoofdingang en gebedsruimte', 50000.0, 0, 1, 1, 'active', '2024-01-01', '2024-12-31'),
                ('Ramadan Iftar', 'Gemeenschappelijke iftar-maaltijden tijdens Ramadan', 10000.0, 0, 2, 2, 'active', '2024-03-01', '2024-04-30'),
                ('Educatie Programma', 'Islamitische educatie voor kinderen en volwassenen', 25000.0, 0, 3, 2, 'active', '2024-01-01', '2024-12-31')
            ]
            
            conn.executemany('''
                INSERT INTO campaigns (title, description, target_amount, current_amount, mosque_id, created_by, status, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', campaigns_data)
            
            # Sample events
            events_data = [
                ('Vrijdaggebed', 'Wekelijks vrijdaggebed met khutbah in het Nederlands.', '2024-01-26', '13:00:00', 1, 'prayer', 100, 2),
                ('Iftar Gemeenschapsmaaltijd', 'Gemeenschappelijke iftar-maaltijd tijdens Ramadan', '2024-01-28', '18:30:00', 2, 'community', 150, 2),
                ('Islamitische Geschiedenis Lezing', 'Lezing over de geschiedenis van de islam', '2024-01-30', '19:00:00', 3, 'lecture', 80, 2)
            ]
            
            conn.executemany('''
                INSERT INTO events (title, description, event_date, event_time, mosque_id, event_type, max_attendees, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', events_data)
            
            # Sample news
            news_data = [
                ('Welkom bij VGM', 'Welkom bij de Vereniging van Gentse Moskeeën. We zijn blij u te verwelkomen op onze nieuwe website.', 'Welkom bij de Vereniging van Gentse Moskeeën.', 1),
                ('Ramadan 2024 Aankondiging', 'De VGM kondigt de Ramadan activiteiten voor 2024 aan, inclusief gemeenschappelijke iftar-maaltijden.', 'Ramadan 2024 activiteiten aangekondigd.', 1),
                ('Nieuwe Moskee Aangesloten', 'We verwelkomen een nieuwe moskee in ons netwerk: Moskee An-Nour in Ledeberg.', 'Nieuwe moskee aangesloten bij VGM.', 1)
            ]
            
            conn.executemany('''
                INSERT INTO news (title, content, excerpt, author_id)
                VALUES (?, ?, ?, ?)
            ''', news_data)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully with payment processing")
    
    # Initialize database
    os.makedirs('instance', exist_ok=True)
    init_database()
    
    # Authentication middleware
    def require_auth(f):
        """Decorator to require authentication"""
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'No token provided'}), 401
            
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = verify_jwt_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            request.user_id = payload['user_id']
            request.user_role = payload['role']
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    def require_role(required_role):
        """Decorator to require specific role"""
        def decorator(f):
            def decorated_function(*args, **kwargs):
                if not hasattr(request, 'user_role') or request.user_role != required_role:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                return f(*args, **kwargs)
            decorated_function.__name__ = f.__name__
            return decorated_function
        return decorator
    
    # API Routes
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})
    
    # Payment endpoints
    @app.route('/api/payments/create-payment-intent', methods=['POST'])
    def create_payment_intent():
        """Create Stripe payment intent"""
        try:
            data = request.get_json()
            amount = data.get('amount')
            currency = data.get('currency', 'eur')
            donation_type = data.get('donation_type', 'general')
            mosque_id = data.get('mosque_id')
            campaign_id = data.get('campaign_id')
            donor_name = data.get('donor_name')
            donor_email = data.get('donor_email')
            
            if not amount or amount <= 0:
                return jsonify({'error': 'Invalid amount'}), 400
            
            # Convert to cents for Stripe
            amount_cents = int(float(amount) * 100)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata={
                    'donation_type': donation_type,
                    'mosque_id': str(mosque_id) if mosque_id else '',
                    'campaign_id': str(campaign_id) if campaign_id else '',
                    'donor_name': donor_name or '',
                    'donor_email': donor_email or ''
                }
            )
            
            return jsonify({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            })
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return jsonify({'error': 'Payment processing error'}), 500
        except Exception as e:
            logger.error(f"Payment intent error: {e}")
            return jsonify({'error': 'Failed to create payment intent'}), 500
    
    @app.route('/api/payments/confirm-payment', methods=['POST'])
    def confirm_payment():
        """Confirm payment and save donation"""
        try:
            data = request.get_json()
            payment_intent_id = data.get('payment_intent_id')
            
            if not payment_intent_id:
                return jsonify({'error': 'Payment intent ID required'}), 400
            
            # Retrieve payment intent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status != 'succeeded':
                return jsonify({'error': 'Payment not completed'}), 400
            
            # Extract metadata
            metadata = intent.metadata
            amount = intent.amount / 100  # Convert back from cents
            
            # Save donation to database
            conn = get_db_connection()
            cursor = conn.execute('''
                INSERT INTO donations (
                    donor_name, donor_email, amount, currency, donation_type,
                    mosque_id, campaign_id, stripe_payment_intent_id, status, payment_method
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.get('donor_name'),
                metadata.get('donor_email'),
                amount,
                intent.currency,
                metadata.get('donation_type'),
                int(metadata.get('mosque_id')) if metadata.get('mosque_id') else None,
                int(metadata.get('campaign_id')) if metadata.get('campaign_id') else None,
                payment_intent_id,
                'completed',
                'card'
            ))
            
            donation_id = cursor.lastrowid
            
            # Update campaign amount if applicable
            if metadata.get('campaign_id'):
                conn.execute('''
                    UPDATE campaigns 
                    SET current_amount = current_amount + ? 
                    WHERE id = ?
                ''', (amount, int(metadata.get('campaign_id'))))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'donation_id': donation_id,
                'status': 'completed',
                'amount': amount,
                'currency': intent.currency
            })
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return jsonify({'error': 'Payment verification error'}), 500
        except Exception as e:
            logger.error(f"Payment confirmation error: {e}")
            return jsonify({'error': 'Failed to confirm payment'}), 500
    
    @app.route('/api/campaigns', methods=['GET'])
    def get_campaigns():
        """Get all active campaigns"""
        try:
            conn = get_db_connection()
            campaigns = conn.execute('''
                SELECT c.*, m.name as mosque_name,
                       CASE 
                           WHEN c.target_amount > 0 THEN (c.current_amount / c.target_amount) * 100
                           ELSE 0
                       END as progress_percentage
                FROM campaigns c
                LEFT JOIN mosques m ON c.mosque_id = m.id
                WHERE c.status = 'active'
                ORDER BY c.created_at DESC
            ''').fetchall()
            conn.close()
            
            return jsonify([dict(campaign) for campaign in campaigns])
        except Exception as e:
            logger.error(f"Error fetching campaigns: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/campaigns/<int:campaign_id>', methods=['GET'])
    def get_campaign(campaign_id):
        """Get specific campaign by ID"""
        try:
            conn = get_db_connection()
            campaign = conn.execute('''
                SELECT c.*, m.name as mosque_name,
                       CASE 
                           WHEN c.target_amount > 0 THEN (c.current_amount / c.target_amount) * 100
                           ELSE 0
                       END as progress_percentage
                FROM campaigns c
                LEFT JOIN mosques m ON c.mosque_id = m.id
                WHERE c.id = ? AND c.status = 'active'
            ''', (campaign_id,)).fetchone()
            conn.close()
            
            if campaign is None:
                return jsonify({'error': 'Campaign not found'}), 404
            
            return jsonify(dict(campaign))
        except Exception as e:
            logger.error(f"Error fetching campaign {campaign_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/donations', methods=['GET'])
    @require_auth
    def get_donations():
        """Get donations (admin only)"""
        try:
            conn = get_db_connection()
            donations = conn.execute('''
                SELECT d.*, m.name as mosque_name, c.title as campaign_title
                FROM donations d
                LEFT JOIN mosques m ON d.mosque_id = m.id
                LEFT JOIN campaigns c ON d.campaign_id = c.id
                ORDER BY d.created_at DESC
            ''').fetchall()
            conn.close()
            
            return jsonify([dict(donation) for donation in donations])
        except Exception as e:
            logger.error(f"Error fetching donations: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Existing authentication endpoints (unchanged)
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """User login endpoint"""
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({'error': 'Email and password required'}), 400
            
            conn = get_db_connection()
            user = conn.execute('''
                SELECT u.*, m.name as mosque_name 
                FROM users u 
                LEFT JOIN mosques m ON u.mosque_id = m.id 
                WHERE u.email = ? AND u.is_active = 1
            ''', (email,)).fetchone()
            conn.close()
            
            if not user or not verify_password(password, user['password_hash']):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Generate JWT token
            token = generate_jwt_token(user['id'], user['role'])
            
            # Store session
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO user_sessions (user_id, token, expires_at)
                VALUES (?, ?, ?)
            ''', (user['id'], token, datetime.utcnow() + timedelta(hours=24)))
            conn.commit()
            conn.close()
            
            return jsonify({
                'token': token,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'role': user['role'],
                    'mosque_id': user['mosque_id'],
                    'mosque_name': user['mosque_name']
                }
            })
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return jsonify({'error': 'Login failed'}), 500
    
    # Existing API endpoints (unchanged)
    @app.route('/api/mosques', methods=['GET'])
    def get_mosques():
        """Get all active mosques"""
        try:
            conn = get_db_connection()
            mosques = conn.execute('''
                SELECT * FROM mosques WHERE is_active = 1 ORDER BY name
            ''').fetchall()
            conn.close()
            
            return jsonify([dict(mosque) for mosque in mosques])
        except Exception as e:
            logger.error(f"Error fetching mosques: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/events', methods=['GET'])
    def get_events():
        """Get all active events"""
        try:
            conn = get_db_connection()
            events = conn.execute('''
                SELECT e.*, m.name as mosque_name
                FROM events e
                LEFT JOIN mosques m ON e.mosque_id = m.id
                WHERE e.is_active = 1
                ORDER BY e.event_date ASC, e.event_time ASC
            ''').fetchall()
            conn.close()
            
            return jsonify([dict(event) for event in events])
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/news', methods=['GET'])
    def get_news():
        """Get all published news"""
        try:
            conn = get_db_connection()
            news = conn.execute('''
                SELECT n.*, u.first_name, u.last_name
                FROM news n
                LEFT JOIN users u ON n.author_id = u.id
                WHERE n.status = 'published' 
                ORDER BY n.published_at DESC
            ''').fetchall()
            conn.close()
            
            return jsonify([dict(article) for article in news])
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return jsonify({'error': str(e)}), 500
    
    return app

# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)