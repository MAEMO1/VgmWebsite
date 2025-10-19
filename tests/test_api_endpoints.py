"""
Backend API endpoint tests for VGM Website
Tests for authentication, mosques, events, news, analytics, and file uploads
"""

import pytest
import json
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash

# Import the app and models
from app_new import create_app
from models_new import db, User, Mosque, Event, BlogPost, MediaFile, Donation, FundraisingCampaign

@pytest.fixture
def app():
    """Create test app with test database"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create test user"""
    with app.app_context():
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='LID',
            is_active=True
        )
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_mosque(app):
    """Create test mosque"""
    with app.app_context():
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
        db.session.add(mosque)
        db.session.commit()
        return mosque

@pytest.fixture
def auth_headers(app, test_user):
    """Create authentication headers"""
    with app.app_context():
        # Generate JWT token
        from app_new import generate_jwt_token
        token = generate_jwt_token(test_user.id, test_user.role, 'access')
        return {'Authorization': f'Bearer {token}'}

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health endpoint returns 200"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'timestamp' in data

class TestCSRFEndpoint:
    """Test CSRF token endpoint"""
    
    def test_csrf_token(self, client):
        """Test CSRF token endpoint"""
        response = client.get('/api/csrf')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'csrf_token' in data

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login', json={
            'email': 'wrong@example.com',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Invalid credentials'
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Email and password required'
    
    def test_register_success(self, client):
        """Test successful registration"""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '+32 9 123 45 67'
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['email'] == 'newuser@example.com'
    
    def test_register_existing_user(self, client, test_user):
        """Test registration with existing email"""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'password',
            'first_name': 'Test',
            'last_name': 'User'
        })
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['error'] == 'User already exists'
    
    def test_register_missing_fields(self, client):
        """Test registration with missing fields"""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'password'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'All required fields must be provided'
    
    def test_refresh_token_success(self, client, test_user):
        """Test successful token refresh"""
        # First login to get refresh token
        login_response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        login_data = json.loads(login_response.data)
        refresh_token = login_data['refresh_token']
        
        # Use refresh token
        response = client.post('/api/auth/refresh', json={
            'refresh_token': refresh_token
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'user' in data
    
    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token"""
        response = client.post('/api/auth/refresh', json={
            'refresh_token': 'invalid_token'
        })
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Invalid refresh token'

class TestMosquesAPI:
    """Test mosques endpoints"""
    
    def test_get_mosques(self, client, test_mosque):
        """Test get all mosques"""
        response = client.get('/api/mosques')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == 'Test Mosque'
    
    def test_get_mosque_by_id(self, client, test_mosque):
        """Test get specific mosque"""
        response = client.get(f'/api/mosques/{test_mosque.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Test Mosque'
        assert data['id'] == test_mosque.id
    
    def test_get_nonexistent_mosque(self, client):
        """Test get non-existent mosque"""
        response = client.get('/api/mosques/999')
        assert response.status_code == 404

class TestEventsAPI:
    """Test events endpoints"""
    
    def test_get_events(self, client, test_mosque):
        """Test get all events"""
        # Create test event
        with client.application.app_context():
            event = Event(
                mosque_id=test_mosque.id,
                title='Test Event',
                description='Test event description',
                event_date=datetime.now().date() + timedelta(days=1),
                event_time=datetime.now().time(),
                event_type='event',
                is_active=True
            )
            db.session.add(event)
            db.session.commit()
        
        response = client.get('/api/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['title'] == 'Test Event'

class TestNewsAPI:
    """Test news endpoints"""
    
    def test_get_news(self, client, test_user):
        """Test get all news"""
        # Create test news article
        with client.application.app_context():
            news = BlogPost(
                title='Test News',
                content='Test news content',
                excerpt='Test excerpt',
                author_id=test_user.id,
                category='news',
                status='published',
                published_at=datetime.now()
            )
            db.session.add(news)
            db.session.commit()
        
        response = client.get('/api/news')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['title'] == 'Test News'

class TestAnalyticsAPI:
    """Test analytics endpoints"""
    
    def test_analytics_summary_unauthorized(self, client):
        """Test analytics summary without auth"""
        response = client.get('/api/analytics/summary')
        assert response.status_code == 401
    
    def test_analytics_summary_authorized(self, client, auth_headers):
        """Test analytics summary with auth"""
        response = client.get('/api/analytics/summary', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_users' in data
        assert 'total_mosques' in data
        assert 'total_events' in data
        assert 'total_donations' in data
    
    def test_analytics_reports_unauthorized(self, client):
        """Test analytics reports without auth"""
        response = client.get('/api/analytics/reports')
        assert response.status_code == 401
    
    def test_analytics_reports_authorized(self, client, auth_headers):
        """Test analytics reports with auth"""
        response = client.get('/api/analytics/reports', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)

class TestPaymentsAPI:
    """Test payment endpoints"""
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_success(self, mock_create, client):
        """Test successful payment intent creation"""
        mock_intent = MagicMock()
        mock_intent.client_secret = 'pi_test_secret'
        mock_intent.id = 'pi_test_id'
        mock_create.return_value = mock_intent
        
        response = client.post('/api/payments/create-payment-intent', json={
            'amount': 50.00,
            'currency': 'eur',
            'donation_type': 'general',
            'mosque_id': 1
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'client_secret' in data
        assert 'payment_intent_id' in data
    
    def test_create_payment_intent_invalid_amount(self, client):
        """Test payment intent with invalid amount"""
        response = client.post('/api/payments/create-payment-intent', json={
            'amount': -10.00,
            'currency': 'eur'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Valid amount required'
    
    def test_create_payment_intent_missing_amount(self, client):
        """Test payment intent with missing amount"""
        response = client.post('/api/payments/create-payment-intent', json={
            'currency': 'eur'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Valid amount required'

class TestFileUploadAPI:
    """Test file upload endpoints"""
    
    def test_upload_file_unauthorized(self, client):
        """Test file upload without auth"""
        response = client.post('/api/upload')
        assert response.status_code == 401
    
    def test_upload_file_no_file(self, client, auth_headers):
        """Test file upload without file"""
        response = client.post('/api/upload', headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'No file provided'
    
    @patch('app_new.allowed_file')
    @patch('app_new.get_file_size')
    def test_upload_file_success(self, mock_size, mock_allowed, client, auth_headers):
        """Test successful file upload"""
        mock_allowed.return_value = True
        mock_size.return_value = 1024  # 1KB
        
        # Create a mock file
        data = {
            'file': (io.BytesIO(b'test content'), 'test.txt'),
            'description': 'Test file',
            'is_public': 'true'
        }
        
        response = client.post('/api/upload', 
                             data=data,
                             headers=auth_headers,
                             content_type='multipart/form-data')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'id' in data
        assert 'filename' in data
        assert 'file_size' in data

class TestSearchAPI:
    """Test search endpoints"""
    
    def test_search_no_query(self, client):
        """Test search without query"""
        response = client.get('/api/search')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Search query required'
    
    def test_search_with_query(self, client, test_mosque):
        """Test search with query"""
        response = client.get('/api/search?q=Test')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'mosques' in data
        assert 'events' in data
        assert 'news' in data
        assert 'total' in data

class TestWebhooksAPI:
    """Test webhook endpoints"""
    
    def test_stripe_webhook_no_signature(self, client):
        """Test Stripe webhook without signature"""
        response = client.post('/api/webhooks/stripe', 
                              data='{"type": "test"}',
                              content_type='application/json')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['error'] == 'Webhook not configured'
    
    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_success(self, mock_construct, client):
        """Test successful Stripe webhook"""
        mock_construct.return_value = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_id'
                }
            }
        }
        
        with patch.dict(os.environ, {'STRIPE_WEBHOOK_SECRET': 'whsec_test'}):
            response = client.post('/api/webhooks/stripe',
                                 data='{"type": "payment_intent.succeeded"}',
                                 content_type='application/json',
                                 headers={'Stripe-Signature': 'test_signature'})
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'

class TestRateLimiting:
    """Test rate limiting"""
    
    def test_login_rate_limit(self, client, test_user):
        """Test login rate limiting"""
        # Make multiple login attempts
        for i in range(6):  # Should be limited at 5 per minute
            response = client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'wrongpassword'  # Wrong password to avoid success
            })
        
        # The 6th attempt should be rate limited
        assert response.status_code == 429

class TestRBACIntegration:
    """Test RBAC integration"""
    
    def test_analytics_without_capability(self, client, test_user):
        """Test analytics access without proper capability"""
        # Create user with LID role (no analytics capability)
        with client.application.app_context():
            user = User(
                email='lid@example.com',
                first_name='Lid',
                last_name='User',
                role='LID',  # LID role doesn't have analytics.view_platform
                is_active=True
            )
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            # Generate token for LID user
            from app_new import generate_jwt_token
            token = generate_jwt_token(user.id, user.role, 'access')
            headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/analytics/summary', headers=headers)
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['error'] == 'Insufficient permissions'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
