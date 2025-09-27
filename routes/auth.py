from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import jwt
import os

auth_bp = Blueprint('auth', __name__)

# JWT Secret Key
JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')

def generate_token(user_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Import here to avoid circular imports
        from models import User, db
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400
        
        desired_role = data.get('role', 'user')
        if desired_role == 'admin':
            stored_role = 'admin'
        else:
            stored_role = 'user'

        # Create new user
        user = User(
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            role=stored_role,
            mosque_id=data.get('mosque_id') if stored_role != 'user' else None,
            is_active=True,
            email_verified=False
        )
        
        db.session.add(user)
        db.session.flush()

        if desired_role == 'mosque_admin':
            from models import MosqueAccessRequest
            access_request = MosqueAccessRequest(
                user_id=user.id,
                mosque_id=data.get('mosque_id'),
                mosque_name=data.get('mosque_name'),
                motivation=data.get('admin_motivation'),
                contact_email=data.get('email'),
                contact_phone=data.get('phone')
            )
            db.session.add(access_request)

        db.session.commit()

        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            },
            'token': token
        }), 201
        
    except Exception as e:
from models import db
from services.email_service import send_password_reset_email
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/auth/request-password-reset', methods=['POST'])
def request_password_reset():
    """Initiate a password reset request"""
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        from models import User, PasswordResetToken, db

        user = User.query.filter_by(email=email).first()

        token_value = None
        if user:
            # Invalidate existing unused tokens
            PasswordResetToken.query.filter(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None)
            ).delete()

            token_value = secrets.token_urlsafe(32)
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token_value,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            db.session.add(reset_token)
            db.session.commit()

            current_app.logger.info("Password reset requested for %s", email)

            locale = (data.get('locale') or 'nl').split('-')[0]
            frontend_base = current_app.config.get('FRONTEND_BASE_URL', 'http://localhost:3000').rstrip('/')
            reset_path = f"/{locale}/forgot-password?token={token_value}"
            reset_url = frontend_base + reset_path

            if not send_password_reset_email(user.email, reset_url, locale):
                current_app.logger.warning('Password reset email could not be sent to %s', user.email)

        response = {
            'message': 'If an account exists for this email, you will receive password reset instructions.'
        }

        # Expose token in non-production environments to simplify testing
        if token_value and current_app.config.get('ENV') != 'production':
            response['reset_token'] = token_value

        return jsonify(response)

    except Exception as e:
        current_app.logger.exception('Password reset request failed: %s', e)
        return jsonify({'error': 'Unable to process password reset request'}), 500


