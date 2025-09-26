"""
OpenAPI Schema Generator for VGM Website
Generates OpenAPI 3.0 specification for Flask-RESTX API
"""

from flask_restx import Api, Resource, fields, Namespace
from flask import Flask
import json
from datetime import datetime

def create_api_schema():
    """Create OpenAPI schema for VGM Website API"""
    
    # Create Flask app for schema generation
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    
    api = Api(
        app,
        version='1.0.0',
        title='VGM Website API',
        description='API for Vereniging van Gentse Moskeeën Website',
        doc='/docs/',
        prefix='/api'
    )
    
    # Define namespaces
    auth_ns = Namespace('auth', description='Authentication operations')
    mosques_ns = Namespace('mosques', description='Mosque operations')
    events_ns = Namespace('events', description='Event operations')
    ramadan_ns = Namespace('ramadan', description='Ramadan operations')
    donations_ns = Namespace('donations', description='Donation operations')
    news_ns = Namespace('news', description='News operations')
    
    api.add_namespace(auth_ns)
    api.add_namespace(mosques_ns)
    api.add_namespace(events_ns)
    api.add_namespace(ramadan_ns)
    api.add_namespace(donations_ns)
    api.add_namespace(news_ns)
    
    # Common field models
    error_model = api.model('Error', {
        'error': fields.String(required=True, description='Error message'),
        'code': fields.Integer(description='Error code')
    })
    
    success_model = api.model('Success', {
        'message': fields.String(required=True, description='Success message'),
        'data': fields.Raw(description='Response data')
    })
    
    # Auth models
    login_model = api.model('Login', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password'),
        'remember': fields.Boolean(description='Remember user')
    })
    
    register_model = api.model('Register', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password'),
        'first_name': fields.String(required=True, description='First name'),
        'last_name': fields.String(required=True, description='Last name'),
        'phone': fields.String(description='Phone number'),
        'role': fields.String(description='User role'),
        'mosque_id': fields.Integer(description='Mosque ID')
    })
    
    user_model = api.model('User', {
        'id': fields.Integer(description='User ID'),
        'email': fields.String(description='User email'),
        'first_name': fields.String(description='First name'),
        'last_name': fields.String(description='Last name'),
        'phone': fields.String(description='Phone number'),
        'role': fields.String(description='User role'),
        'mosque_id': fields.Integer(description='Mosque ID'),
        'is_active': fields.Boolean(description='Is active'),
        'email_verified': fields.Boolean(description='Email verified'),
        'created_at': fields.DateTime(description='Created at')
    })
    
    # Mosque models
    mosque_model = api.model('Mosque', {
        'id': fields.Integer(description='Mosque ID'),
        'name': fields.String(description='Mosque name'),
        'address': fields.String(description='Mosque address'),
        'phone': fields.String(description='Phone number'),
        'email': fields.String(description='Email address'),
        'website': fields.String(description='Website URL'),
        'capacity': fields.Integer(description='Capacity'),
        'established_year': fields.Integer(description='Established year'),
        'imam_name': fields.String(description='Imam name'),
        'description': fields.String(description='Description'),
        'latitude': fields.Float(description='Latitude'),
        'longitude': fields.Float(description='Longitude'),
        'is_active': fields.Boolean(description='Is active'),
        'created_at': fields.DateTime(description='Created at'),
        'updated_at': fields.DateTime(description='Updated at')
    })
    
    # Event models
    event_model = api.model('Event', {
        'id': fields.Integer(description='Event ID'),
        'mosque_id': fields.Integer(description='Mosque ID'),
        'title': fields.String(description='Event title'),
        'description': fields.String(description='Event description'),
        'event_date': fields.Date(description='Event date'),
        'event_time': fields.String(description='Event time'),
        'event_type': fields.String(description='Event type'),
        'is_recurring': fields.Boolean(description='Is recurring'),
        'recurring_pattern': fields.String(description='Recurring pattern'),
        'max_attendees': fields.Integer(description='Max attendees'),
        'current_attendees': fields.Integer(description='Current attendees'),
        'is_active': fields.Boolean(description='Is active'),
        'created_by': fields.Integer(description='Created by user ID'),
        'created_at': fields.DateTime(description='Created at'),
        'updated_at': fields.DateTime(description='Updated at')
    })
    
    # Ramadan models
    iftar_event_model = api.model('IftarEvent', {
        'id': fields.Integer(description='Iftar event ID'),
        'mosque_id': fields.Integer(description='Mosque ID'),
        'date': fields.Date(description='Event date'),
        'start_time': fields.String(description='Start time'),
        'end_time': fields.String(description='End time'),
        'location': fields.String(description='Location'),
        'is_family_friendly': fields.Boolean(description='Is family friendly'),
        'capacity': fields.Integer(description='Capacity'),
        'created_at': fields.DateTime(description='Created at'),
        'updated_at': fields.DateTime(description='Updated at')
    })
    
    # Donation models
    donation_model = api.model('Donation', {
        'id': fields.Integer(description='Donation ID'),
        'mosque_id': fields.Integer(description='Mosque ID'),
        'campaign_id': fields.Integer(description='Campaign ID'),
        'donor_name': fields.String(description='Donor name'),
        'donor_email': fields.String(description='Donor email'),
        'amount': fields.Float(description='Donation amount'),
        'payment_method': fields.String(description='Payment method'),
        'payment_status': fields.String(description='Payment status'),
        'transaction_id': fields.String(description='Transaction ID'),
        'is_anonymous': fields.Boolean(description='Is anonymous'),
        'created_at': fields.DateTime(description='Created at')
    })
    
    # News models
    news_model = api.model('News', {
        'id': fields.Integer(description='News ID'),
        'title': fields.String(description='News title'),
        'content': fields.String(description='News content'),
        'excerpt': fields.String(description='News excerpt'),
        'author_id': fields.Integer(description='Author ID'),
        'category': fields.String(description='News category'),
        'featured_image': fields.String(description='Featured image URL'),
        'is_published': fields.Boolean(description='Is published'),
        'published_at': fields.DateTime(description='Published at'),
        'created_at': fields.DateTime(description='Created at'),
        'updated_at': fields.DateTime(description='Updated at')
    })
    
    # Auth endpoints
    @auth_ns.route('/login')
    class Login(Resource):
        @auth_ns.expect(login_model)
        @auth_ns.marshal_with(success_model)
        @auth_ns.marshal_with(error_model, code=400)
        @auth_ns.marshal_with(error_model, code=401)
        def post(self):
            """Login user"""
            pass
    
    @auth_ns.route('/register')
    class Register(Resource):
        @auth_ns.expect(register_model)
        @auth_ns.marshal_with(success_model)
        @auth_ns.marshal_with(error_model, code=400)
        def post(self):
            """Register new user"""
            pass
    
    @auth_ns.route('/me')
    class Me(Resource):
        @auth_ns.marshal_with(user_model)
        @auth_ns.marshal_with(error_model, code=401)
        def get(self):
            """Get current user information"""
            pass
    
    # Mosque endpoints
    @mosques_ns.route('/')
    class MosqueList(Resource):
        @mosques_ns.marshal_list_with(mosque_model)
        def get(self):
            """Get list of mosques"""
            pass
    
    @mosques_ns.route('/<int:mosque_id>')
    class MosqueDetail(Resource):
        @mosques_ns.marshal_with(mosque_model)
        @mosques_ns.marshal_with(error_model, code=404)
        def get(self, mosque_id):
            """Get mosque details"""
            pass
    
    # Event endpoints
    @events_ns.route('/')
    class EventList(Resource):
        @events_ns.marshal_list_with(event_model)
        def get(self):
            """Get list of events"""
            pass
    
    @events_ns.route('/<int:event_id>')
    class EventDetail(Resource):
        @events_ns.marshal_with(event_model)
        @events_ns.marshal_with(error_model, code=404)
        def get(self, event_id):
            """Get event details"""
            pass
    
    # Ramadan endpoints
    @ramadan_ns.route('/iftar-events')
    class IftarEventList(Resource):
        @ramadan_ns.marshal_list_with(iftar_event_model)
        def get(self):
            """Get list of iftar events"""
            pass
    
    # Donation endpoints
    @donations_ns.route('/')
    class DonationList(Resource):
        @donations_ns.marshal_list_with(donation_model)
        def get(self):
            """Get list of donations"""
            pass
    
    # News endpoints
    @news_ns.route('/')
    class NewsList(Resource):
        @news_ns.marshal_list_with(news_model)
        def get(self):
            """Get list of news articles"""
            pass
    
    @news_ns.route('/<int:news_id>')
    class NewsDetail(Resource):
        @news_ns.marshal_with(news_model)
        @news_ns.marshal_with(error_model, code=404)
        def get(self, news_id):
            """Get news article details"""
            pass
    
    return api

