from werkzeug.security import generate_password_hash, check_password_hash

from main import app
from models import db, User, Mosque, PasswordResetToken, MosqueAccessRequest


def create_user(email: str, password: str, role: str = 'user', mosque_id: int | None = None) -> User:
    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        first_name='Test',
        last_name='User',
        role=role,
        mosque_id=mosque_id,
        is_active=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_password_reset_flow_returns_token_and_resets_password(client):
    with app.app_context():
        user = create_user('user@example.com', 'Password123')

    response = client.post(
        '/api/auth/request-password-reset',
        json={'email': 'user@example.com', 'locale': 'en'},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data

    with app.app_context():
        token_entry = PasswordResetToken.query.filter_by(user_id=user.id).first()
        assert token_entry is not None
        token_value = token_entry.token

    # Complete reset
    response = client.post(
        '/api/auth/reset-password',
        json={'token': token_value, 'new_password': 'NewSecret123!'},
    )
    assert response.status_code == 200
    assert response.get_json()['message']

    with app.app_context():
        db.session.refresh(user)
        assert check_password_hash(user.password_hash, 'NewSecret123!')
        token_entry = PasswordResetToken.query.filter_by(token=token_value).first()
        assert token_entry is not None
        assert token_entry.used_at is not None


def test_mosque_access_request_approval_promotes_user(client):
    with app.app_context():
        mosque = Mosque.query.first()
        normal_user = create_user('member@example.com', 'Password123')
        admin_user = create_user('admin@example.com', 'AdminPass123', role='admin')

    # Login as normal user and submit request
    login_response = client.post(
        '/api/auth/login',
        json={'email': 'member@example.com', 'password': 'Password123'},
    )
    assert login_response.status_code == 200

    request_payload = {
        'mosque_id': mosque.id,
        'motivation': 'I manage events at this mosque.',
        'contact_email': 'member@example.com',
        'contact_phone': '+32 9 111 11 11',
    }
    response = client.post('/api/mosques/access-requests', json=request_payload)
    assert response.status_code == 201
    request_data = response.get_json()['request']
    request_id = request_data['id']

    # Ensure request is stored as pending
    with app.app_context():
        stored_request = MosqueAccessRequest.query.get(request_id)
        assert stored_request.status == 'pending'

    # Approve as admin using separate session
    admin_client = app.test_client()
    admin_login = admin_client.post(
        '/api/auth/login', json={'email': 'admin@example.com', 'password': 'AdminPass123'}
    )
    assert admin_login.status_code == 200

    approve_response = admin_client.patch(
        f'/api/mosques/access-requests/{request_id}',
        json={'status': 'approved', 'mosque_id': mosque.id},
    )
    assert approve_response.status_code == 200

    with app.app_context():
        updated_request = MosqueAccessRequest.query.get(request_id)
        assert updated_request.status == 'approved'
        updated_user = User.query.filter_by(email='member@example.com').first()
        assert updated_user.role == 'mosque_admin'
        assert updated_user.mosque_id == mosque.id