@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Complete a password reset using a valid reset token"""
    try:
        data = request.get_json() or {}
        token = data.get('token')
        new_password = data.get('new_password')

        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400

        from models import PasswordResetToken, User, db

        reset_token = PasswordResetToken.query.filter_by(token=token).first()

        if not reset_token:
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        if reset_token.is_used or reset_token.is_expired:
            return jsonify({'error': 'Reset token is no longer valid'}), 400

        user = User.query.get(reset_token.user_id)
        if not user or not user.is_active:
            return jsonify({'error': 'Associated user account is inactive'}), 400

        user.password_hash = generate_password_hash(new_password)
        reset_token.used_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': 'Password has been reset successfully'})

    except Exception as e:
        from models import db
        db.session.rollback()
        current_app.logger.exception('Password reset failed: %s', e)
        return jsonify({'error': 'Unable to reset password'}), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Import here to avoid circular imports
        from models import User
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Login user
        login_user(user, remember=data.get('remember', False))
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'mosque_id': user.mosque_id
            },
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    try:
        logout_user()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    try:
        return jsonify({
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
                'phone': current_user.phone,
                'role': current_user.role,
                'mosque_id': current_user.mosque_id,
                'is_active': current_user.is_active,
                'email_verified': current_user.email_verified,
                'created_at': current_user.created_at.isoformat() if current_user.created_at else None
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/verify-token', methods=['POST'])
def verify_token_endpoint():
    """Verify JWT token"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        from models import User
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        return jsonify({
            'valid': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'mosque_id': user.mosque_id
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not check_password_hash(current_user.password_hash, data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        from models import db
        current_user.password_hash = generate_password_hash(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        from models import db
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/update-profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        
        from models import db
        
        # Update allowed fields
        if 'first_name' in data:
            current_user.first_name = data['first_name']
        if 'last_name' in data:
            current_user.last_name = data['last_name']
        if 'phone' in data:
            current_user.phone = data['phone']
        if 'mosque_id' in data:
            current_user.mosque_id = data['mosque_id']
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
                'phone': current_user.phone,
                'role': current_user.role,
                'mosque_id': current_user.mosque_id
            }
        }), 200
        
    except Exception as e:
        from models import db
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/mosques/access-requests', methods=['POST'])
@login_required
def create_mosque_access_request():
    """Submit a request for mosque administrator access"""
    try:
        if current_user.role in ('admin', 'mosque_admin'):
            return jsonify({'error': 'Account already has elevated permissions'}), 400

        data = request.get_json() or {}
        from models import MosqueAccessRequest, db

        existing_request = MosqueAccessRequest.query.filter_by(
            user_id=current_user.id, status='pending'
        ).first()
        if existing_request:
            return jsonify({'error': 'You already have a pending request'}), 400

        mosque_id = data.get('mosque_id')
        if mosque_id:
            try:
                mosque_id = int(mosque_id)
            except (TypeError, ValueError):
                return jsonify({'error': 'Invalid mosque id'}), 400
        else:
            mosque_id = None

        access_request = MosqueAccessRequest(
            user_id=current_user.id,
            mosque_id=mosque_id,
            mosque_name=data.get('mosque_name'),
            motivation=data.get('motivation'),
            contact_email=data.get('contact_email') or current_user.email,
            contact_phone=data.get('contact_phone') or current_user.phone
        )

        db.session.add(access_request)
        db.session.commit()

        return jsonify({
            'message': 'Access request submitted successfully',
            'request': access_request.as_dict()
        }), 201

    except Exception as e:
        from models import db
        db.session.rollback()
        current_app.logger.exception('Failed to create access request: %s', e)
        return jsonify({'error': 'Unable to submit access request'}), 500


@auth_bp.route('/api/mosques/access-requests/me', methods=['GET'])
@login_required
def list_my_access_requests():
    """List access requests submitted by the current user"""
    from models import MosqueAccessRequest

    requests = MosqueAccessRequest.query.filter_by(user_id=current_user.id).order_by(
        MosqueAccessRequest.created_at.desc()
    ).all()

    return jsonify([req.as_dict() for req in requests])


@auth_bp.route('/api/mosques/access-requests', methods=['GET'])
@login_required
def list_all_access_requests():
    """List all access requests for administrators"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    from models import MosqueAccessRequest

    status = request.args.get('status')
    query = MosqueAccessRequest.query
    if status:
        query = query.filter_by(status=status)

    requests = query.order_by(MosqueAccessRequest.created_at.desc()).all()
    return jsonify([req.as_dict() for req in requests])


@auth_bp.route('/api/mosques/access-requests/<int:request_id>', methods=['PATCH'])
@login_required
def update_access_request(request_id: int):
    """Approve or reject an access request"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    from models import MosqueAccessRequest, User, db

    data = request.get_json() or {}
    status = data.get('status')

    if status not in {'approved', 'rejected'}:
        return jsonify({'error': 'Invalid status'}), 400

    access_request = MosqueAccessRequest.query.get_or_404(request_id)

    if access_request.status != 'pending':
        return jsonify({'error': 'Request has already been processed'}), 400

    mosque_id = data.get('mosque_id') or access_request.mosque_id
    if mosque_id:
        try:
            mosque_id = int(mosque_id)
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid mosque id'}), 400

    access_request.status = status
    access_request.admin_notes = data.get('admin_notes')
    access_request.mosque_id = mosque_id
    access_request.processed_at = datetime.utcnow()
    access_request.processed_by = current_user.id

    if status == 'approved':
        user = User.query.get(access_request.user_id)
        if not user:
            return jsonify({'error': 'Associated user not found'}), 400

        user.role = 'mosque_admin'
        if mosque_id:
            user.mosque_id = mosque_id

    db.session.commit()

    return jsonify({
        'message': 'Request updated successfully',
        'request': access_request.as_dict()
    })
