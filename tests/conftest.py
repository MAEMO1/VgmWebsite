"""
Pytest configuration and shared fixtures for VGM Website tests
"""

import pytest
import os
import tempfile
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Set test environment
os.environ['TESTING'] = 'True'
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
os.environ['WTF_CSRF_ENABLED'] = 'False'

@pytest.fixture(scope='session')
def app():
    """Create test app with test database"""
    from app_new import create_app
    from models_new import db
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Create database session"""
    from models_new import db
    with app.app_context():
        yield db.session

@pytest.fixture
def test_user(app, db_session):
    """Create test user"""
    from models_new import User
    
    user = User(
        email='test@example.com',
        first_name='Test',
        last_name='User',
        role='LID',
        is_active=True
    )
    user.set_password('testpassword')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_admin_user(app, db_session):
    """Create test admin user"""
    from models_new import User
    
    user = User(
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        role='BEHEERDER',
        is_active=True
    )
    user.set_password('adminpassword')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_mosque(app, db_session):
    """Create test mosque"""
    from models_new import Mosque
    
    mosque = Mosque(
        name='Test Mosque',
        address='Test Address 123',
        phone='+32 9 123 45 67',
        email='test@mosque.be',
        capacity=200,
        established_year=2020,
        imam_name='Test Imam',
        description='Test mosque description',
        latitude=51.0543,
        longitude=3.7174,
        is_active=True
    )
    db_session.add(mosque)
    db_session.commit()
    return mosque

@pytest.fixture
def test_event(app, db_session, test_mosque):
    """Create test event"""
    from models_new import Event
    
    event = Event(
        mosque_id=test_mosque.id,
        title='Test Event',
        description='Test event description',
        event_date=datetime.now().date() + timedelta(days=1),
        event_time=datetime.now().time(),
        event_type='event',
        is_active=True
    )
    db_session.add(event)
    db_session.commit()
    return event

@pytest.fixture
def test_news_article(app, db_session, test_user):
    """Create test news article"""
    from models_new import BlogPost
    
    article = BlogPost(
        title='Test News',
        content='Test news content',
        excerpt='Test excerpt',
        author_id=test_user.id,
        category='news',
        status='published',
        published_at=datetime.now()
    )
    db_session.add(article)
    db_session.commit()
    return article

@pytest.fixture
def auth_headers(app, test_user):
    """Create authentication headers for test user"""
    with app.app_context():
        from app_new import generate_jwt_token
        token = generate_jwt_token(test_user.id, test_user.role, 'access')
        return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def admin_auth_headers(app, test_admin_user):
    """Create authentication headers for admin user"""
    with app.app_context():
        from app_new import generate_jwt_token
        token = generate_jwt_token(test_admin_user.id, test_admin_user.role, 'access')
        return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    import shutil
    shutil.rmtree(temp_dir)

@pytest.fixture(autouse=True)
def cleanup_database(app):
    """Clean up database after each test"""
    from models_new import db
    
    with app.app_context():
        # Clear all tables
        db.session.rollback()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
