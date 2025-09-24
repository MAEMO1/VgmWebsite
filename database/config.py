# Database configuration for VGM Website
# This file contains database connection settings and utilities

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://vgm_user:vgm_password@localhost:5432/vgm_database')

# For development/testing, use SQLite
if os.getenv('FLASK_ENV') == 'development':
    DATABASE_URL = 'sqlite:///vgm_website.db'

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool if 'sqlite' in DATABASE_URL else None,
    connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Database utility functions
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with schema"""
    try:
        # Import all models to ensure they are registered
        from models import User, Mosque, MosqueFeature, PrayerTime, Event, BoardMember, MosqueHistory, MediaFile, BlogPost, JanazahEvent, Donation, FundraisingCampaign, ContactSubmission, UserSession
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Load initial data if tables are empty
        db = SessionLocal()
        try:
            # Check if mosques table is empty
            result = db.execute(text("SELECT COUNT(*) FROM mosques")).scalar()
            if result == 0:
                # Load initial data from schema.sql
                load_initial_data(db)
                logging.info("Initial data loaded successfully")
        finally:
            db.close()
            
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise

def load_initial_data(db):
    """Load initial data from schema.sql"""
    try:
        # Read and execute schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        for statement in statements:
            if statement.upper().startswith(('INSERT', 'CREATE', 'ALTER')):
                db.execute(text(statement))
        
        db.commit()
        logging.info("Initial data loaded from schema.sql")
    except Exception as e:
        logging.error(f"Error loading initial data: {e}")
        db.rollback()
        raise

def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).scalar()
        db.close()
        return result == 1
    except Exception as e:
        logging.error(f"Database connection test failed: {e}")
        return False

# Database health check
def health_check():
    """Database health check for monitoring"""
    try:
        db = SessionLocal()
        # Test basic query
        result = db.execute(text("SELECT COUNT(*) FROM mosques")).scalar()
        db.close()
        return {
            'status': 'healthy',
            'mosques_count': result,
            'database_url': DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'local'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'database_url': DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'local'
        }