def generate_openapi_schema():
    """Generate OpenAPI 3.0 schema"""
    api = create_api_schema()
    
    # Get the OpenAPI schema within app context
    with api.app.app_context():
        schema = api.__schema__
    
    # Add additional OpenAPI 3.0 metadata
    schema.update({
        'openapi': '3.0.3',
        'info': {
            'title': 'VGM Website API',
            'version': '1.0.0',
            'description': 'API for Vereniging van Gentse Moskeeën Website',
            'contact': {
                'name': 'VGM Support',
                'email': 'support@vgm.be'
            }
        },
        'servers': [
            {
                'url': 'https://vgmwebsite-production.up.railway.app',
                'description': 'Production server'
            },
            {
                'url': 'http://localhost:5000',
                'description': 'Development server'
            }
        ],
        'tags': [
            {'name': 'auth', 'description': 'Authentication operations'},
            {'name': 'mosques', 'description': 'Mosque operations'},
            {'name': 'events', 'description': 'Event operations'},
            {'name': 'ramadan', 'description': 'Ramadan operations'},
            {'name': 'donations', 'description': 'Donation operations'},
            {'name': 'news', 'description': 'News operations'}
        ]
    })
    
    return schema

if __name__ == '__main__':
    schema = generate_openapi_schema()
    
    # Save to file
    with open('openapi.json', 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print("OpenAPI schema generated successfully!")
    print("Schema saved to: openapi.json")
