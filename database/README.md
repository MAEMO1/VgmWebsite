# VGM Website Database Setup

This document explains how to set up and manage the database for the VGM Website.

## Database Schema

The VGM Website uses a PostgreSQL database with the following main tables:

### Core Tables
- **users** - User authentication and management
- **mosques** - Mosque information and details
- **mosque_features** - Features available at each mosque
- **prayer_times** - Daily prayer times for each mosque
- **events** - Events and activities at mosques
- **board_members** - Board members of each mosque
- **mosque_history** - Historical events for each mosque

### Content Tables
- **blog_posts** - News articles and announcements
- **janazah_events** - Funeral prayer announcements
- **donations** - Donation records
- **fundraising_campaigns** - Fundraising campaigns
- **contact_submissions** - Contact form submissions
- **media_files** - Photos, videos, and documents

### System Tables
- **user_sessions** - User session management

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- PostgreSQL 12+ (or SQLite for development)
- pip or poetry for package management

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Configuration

#### Development (SQLite)
```bash
export FLASK_ENV=development
export DATABASE_URL=sqlite:///vgm_website.db
```

#### Production (PostgreSQL)
```bash
export DATABASE_URL=postgresql://username:password@host:port/database
```

### 4. Initialize Database

#### Option 1: Using Migration Script
```bash
python migrate.py --action migrate
```

#### Option 2: Manual Setup
```bash
# Create tables
python migrate.py --action create

# Load initial data
python migrate.py --action load-data
```

### 5. Verify Setup
```bash
python migrate.py --action check
```

## Database Management

### Migration Commands

```bash
# Full migration (create tables + load data)
python migrate.py --action migrate

# Create tables only
python migrate.py --action create

# Load initial data only
python migrate.py --action load-data

# Drop all tables (destructive!)
python migrate.py --action drop --force

# Check database status
python migrate.py --action check
```

### Health Checks

The application provides health check endpoints:

- `/health` - Basic application health
- `/health/db` - Database health with statistics

### Sample Data

The initial data includes:
- 6 sample mosques in Gent
- Admin user (email: admin@vgm-gent.be, password: admin123)
- Sample prayer times
- Sample events
- Board members for each mosque
- Historical events

## Database Schema Details

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) DEFAULT 'user',
    mosque_id INTEGER REFERENCES mosques(id),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Mosques Table
```sql
CREATE TABLE mosques (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    capacity INTEGER,
    established_year INTEGER,
    imam_name VARCHAR(255),
    description TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if PostgreSQL is running
   - Verify connection string
   - Check firewall settings

2. **Permission Denied**
   - Ensure user has CREATE privileges
   - Check database permissions

3. **Table Already Exists**
   - Use `--action drop` to remove existing tables
   - Or modify the migration script

### Logs

Check application logs for detailed error messages:
```bash
tail -f logs/vgm_website.log
```

### Database Backup

```bash
# PostgreSQL backup
pg_dump vgm_database > backup.sql

# PostgreSQL restore
psql vgm_database < backup.sql
```

## Production Considerations

1. **Security**
   - Use strong passwords
   - Enable SSL connections
   - Regular security updates

2. **Performance**
   - Add database indexes
   - Monitor query performance
   - Use connection pooling

3. **Backup**
   - Regular automated backups
   - Test restore procedures
   - Offsite backup storage

4. **Monitoring**
   - Database health checks
   - Performance metrics
   - Error logging

## Support

For database-related issues:
1. Check the logs
2. Verify configuration
3. Test database connection
4. Contact system administrator
