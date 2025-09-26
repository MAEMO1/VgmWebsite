#!/usr/bin/env python3
"""
VGM Website - Enhanced Backend with Authentication
P1 Implementation: Authentication System
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask application with authentication"""
    app = Flask(__name__)
    
    # Configure secret key for sessions
    app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    
    # JWT Secret Key
    JWT_SECRET = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))
    
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
        """Initialize database with authentication tables"""
        conn = get_db_connection()
        
        # Create tables
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
        logger.info("Database initialized successfully with authentication")
    
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
    
    # Authentication endpoints
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
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """User registration endpoint"""
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            phone = data.get('phone')
            mosque_id = data.get('mosque_id')
            
            if not all([email, password, first_name, last_name]):
                return jsonify({'error': 'All required fields must be provided'}), 400
            
            conn = get_db_connection()
            
            # Check if user already exists
            existing_user = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
            if existing_user:
                conn.close()
                return jsonify({'error': 'User already exists'}), 409
            
            # Create new user
            password_hash = hash_password(password)
            cursor = conn.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name, phone, mosque_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, password_hash, first_name, last_name, phone, mosque_id))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return jsonify({'error': 'Registration failed'}), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    @require_auth
    def logout():
        """User logout endpoint"""
        try:
            token = request.headers.get('Authorization')[7:]  # Remove 'Bearer '
            
            conn = get_db_connection()
            conn.execute('DELETE FROM user_sessions WHERE token = ?', (token,))
            conn.commit()
            conn.close()
            
            return jsonify({'message': 'Logged out successfully'})
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return jsonify({'error': 'Logout failed'}), 500
    
    @app.route('/api/auth/me', methods=['GET'])
    @require_auth
    def get_current_user():
        """Get current user info"""
        try:
            conn = get_db_connection()
            user = conn.execute('''
                SELECT u.*, m.name as mosque_name 
                FROM users u 
                LEFT JOIN mosques m ON u.mosque_id = m.id 
                WHERE u.id = ?
            ''', (request.user_id,)).fetchone()
            conn.close()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify({
                'id': user['id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': user['role'],
                'mosque_id': user['mosque_id'],
                'mosque_name': user['mosque_name'],
                'phone': user['phone'],
                'email_verified': user['email_verified']
            })
            
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return jsonify({'error': 'Failed to get user info'}), 500
    
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
    
    # Admin endpoints
    @app.route('/api/admin/users', methods=['GET'])
    @require_auth
    @require_role('admin')
    def get_all_users():
        """Get all users (admin only)"""
        try:
            conn = get_db_connection()
            users = conn.execute('''
                SELECT u.*, m.name as mosque_name 
                FROM users u 
                LEFT JOIN mosques m ON u.mosque_id = m.id 
                ORDER BY u.created_at DESC
            ''').fetchall()
            conn.close()
            
            return jsonify([dict(user) for user in users])
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/events', methods=['POST'])
    @require_auth
    @require_role('admin')
    def create_event():
        """Create new event (admin only)"""
        try:
            data = request.get_json()
            
            conn = get_db_connection()
            cursor = conn.execute('''
                INSERT INTO events (title, description, event_date, event_time, mosque_id, event_type, max_attendees, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('title'),
                data.get('description'),
                data.get('event_date'),
                data.get('event_time'),
                data.get('mosque_id'),
                data.get('event_type', 'event'),
                data.get('max_attendees'),
                request.user_id
            ))
            
            event_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({'message': 'Event created successfully', 'event_id': event_id}), 201
            
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return jsonify({'error': str(e)}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)