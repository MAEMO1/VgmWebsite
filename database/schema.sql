-- Database schema for VGM Website
-- This file contains the SQL schema for all tables

-- Users table for authentication and user management
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) DEFAULT 'user', -- 'admin', 'mosque_admin', 'user'
    mosque_id INTEGER REFERENCES mosques(id),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mosques table
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

-- Mosque features table
CREATE TABLE mosque_features (
    id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
    feature_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prayer times table
CREATE TABLE prayer_times (
    id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    fajr TIME NOT NULL,
    dhuhr TIME NOT NULL,
    asr TIME NOT NULL,
    maghrib TIME NOT NULL,
    isha TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(mosque_id, date)
);

-- Events table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    event_time TIME NOT NULL,
    event_type VARCHAR(50) DEFAULT 'event', -- 'prayer', 'event', 'lecture', 'community'
    is_recurring BOOLEAN DEFAULT false,
    recurring_pattern VARCHAR(50), -- 'weekly', 'monthly', 'yearly'
    max_attendees INTEGER,
    current_attendees INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Board members table
CREATE TABLE board_members (
    id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    position VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    bio TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mosque history table
CREATE TABLE mosque_history (
    id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
    year VARCHAR(10) NOT NULL,
    event_title VARCHAR(255) NOT NULL,
    event_description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Media files table
CREATE TABLE media_files (
    id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- 'image', 'video', 'document'
    file_size INTEGER,
    mime_type VARCHAR(100),
    description TEXT,
    uploaded_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- News/Blog posts table
CREATE TABLE blog_posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    author_id INTEGER REFERENCES users(id),
    category VARCHAR(100) DEFAULT 'news', -- 'news', 'announcement', 'reflection'
    featured_image VARCHAR(500),
    is_published BOOLEAN DEFAULT false,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Janazah (funeral prayers) table
CREATE TABLE janazah_events (
    id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
    deceased_name VARCHAR(255) NOT NULL,
    deceased_age INTEGER,
    deceased_date DATE NOT NULL,
    prayer_date DATE NOT NULL,
    prayer_time TIME NOT NULL,
    burial_location VARCHAR(255),
    contact_person VARCHAR(255),
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),
    notes TEXT,
    is_public BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Donations table
CREATE TABLE donations (
    id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
    campaign_id INTEGER REFERENCES fundraising_campaigns(id),
    donor_name VARCHAR(255),
    donor_email VARCHAR(255),
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50), -- 'stripe', 'paypal', 'bank_transfer'
    payment_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'completed', 'failed'
    transaction_id VARCHAR(255),
    is_anonymous BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fundraising campaigns table
CREATE TABLE fundraising_campaigns (
    id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    target_amount DECIMAL(10, 2),
    current_amount DECIMAL(10, 2) DEFAULT 0,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contact form submissions table
CREATE TABLE contact_submissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    mosque_id INTEGER REFERENCES mosques(id),
    status VARCHAR(50) DEFAULT 'new', -- 'new', 'in_progress', 'resolved'
    responded_by INTEGER REFERENCES users(id),
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions table for authentication
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_mosques_active ON mosques(is_active);
CREATE INDEX idx_events_mosque_date ON events(mosque_id, event_date);
CREATE INDEX idx_prayer_times_mosque_date ON prayer_times(mosque_id, date);
CREATE INDEX idx_blog_posts_published ON blog_posts(is_published, published_at);
CREATE INDEX idx_janazah_events_date ON janazah_events(prayer_date);
CREATE INDEX idx_donations_mosque ON donations(mosque_id);
CREATE INDEX idx_contact_submissions_status ON contact_submissions(status);

-- Insert initial admin user (password: admin123)
INSERT INTO users (email, password_hash, first_name, last_name, role) 
VALUES ('admin@vgm-gent.be', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8QzQz2O', 'Admin', 'User', 'admin');

-- Insert sample mosques data
INSERT INTO mosques (name, address, phone, email, website, capacity, established_year, imam_name, description, latitude, longitude) VALUES
('Moskee Salahaddien', 'Sint-Pietersnieuwstraat 120, 9000 Gent', '+32 9 123 45 67', 'info@salahaddien.be', 'www.salahaddien.be', 500, 1985, 'Sheikh Ahmed Al-Mansouri', 'Moskee Salahaddien is een van de oudste en grootste moskeeën in Gent. Opgericht in 1985, heeft deze moskee een rijke geschiedenis van gemeenschapsopbouw en religieuze educatie.', 51.0543, 3.7174),
('Moskee Al-Fath', 'Korte Meer 11, 9000 Gent', '+32 9 234 56 78', 'info@alfath.be', 'www.alfath.be', 300, 1992, 'Sheikh Ibrahim Al-Turk', 'Moskee Al-Fath is gelegen in het centrum van Gent en richt zich op educatie en gemeenschapsopbouw.', 51.0538, 3.7251),
('Moskee Selimiye', 'Kasteellaan 15, 9000 Gent', '+32 9 345 67 89', 'info@selimiye.be', 'www.selimiye.be', 200, 1998, 'Sheikh Mustafa Al-Bosniak', 'Moskee Selimiye is een kleine maar actieve moskee met sterke gemeenschapsbanden.', 51.0569, 3.7198),
('Moskee Al-Noor', 'Bruggestraat 45, 9000 Gent', '+32 9 456 78 90', 'info@alnoor.be', 'www.alnoor.be', 400, 2005, 'Sheikh Abdul Rahman Al-Pakistani', 'Moskee Al-Noor is een moderne moskee met uitgebreide faciliteiten en diverse activiteiten.', 51.0521, 3.7302),
('Moskee Al-Hidayah', 'Kortrijksesteenweg 200, 9000 Gent', '+32 9 567 89 01', 'info@alhidayah.be', 'www.alhidayah.be', 350, 2010, 'Sheikh Omar Al-Moroccan', 'Moskee Al-Hidayah richt zich op jongeren en educatieve programma''s.', 51.0489, 3.7123),
('Moskee Al-Iman', 'Gentsesteenweg 75, 9000 Gent', '+32 9 678 90 12', 'info@aliman.be', 'www.aliman.be', 250, 2015, 'Sheikh Yusuf Al-Somali', 'Moskee Al-Iman is een gemeenschapsgerichte moskee met sterke sociale programma''s.', 51.0512, 3.7089);

-- Insert mosque features
INSERT INTO mosque_features (mosque_id, feature_name) VALUES
(1, 'Vrouwenafdeling'), (1, 'Parking (50 plaatsen)'), (1, 'Kinderopvang'), (1, 'Bibliotheek'), (1, 'Sportzaal'), (1, 'Cafetaria'), (1, 'Winkel'), (1, 'Gebedsruimte voor vrouwen'),
(2, 'Vrouwenafdeling'), (2, 'Parking (20 plaatsen)'), (2, 'Kinderopvang'), (2, 'Bibliotheek'), (2, 'Computerruimte'),
(3, 'Vrouwenafdeling'), (3, 'Parking (15 plaatsen)'), (3, 'Bibliotheek'),
(4, 'Vrouwenafdeling'), (4, 'Parking (40 plaatsen)'), (4, 'Kinderopvang'), (4, 'Bibliotheek'), (4, 'Sportzaal'), (4, 'Computerruimte'), (4, 'Cafetaria'),
(5, 'Vrouwenafdeling'), (5, 'Parking (30 plaatsen)'), (5, 'Kinderopvang'), (5, 'Bibliotheek'), (5, 'Computerruimte'), (5, 'Jongerencentrum'),
(6, 'Vrouwenafdeling'), (6, 'Parking (25 plaatsen)'), (6, 'Bibliotheek'), (6, 'Sociale dienstverlening');

-- Insert sample prayer times for today
INSERT INTO prayer_times (mosque_id, date, fajr, dhuhr, asr, maghrib, isha) VALUES
(1, CURRENT_DATE, '05:45', '12:30', '15:45', '18:15', '19:45'),
(2, CURRENT_DATE, '05:50', '12:35', '15:50', '18:20', '19:50'),
(3, CURRENT_DATE, '05:40', '12:25', '15:40', '18:10', '19:40'),
(4, CURRENT_DATE, '05:55', '12:40', '15:55', '18:25', '19:55'),
(5, CURRENT_DATE, '05:48', '12:33', '15:48', '18:18', '19:48'),
(6, CURRENT_DATE, '05:42', '12:27', '15:42', '18:12', '19:42');

-- Insert sample events
INSERT INTO events (mosque_id, title, description, event_date, event_time, event_type) VALUES
(1, 'Vrijdaggebed', 'Wekelijks vrijdaggebed met preek', CURRENT_DATE + INTERVAL '1 day', '13:00', 'prayer'),
(1, 'Koranlessen voor kinderen', 'Wekelijkse Koranlessen voor kinderen van 6-12 jaar', CURRENT_DATE + INTERVAL '2 days', '16:00', 'lecture'),
(2, 'Arabische lessen', 'Wekelijkse Arabische lessen voor volwassenen', CURRENT_DATE + INTERVAL '3 days', '14:00', 'lecture'),
(3, 'Spirituele lezing', 'Maandelijkse spirituele lezing', CURRENT_DATE + INTERVAL '5 days', '19:00', 'lecture'),
(4, 'Sportactiviteiten', 'Wekelijkse sportactiviteiten voor jongeren', CURRENT_DATE + INTERVAL '2 days', '15:00', 'event'),
(5, 'Jongerenactiviteiten', 'Wekelijkse jongerenactiviteiten', CURRENT_DATE + INTERVAL '4 days', '16:00', 'event'),
(6, 'Sociale ondersteuning', 'Maandelijkse sociale ondersteuning sessie', CURRENT_DATE + INTERVAL '6 days', '14:00', 'community');

-- Insert board members
INSERT INTO board_members (mosque_id, name, position, email) VALUES
(1, 'Dr. Mohammed Al-Hassan', 'Voorzitter', 'voorzitter@salahaddien.be'),
(1, 'Fatima Al-Zahra', 'Secretaris', 'secretaris@salahaddien.be'),
(1, 'Ahmed Al-Mansouri', 'Penningmeester', 'penningmeester@salahaddien.be'),
(1, 'Aisha Al-Rashid', 'Bestuurslid', 'bestuur@salahaddien.be'),
(2, 'Hassan Al-Mahmoud', 'Voorzitter', 'voorzitter@alfath.be'),
(2, 'Amina Al-Hassan', 'Secretaris', 'secretaris@alfath.be'),
(3, 'Mehmet Al-Bosniak', 'Voorzitter', 'voorzitter@selimiye.be'),
(3, 'Fatima Al-Bosniak', 'Secretaris', 'secretaris@selimiye.be'),
(4, 'Abdul Rahman Al-Pakistani', 'Voorzitter', 'voorzitter@alnoor.be'),
(4, 'Aisha Al-Pakistani', 'Secretaris', 'secretaris@alnoor.be'),
(5, 'Omar Al-Moroccan', 'Voorzitter', 'voorzitter@alhidayah.be'),
(5, 'Khadija Al-Moroccan', 'Secretaris', 'secretaris@alhidayah.be'),
(6, 'Yusuf Al-Somali', 'Voorzitter', 'voorzitter@aliman.be'),
(6, 'Halima Al-Somali', 'Secretaris', 'secretaris@aliman.be');

-- Insert mosque history
INSERT INTO mosque_history (mosque_id, year, event_title, event_description) VALUES
(1, '1985', 'Oprichting', 'Moskee Salahaddien werd opgericht door de eerste generatie Marokkaanse immigranten in Gent.'),
(1, '1992', 'Uitbreiding', 'Eerste uitbreiding van de moskee met een vrouwenafdeling en kinderopvang.'),
(1, '2005', 'Renovatie', 'Grote renovatie en modernisering van alle faciliteiten.'),
(1, '2018', 'Nieuwe Imam', 'Sheikh Ahmed Al-Mansouri werd aangesteld als nieuwe imam.'),
(2, '1992', 'Oprichting', 'Moskee Al-Fath werd opgericht door de Turkse gemeenschap in Gent.'),
(2, '2000', 'Uitbreiding', 'Uitbreiding met vrouwenafdeling en educatieve faciliteiten.'),
(3, '1998', 'Oprichting', 'Moskee Selimiye werd opgericht door de Bosnische gemeenschap in Gent.'),
(3, '2010', 'Renovatie', 'Renovatie van de gebedsruimte en faciliteiten.'),
(4, '2005', 'Oprichting', 'Moskee Al-Noor werd opgericht door de Pakistaanse gemeenschap in Gent.'),
(4, '2015', 'Uitbreiding', 'Uitbreiding met sportzaal en computerruimte.'),
(5, '2010', 'Oprichting', 'Moskee Al-Hidayah werd opgericht door de Marokkaanse gemeenschap in Gent.'),
(5, '2020', 'Jongerencentrum', 'Opening van het jongerencentrum.'),
(6, '2015', 'Oprichting', 'Moskee Al-Iman werd opgericht door de Somalische gemeenschap in Gent.'),
(6, '2022', 'Sociale dienstverlening', 'Start van sociale dienstverlening programma.');
