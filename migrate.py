#!/usr/bin/env python3
"""
Database migration script for VGM Website
This script handles database initialization and migrations
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.config import DATABASE_URL, engine, SessionLocal
from models import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all database tables"""
    try:
        logger.info("Creating database tables...")
        db.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def drop_tables():
    """Drop all database tables"""
    try:
        logger.info("Dropping database tables...")
        db.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
        return True
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        return False

def load_initial_data():
    """Load initial data from schema.sql"""
    try:
        db = SessionLocal()
        try:
            # Read schema.sql file
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            executed_count = 0
            
            for statement in statements:
                if statement.upper().startswith(('INSERT', 'CREATE', 'ALTER')):
                    try:
                        db.execute(text(statement))
                        executed_count += 1
                    except SQLAlchemyError as e:
                        logger.warning(f"Skipping statement due to error: {e}")
                        continue
            
            db.commit()
            logger.info(f"Initial data loaded successfully ({executed_count} statements executed)")
            return True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error loading initial data: {e}")
        return False

def check_database_connection():
    """Check if database connection is working"""
    try:
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT 1")).scalar()
            logger.info("Database connection successful")
            return result == 1
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def get_table_count():
    """Get count of records in main tables"""
    try:
        db = SessionLocal()
        try:
            tables = ['users', 'mosques', 'events', 'prayer_times', 'board_members']
            counts = {}
            
            for table in tables:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    counts[table] = result
                except SQLAlchemyError:
                    counts[table] = 0
            
            return counts
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error getting table counts: {e}")
        return {}

def main():
    """Main migration function"""
    logger.info("Starting database migration...")
    
    # Check database connection
    if not check_database_connection():
        logger.error("Cannot connect to database. Exiting.")
        return False
    
    # Create tables
    if not create_tables():
        logger.error("Failed to create tables. Exiting.")
        return False
    
    # Load initial data
    if not load_initial_data():
        logger.error("Failed to load initial data. Exiting.")
        return False
    
    # Show table counts
    counts = get_table_count()
    logger.info("Database migration completed successfully!")
    logger.info("Table counts:")
    for table, count in counts.items():
        logger.info(f"  {table}: {count} records")
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='VGM Website Database Migration')
    parser.add_argument('--action', choices=['migrate', 'create', 'drop', 'load-data', 'check'], 
                       default='migrate', help='Action to perform')
    parser.add_argument('--force', action='store_true', help='Force action without confirmation')
    
    args = parser.parse_args()
    
    if args.action == 'migrate':
        success = main()
        sys.exit(0 if success else 1)
    elif args.action == 'create':
        success = create_tables()
        sys.exit(0 if success else 1)
    elif args.action == 'drop':
        if not args.force:
            confirm = input("Are you sure you want to drop all tables? (yes/no): ")
            if confirm.lower() != 'yes':
                logger.info("Operation cancelled")
                sys.exit(0)
        success = drop_tables()
        sys.exit(0 if success else 1)
    elif args.action == 'load-data':
        success = load_initial_data()
        sys.exit(0 if success else 1)
    elif args.action == 'check':
        success = check_database_connection()
        if success:
            counts = get_table_count()
            logger.info("Database status: OK")
            logger.info("Table counts:")
            for table, count in counts.items():
                logger.info(f"  {table}: {count} records")
        sys.exit(0 if success else 1)
