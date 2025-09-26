#!/usr/bin/env python3
"""
VGM Website - Clean Backend Implementation
A simplified, working Flask backend for the VGM website
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask application with clean implementation"""
    app = Flask(__name__)
    
    # Configure CORS properly
    CORS(app, 
         origins=['http://localhost:3000', 'https://vgm-website.vercel.app'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-CSRF-Token'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Database helper functions
    def get_db_connection():
        """Get database connection"""
        conn = sqlite3.connect('instance/vgm_website.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database():
        """Initialize database with clean schema"""
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
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mosque_id) REFERENCES mosques (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                excerpt TEXT,
                author_name TEXT DEFAULT 'VGM Team',
                published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'published',
                featured_image TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
            
            # Sample events
            events_data = [
                ('Vrijdaggebed', 'Wekelijks vrijdaggebed met khutbah in het Nederlands.', '2024-01-26', '13:00:00', 1, 'prayer', 100),
                ('Iftar Gemeenschapsmaaltijd', 'Gemeenschappelijke iftar-maaltijd tijdens Ramadan', '2024-01-28', '18:30:00', 2, 'community', 150),
                ('Islamitische Geschiedenis Lezing', 'Lezing over de geschiedenis van de islam', '2024-01-30', '19:00:00', 3, 'lecture', 80)
            ]
            
            conn.executemany('''
                INSERT INTO events (title, description, event_date, event_time, mosque_id, event_type, max_attendees)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', events_data)
            
            # Sample news
            news_data = [
                ('Welkom bij VGM', 'Welkom bij de Vereniging van Gentse Moskeeën. We zijn blij u te verwelkomen op onze nieuwe website.', 'Welkom bij de Vereniging van Gentse Moskeeën.', 'VGM Team'),
                ('Ramadan 2024 Aankondiging', 'De VGM kondigt de Ramadan activiteiten voor 2024 aan, inclusief gemeenschappelijke iftar-maaltijden.', 'Ramadan 2024 activiteiten aangekondigd.', 'VGM Team'),
                ('Nieuwe Moskee Aangesloten', 'We verwelkomen een nieuwe moskee in ons netwerk: Moskee An-Nour in Ledeberg.', 'Nieuwe moskee aangesloten bij VGM.', 'VGM Team')
            ]
            
            conn.executemany('''
                INSERT INTO news (title, content, excerpt, author_name)
                VALUES (?, ?, ?, ?)
            ''', news_data)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    # Initialize database
    os.makedirs('instance', exist_ok=True)
    init_database()
    
    # API Routes
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})
    
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
    
    @app.route('/api/mosques/<int:mosque_id>', methods=['GET'])
    def get_mosque(mosque_id):
        """Get specific mosque by ID"""
        try:
            conn = get_db_connection()
            mosque = conn.execute('''
                SELECT * FROM mosques WHERE id = ? AND is_active = 1
            ''', (mosque_id,)).fetchone()
            conn.close()
            
            if mosque is None:
                return jsonify({'error': 'Mosque not found'}), 404
            
            return jsonify(dict(mosque))
        except Exception as e:
            logger.error(f"Error fetching mosque {mosque_id}: {e}")
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
    
    @app.route('/api/events/<int:event_id>', methods=['GET'])
    def get_event(event_id):
        """Get specific event by ID"""
        try:
            conn = get_db_connection()
            event = conn.execute('''
                SELECT e.*, m.name as mosque_name, m.address as mosque_address
                FROM events e
                LEFT JOIN mosques m ON e.mosque_id = m.id
                WHERE e.id = ? AND e.is_active = 1
            ''', (event_id,)).fetchone()
            conn.close()
            
            if event is None:
                return jsonify({'error': 'Event not found'}), 404
            
            return jsonify(dict(event))
        except Exception as e:
            logger.error(f"Error fetching event {event_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/news', methods=['GET'])
    def get_news():
        """Get all published news"""
        try:
            conn = get_db_connection()
            news = conn.execute('''
                SELECT * FROM news 
                WHERE status = 'published' 
                ORDER BY published_at DESC
            ''').fetchall()
            conn.close()
            
            return jsonify([dict(article) for article in news])
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/news/<int:news_id>', methods=['GET'])
    def get_news_article(news_id):
        """Get specific news article by ID"""
        try:
            conn = get_db_connection()
            article = conn.execute('''
                SELECT * FROM news WHERE id = ? AND status = 'published'
            ''', (news_id,)).fetchone()
            conn.close()
            
            if article is None:
                return jsonify({'error': 'Article not found'}), 404
            
            return jsonify(dict(article))
        except Exception as e:
            logger.error(f"Error fetching news article {news_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ramadan/iftar-events', methods=['GET'])
    def get_iftar_events():
        """Get iftar events (filtered events)"""
        try:
            conn = get_db_connection()
            events = conn.execute('''
                SELECT e.*, m.name as mosque_name
                FROM events e
                LEFT JOIN mosques m ON e.mosque_id = m.id
                WHERE e.is_active = 1 AND e.event_type = 'community'
                ORDER BY e.event_date ASC, e.event_time ASC
            ''').fetchall()
            conn.close()
            
            return jsonify([dict(event) for event in events])
        except Exception as e:
            logger.error(f"Error fetching iftar events: {e}")
            return jsonify({'error': str(e)}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
