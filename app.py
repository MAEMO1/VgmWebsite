#!/usr/bin/env python3
"""
VGM Website - Enhanced Backend with Payment Processing
P2 Implementation: Stripe Integration
"""

import os
import logging
import secrets
import hashlib
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
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
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Configure CORS properly
    default_origins = [
        'http://localhost:3000',
        'http://localhost:3001',
        'https://vgm-website.vercel.app',
        'https://frontend-maemo.vercel.app'
    ]
    cors_origins = os.environ.get('ALLOWED_ORIGINS', ','.join(default_origins)).split(',')
    cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

    CORS(
        app,
        origins=cors_origins,
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization', 'X-CSRF-Token'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    )
    
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
    
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def get_file_size(file):
        """Get file size in bytes"""
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        return size
    
    def create_notification(user_id, title, message, notification_type, mosque_id=None, priority='normal', action_url=None, metadata=None, expires_at=None):
        """Create a notification for a user"""
        conn = get_db_connection()
        cursor = conn.execute('''
            INSERT INTO notifications (
                user_id, mosque_id, title, message, notification_type, 
                priority, action_url, metadata, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, mosque_id, title, message, notification_type, priority, action_url, metadata, expires_at))
        
        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return notification_id
    
    def get_user_notifications(user_id, limit=50, offset=0, unread_only=False):
        """Get notifications for a user"""
        conn = get_db_connection()
        
        query = '''
            SELECT n.*, m.name as mosque_name
            FROM notifications n
            LEFT JOIN mosques m ON n.mosque_id = m.id
            WHERE n.user_id = ?
        '''
        params = [user_id]
        
        if unread_only:
            query += ' AND n.is_read = 0'
        
        query += ' ORDER BY n.created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        notifications = conn.execute(query, params).fetchall()
        conn.close()
        
        return [dict(notification) for notification in notifications]
    
    def mark_notification_read(notification_id, user_id):
        """Mark a notification as read"""
        conn = get_db_connection()
        conn.execute('''
            UPDATE notifications 
            SET is_read = 1 
            WHERE id = ? AND user_id = ?
        ''', (notification_id, user_id))
        conn.commit()
        conn.close()
    
    def mark_all_notifications_read(user_id):
        """Mark all notifications as read for a user"""
        conn = get_db_connection()
        conn.execute('''
            UPDATE notifications 
            SET is_read = 1 
            WHERE user_id = ? AND is_read = 0
        ''', (user_id,))
        conn.commit()
        conn.close()
    
    def get_notification_count(user_id):
        """Get unread notification count for a user"""
        conn = get_db_connection()
        count = conn.execute('''
            SELECT COUNT(*) FROM notifications 
            WHERE user_id = ? AND is_read = 0
        ''', (user_id,)).fetchone()[0]
        conn.close()
        return count
    
    def track_analytics_event(event_type, user_id=None, mosque_id=None, event_data=None, ip_address=None, user_agent=None):
        """Track an analytics event"""
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO analytics_events (event_type, user_id, mosque_id, event_data, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_type, user_id, mosque_id, event_data, ip_address, user_agent))
        conn.commit()
        conn.close()
    
    def track_page_view(page_path, user_id=None, session_id=None, ip_address=None, user_agent=None, referrer=None):
        """Track a page view"""
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO page_views (page_path, user_id, session_id, ip_address, user_agent, referrer)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (page_path, user_id, session_id, ip_address, user_agent, referrer))
        conn.commit()
        conn.close()
    
    def track_user_activity(user_id, activity_type, activity_data=None, ip_address=None):
        """Track user activity"""
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO user_activity (user_id, activity_type, activity_data, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (user_id, activity_type, activity_data, ip_address))
        conn.commit()
        conn.close()
    
    def get_analytics_summary(days=30):
        """Get analytics summary for the last N days"""
        conn = get_db_connection()
        
        # Page views
        page_views = conn.execute('''
            SELECT page_path, COUNT(*) as views
            FROM page_views
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY page_path
            ORDER BY views DESC
            LIMIT 10
        '''.format(days)).fetchall()
        
        # Event types
        events = conn.execute('''
            SELECT event_type, COUNT(*) as count
            FROM analytics_events
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY event_type
            ORDER BY count DESC
        '''.format(days)).fetchall()
        
        # User activity
        user_activity = conn.execute('''
            SELECT activity_type, COUNT(*) as count
            FROM user_activity
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY activity_type
            ORDER BY count DESC
        '''.format(days)).fetchall()
        
        # Daily stats
        daily_stats = conn.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as page_views
            FROM page_views
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        '''.format(days)).fetchall()
        
        conn.close()
        
        return {
            'page_views': [dict(row) for row in page_views],
            'events': [dict(row) for row in events],
            'user_activity': [dict(row) for row in user_activity],
            'daily_stats': [dict(row) for row in daily_stats]
        }
    
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
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS media_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_type TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                uploaded_by INTEGER,
                mosque_id INTEGER,
                event_id INTEGER,
                campaign_id INTEGER,
                description TEXT,
                is_public BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uploaded_by) REFERENCES users (id),
                FOREIGN KEY (mosque_id) REFERENCES mosques (id),
                FOREIGN KEY (event_id) REFERENCES events (id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                mosque_id INTEGER,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                priority TEXT DEFAULT 'normal',
                is_read BOOLEAN DEFAULT 0,
                action_url TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (mosque_id) REFERENCES mosques (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notification_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                notification_type TEXT NOT NULL,
                email_enabled BOOLEAN DEFAULT 1,
                push_enabled BOOLEAN DEFAULT 1,
                sms_enabled BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, notification_type)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notification_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_name TEXT UNIQUE NOT NULL,
                notification_type TEXT NOT NULL,
                title_template TEXT NOT NULL,
                message_template TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS analytics_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                user_id INTEGER,
                mosque_id INTEGER,
                event_data TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (mosque_id) REFERENCES mosques (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS page_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_path TEXT NOT NULL,
                user_id INTEGER,
                session_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                referrer TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                ip_address TEXT,
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
    
    # File upload endpoints
    @app.route('/api/upload', methods=['POST'])
    @require_auth
    def upload_file():
        """Upload a file"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'File type not allowed'}), 400
            
            # Get file info
            file_size = get_file_size(file)
            if file_size > MAX_CONTENT_LENGTH:
                return jsonify({'error': 'File too large'}), 400
            
            # Generate unique filename
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            secure_original_name = secure_filename(file.filename)
            
            # Save file
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            # Get additional data
            description = request.form.get('description', '')
            mosque_id = request.form.get('mosque_id')
            event_id = request.form.get('event_id')
            campaign_id = request.form.get('campaign_id')
            is_public = request.form.get('is_public', 'true').lower() == 'true'
            
            # Save file info to database
            conn = get_db_connection()
            cursor = conn.execute('''
                INSERT INTO media_files (
                    filename, original_filename, file_path, file_size, file_type,
                    mime_type, uploaded_by, mosque_id, event_id, campaign_id,
                    description, is_public
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                unique_filename,
                secure_original_name,
                file_path,
                file_size,
                file_extension,
                file.content_type,
                request.user_id,
                int(mosque_id) if mosque_id else None,
                int(event_id) if event_id else None,
                int(campaign_id) if campaign_id else None,
                description,
                is_public
            ))
            
            file_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({
                'file_id': file_id,
                'filename': unique_filename,
                'original_filename': secure_original_name,
                'file_size': file_size,
                'file_type': file_extension,
                'mime_type': file.content_type,
                'url': f'/api/files/{file_id}'
            })
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return jsonify({'error': 'Failed to upload file'}), 500
    
    @app.route('/api/files/<int:file_id>', methods=['GET'])
    def get_file(file_id):
        """Get file by ID"""
        try:
            conn = get_db_connection()
            file_info = conn.execute('''
                SELECT * FROM media_files WHERE id = ? AND is_public = 1
            ''', (file_id,)).fetchone()
            conn.close()
            
            if not file_info:
                return jsonify({'error': 'File not found'}), 404
            
            return send_from_directory(
                UPLOAD_FOLDER,
                file_info['filename'],
                as_attachment=False,
                download_name=file_info['original_filename']
            )
            
        except Exception as e:
            logger.error(f"Error retrieving file {file_id}: {e}")
            return jsonify({'error': 'Failed to retrieve file'}), 500
    
    @app.route('/api/files', methods=['GET'])
    def get_files():
        """Get all public files"""
        try:
            conn = get_db_connection()
            files = conn.execute('''
                SELECT mf.*, u.first_name, u.last_name, mo.name as mosque_name
                FROM media_files mf
                LEFT JOIN users u ON mf.uploaded_by = u.id
                LEFT JOIN mosques mo ON mf.mosque_id = mo.id
                WHERE mf.is_public = 1
                ORDER BY mf.created_at DESC
            ''').fetchall()
            conn.close()
            
            return jsonify([dict(file) for file in files])
        except Exception as e:
            logger.error(f"Error fetching files: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/files/<int:file_id>', methods=['DELETE'])
    @require_auth
    def delete_file(file_id):
        """Delete file (admin or owner only)"""
        try:
            conn = get_db_connection()
            file_info = conn.execute('''
                SELECT * FROM media_files WHERE id = ?
            ''', (file_id,)).fetchone()
            
            if not file_info:
                return jsonify({'error': 'File not found'}), 404
            
            # Check permissions
            if request.user_role != 'admin' and file_info['uploaded_by'] != request.user_id:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            # Delete file from filesystem
            try:
                os.remove(file_info['file_path'])
            except OSError:
                pass  # File might already be deleted
            
            # Delete from database
            conn.execute('DELETE FROM media_files WHERE id = ?', (file_id,))
            conn.commit()
            conn.close()
            
            return jsonify({'message': 'File deleted successfully'})
            
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return jsonify({'error': 'Failed to delete file'}), 500
    
    # Notification endpoints
    @app.route('/api/notifications', methods=['GET'])
    @require_auth
    def get_notifications():
        """Get notifications for the current user"""
        try:
            limit = int(request.args.get('limit', 50))
            offset = int(request.args.get('offset', 0))
            unread_only = request.args.get('unread_only', 'false').lower() == 'true'
            
            notifications = get_user_notifications(request.user_id, limit, offset, unread_only)
            unread_count = get_notification_count(request.user_id)
            
            return jsonify({
                'notifications': notifications,
                'unread_count': unread_count,
                'total_count': len(notifications)
            })
            
        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
    @require_auth
    def mark_notification_read_endpoint(notification_id):
        """Mark a specific notification as read"""
        try:
            mark_notification_read(notification_id, request.user_id)
            return jsonify({'message': 'Notification marked as read'})
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/notifications/read-all', methods=['POST'])
    @require_auth
    def mark_all_notifications_read_endpoint():
        """Mark all notifications as read for the current user"""
        try:
            mark_all_notifications_read(request.user_id)
            return jsonify({'message': 'All notifications marked as read'})
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/notifications/count', methods=['GET'])
    @require_auth
    def get_notification_count_endpoint():
        """Get unread notification count for the current user"""
        try:
            count = get_notification_count(request.user_id)
            return jsonify({'unread_count': count})
            
        except Exception as e:
            logger.error(f"Error getting notification count: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/notifications/preferences', methods=['GET'])
    @require_auth
    def get_notification_preferences():
        """Get notification preferences for the current user"""
        try:
            conn = get_db_connection()
            preferences = conn.execute('''
                SELECT notification_type, email_enabled, push_enabled, sms_enabled
                FROM notification_preferences
                WHERE user_id = ?
            ''', (request.user_id,)).fetchall()
            conn.close()
            
            return jsonify([dict(pref) for pref in preferences])
            
        except Exception as e:
            logger.error(f"Error fetching notification preferences: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/notifications/preferences', methods=['POST'])
    @require_auth
    def update_notification_preferences():
        """Update notification preferences for the current user"""
        try:
            data = request.get_json()
            notification_type = data.get('notification_type')
            email_enabled = data.get('email_enabled', True)
            push_enabled = data.get('push_enabled', True)
            sms_enabled = data.get('sms_enabled', False)
            
            conn = get_db_connection()
            conn.execute('''
                INSERT OR REPLACE INTO notification_preferences 
                (user_id, notification_type, email_enabled, push_enabled, sms_enabled, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (request.user_id, notification_type, email_enabled, push_enabled, sms_enabled))
            conn.commit()
            conn.close()
            
            return jsonify({'message': 'Notification preferences updated'})
            
        except Exception as e:
            logger.error(f"Error updating notification preferences: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Admin notification endpoints
    @app.route('/api/admin/notifications', methods=['POST'])
    @require_auth
    @require_role('admin')
    def create_notification():
        """Create a notification (admin only)"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            mosque_id = data.get('mosque_id')
            title = data.get('title')
            message = data.get('message')
            notification_type = data.get('notification_type', 'general')
            priority = data.get('priority', 'normal')
            action_url = data.get('action_url')
            metadata = data.get('metadata')
            expires_at = data.get('expires_at')
            
            if not user_id or not title or not message:
                return jsonify({'error': 'user_id, title, and message are required'}), 400
            
            notification_id = create_notification(
                user_id, title, message, notification_type, mosque_id,
                priority, action_url, metadata, expires_at
            )
            
            return jsonify({
                'notification_id': notification_id,
                'message': 'Notification created successfully'
            })
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Analytics endpoints
    @app.route('/api/analytics/track', methods=['POST'])
    def track_event():
        """Track an analytics event"""
        try:
            data = request.get_json()
            event_type = data.get('event_type')
            user_id = data.get('user_id')
            mosque_id = data.get('mosque_id')
            event_data = data.get('event_data')
            
            if not event_type:
                return jsonify({'error': 'event_type is required'}), 400
            
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            
            track_analytics_event(event_type, user_id, mosque_id, event_data, ip_address, user_agent)
            
            return jsonify({'message': 'Event tracked successfully'})
            
        except Exception as e:
            logger.error(f"Error tracking event: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/analytics/page-view', methods=['POST'])
    def track_page_view_endpoint():
        """Track a page view"""
        try:
            data = request.get_json()
            page_path = data.get('page_path')
            user_id = data.get('user_id')
            session_id = data.get('session_id')
            
            if not page_path:
                return jsonify({'error': 'page_path is required'}), 400
            
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            referrer = request.headers.get('Referer')
            
            track_page_view(page_path, user_id, session_id, ip_address, user_agent, referrer)
            
            return jsonify({'message': 'Page view tracked successfully'})
            
        except Exception as e:
            logger.error(f"Error tracking page view: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/analytics/summary', methods=['GET'])
    @require_auth
    @require_role('admin')
    def get_analytics_summary_endpoint():
        """Get analytics summary (admin only)"""
        try:
            days = int(request.args.get('days', 30))
            summary = get_analytics_summary(days)
            
            return jsonify(summary)
            
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/analytics/reports', methods=['GET'])
    @require_auth
    @require_role('admin')
    def get_analytics_reports():
        """Get detailed analytics reports (admin only)"""
        try:
            days = int(request.args.get('days', 30))
            report_type = request.args.get('type', 'overview')
            
            conn = get_db_connection()
            
            if report_type == 'overview':
                # Overview report
                total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
                total_mosques = conn.execute('SELECT COUNT(*) FROM mosques WHERE is_active = 1').fetchone()[0]
                total_events = conn.execute('SELECT COUNT(*) FROM events WHERE is_active = 1').fetchone()[0]
                total_donations = conn.execute('SELECT COUNT(*) FROM donations').fetchone()[0]
                total_page_views = conn.execute('''
                    SELECT COUNT(*) FROM page_views 
                    WHERE created_at >= datetime('now', '-{} days')
                '''.format(days)).fetchone()[0]
                
                report = {
                    'total_users': total_users,
                    'total_mosques': total_mosques,
                    'total_events': total_events,
                    'total_donations': total_donations,
                    'total_page_views': total_page_views,
                    'period_days': days
                }
                
            elif report_type == 'users':
                # User activity report
                user_stats = conn.execute('''
                    SELECT 
                        u.id, u.first_name, u.last_name, u.email, u.role,
                        COUNT(ua.id) as activity_count,
                        MAX(ua.created_at) as last_activity
                    FROM users u
                    LEFT JOIN user_activity ua ON u.id = ua.user_id
                    WHERE ua.created_at >= datetime('now', '-{} days') OR ua.created_at IS NULL
                    GROUP BY u.id
                    ORDER BY activity_count DESC
                '''.format(days)).fetchall()
                
                report = [dict(row) for row in user_stats]
                
            elif report_type == 'mosques':
                # Mosque activity report
                mosque_stats = conn.execute('''
                    SELECT 
                        m.id, m.name, m.address,
                        COUNT(DISTINCT e.id) as event_count,
                        COUNT(DISTINCT d.id) as donation_count,
                        COUNT(DISTINCT ae.id) as analytics_events
                    FROM mosques m
                    LEFT JOIN events e ON m.id = e.mosque_id AND e.is_active = 1
                    LEFT JOIN donations d ON m.id = d.mosque_id
                    LEFT JOIN analytics_events ae ON m.id = ae.mosque_id
                    WHERE ae.created_at >= datetime('now', '-{} days') OR ae.created_at IS NULL
                    GROUP BY m.id
                    ORDER BY analytics_events DESC
                '''.format(days)).fetchall()
                
                report = [dict(row) for row in mosque_stats]
                
            else:
                return jsonify({'error': 'Invalid report type'}), 400
            
            conn.close()
            return jsonify(report)
            
        except Exception as e:
            logger.error(f"Error getting analytics reports: {e}")
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
    
    # Advanced search endpoints
    @app.route('/api/search', methods=['GET'])
    def advanced_search():
        """Advanced search across all content types"""
        conn = None
        try:
            query = request.args.get('q', '').strip()
            selected_types = request.args.getlist('type')
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            location = request.args.get('location', '').strip()
            capacity_min = request.args.get('capacity_min', type=int)
            capacity_max = request.args.get('capacity_max', type=int)
            sort = request.args.get('sort', 'relevance')
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=20, type=int)

            valid_types = {'mosques', 'events', 'news', 'campaigns'}
            if selected_types:
                selected_types = [ctype for ctype in selected_types if ctype in valid_types]
            if not selected_types:
                selected_types = list(valid_types)

            results = {
                'mosques': [],
                'events': [],
                'news': [],
                'campaigns': [],
                'total_results': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0
            }

            conn = get_db_connection()

            def build_like_conditions(columns, value):
                like_value = f"%{value.lower()}%"
                placeholders = [f"LOWER(COALESCE({col}, '')) LIKE ?" for col in columns]
                return "(" + " OR ".join(placeholders) + ")", [like_value] * len(columns)

            # Search mosques
            if 'mosques' in selected_types:
                mosque_query_parts = ["SELECT * FROM mosques WHERE is_active = 1"]
                mosque_params = []

                if query:
                    condition, params = build_like_conditions(
                        ['name', 'description', 'address', 'imam_name', 'email', 'phone'],
                        query
                    )
                    mosque_query_parts.append("AND " + condition)
                    mosque_params.extend(params)

                if location:
                    condition, params = build_like_conditions(['address'], location)
                    mosque_query_parts.append("AND " + condition)
                    mosque_params.extend(params)

                if capacity_min is not None:
                    mosque_query_parts.append("AND capacity >= ?")
                    mosque_params.append(capacity_min)

                if capacity_max is not None:
                    mosque_query_parts.append("AND capacity <= ?")
                    mosque_params.append(capacity_max)

                if sort in ('recent', 'newest'):
                    order_clause = " ORDER BY created_at DESC"
                elif sort == 'oldest':
                    order_clause = " ORDER BY created_at ASC"
                elif sort == 'name_desc':
                    order_clause = " ORDER BY name COLLATE NOCASE DESC"
                else:
                    order_clause = " ORDER BY name COLLATE NOCASE ASC"

                mosque_query = " ".join(mosque_query_parts) + order_clause
                mosques = conn.execute(mosque_query, mosque_params).fetchall()
                results['mosques'] = [dict(mosque) for mosque in mosques]

            # Search events
            if 'events' in selected_types:
                event_query_parts = [
                    "SELECT e.*, m.name AS mosque_name, m.address AS mosque_address"
                    " FROM events e"
                    " LEFT JOIN mosques m ON e.mosque_id = m.id"
                    " WHERE e.is_active = 1"
                ]
                event_params = []

                if query:
                    condition, params = build_like_conditions(
                        ['e.title', 'e.description', 'm.name', 'm.address'],
                        query
                    )
                    event_query_parts.append("AND " + condition)
                    event_params.extend(params)

                if location:
                    condition, params = build_like_conditions(['m.address'], location)
                    event_query_parts.append("AND " + condition)
                    event_params.extend(params)

                if date_from:
                    event_query_parts.append("AND DATE(e.event_date) >= DATE(?)")
                    event_params.append(date_from)

                if date_to:
                    event_query_parts.append("AND DATE(e.event_date) <= DATE(?)")
                    event_params.append(date_to)

                if sort in ('recent', 'newest'):
                    order_clause = " ORDER BY e.event_date DESC, e.event_time DESC"
                elif sort == 'oldest':
                    order_clause = " ORDER BY e.event_date ASC, e.event_time ASC"
                else:
                    order_clause = " ORDER BY e.event_date ASC, e.event_time ASC"

                event_query = " ".join(event_query_parts) + order_clause
                events = conn.execute(event_query, event_params).fetchall()
                results['events'] = [dict(event) for event in events]

            # Search news
            if 'news' in selected_types:
                news_query_parts = [
                    "SELECT n.*, u.first_name, u.last_name"
                    " FROM news n"
                    " LEFT JOIN users u ON n.author_id = u.id"
                    " WHERE n.status = 'published'"
                ]
                news_params = []

                if query:
                    condition, params = build_like_conditions(
                        ['n.title', 'n.excerpt', 'n.content', 'u.first_name', 'u.last_name'],
                        query
                    )
                    news_query_parts.append("AND " + condition)
                    news_params.extend(params)

                if date_from:
                    news_query_parts.append("AND DATE(n.published_at) >= DATE(?)")
                    news_params.append(date_from)

                if date_to:
                    news_query_parts.append("AND DATE(n.published_at) <= DATE(?)")
                    news_params.append(date_to)

                if sort in ('recent', 'newest'):
                    order_clause = " ORDER BY n.published_at DESC"
                elif sort == 'oldest':
                    order_clause = " ORDER BY n.published_at ASC"
                elif sort == 'name_desc':
                    order_clause = " ORDER BY n.title COLLATE NOCASE DESC"
                elif sort == 'name':
                    order_clause = " ORDER BY n.title COLLATE NOCASE ASC"
                else:
                    order_clause = " ORDER BY n.published_at DESC"

                news_query = " ".join(news_query_parts) + order_clause
                news = conn.execute(news_query, news_params).fetchall()
                results['news'] = [dict(article) for article in news]

            # Search campaigns
            if 'campaigns' in selected_types:
                campaign_query_parts = [
                    "SELECT c.*, m.name AS mosque_name, m.address AS mosque_address"
                    " FROM campaigns c"
                    " LEFT JOIN mosques m ON c.mosque_id = m.id"
                    " WHERE c.status = 'active'"
                ]
                campaign_params = []

                if query:
                    condition, params = build_like_conditions(
                        ['c.title', 'c.description', 'm.name', 'm.address'],
                        query
                    )
                    campaign_query_parts.append("AND " + condition)
                    campaign_params.extend(params)

                if location:
                    condition, params = build_like_conditions(['m.address'], location)
                    campaign_query_parts.append("AND " + condition)
                    campaign_params.extend(params)

                if date_from:
                    campaign_query_parts.append("AND DATE(c.start_date) >= DATE(?)")
                    campaign_params.append(date_from)

                if date_to:
                    campaign_query_parts.append("AND DATE(c.end_date) <= DATE(?)")
                    campaign_params.append(date_to)

                if sort in ('recent', 'newest'):
                    order_clause = " ORDER BY c.start_date DESC"
                elif sort == 'oldest':
                    order_clause = " ORDER BY c.start_date ASC"
                else:
                    order_clause = " ORDER BY c.start_date ASC"

                campaign_query = " ".join(campaign_query_parts) + order_clause
                campaigns = conn.execute(campaign_query, campaign_params).fetchall()
                results['campaigns'] = [dict(campaign) for campaign in campaigns]

            total_results = (
                len(results['mosques']) +
                len(results['events']) +
                len(results['news']) +
                len(results['campaigns'])
            )
            results['total_results'] = total_results
            results['total_pages'] = (total_results + per_page - 1) // per_page if per_page else 0

            return jsonify(results)

        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if conn is not None:
                conn.close()
    
    return app

# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
