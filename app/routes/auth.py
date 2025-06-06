from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from app.models import User
from app import mail
from flask_mail import Message
from datetime import datetime, timedelta
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.objects(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    user = User(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name']
    )
    user.set_password(data['password'])
    
    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    user.verification_token = verification_token
    user.save()
    
    # Send verification email
    try:
        msg = Message(
            'Welcome to Our E-Commerce Store!',
            recipients=[user.email]
        )
        msg.body = f'''Welcome {user.first_name}!

Thank you for registering with our store. Please verify your email by clicking the following link:
{request.host_url}verify-email/{verification_token}

If you did not register for an account, please ignore this email.
'''
        mail.send(msg)
    except Exception as e:
        # Log the error but don't fail the registration
        print(f"Failed to send verification email: {str(e)}")
    
    return jsonify({
        'message': 'Registration successful. Please check your email for verification.',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens."""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.objects(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is not active'}), 401
    
    # Create access and refresh tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    
    # Update password if provided
    if 'password' in data:
        user.set_password(data['password'])
    
    user.updated_at = datetime.utcnow()
    user.save()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify user email."""
    user = User.objects(verification_token=token).first()
    
    if not user:
        return jsonify({'error': 'Invalid verification token'}), 400
    
    user.is_active = True
    user.verification_token = None
    user.save()
    
    return jsonify({'message': 'Email verified successfully'}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email."""
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    user = User.objects(email=data['email']).first()
    
    if not user:
        # Don't reveal that the email doesn't exist
        return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    user.save()
    
    # Send reset email
    try:
        msg = Message(
            'Password Reset Request',
            recipients=[user.email]
        )
        msg.body = f'''Hello {user.first_name},

You have requested to reset your password. Click the following link to reset your password:
{request.host_url}reset-password/{reset_token}

This link will expire in 1 hour.

If you did not request a password reset, please ignore this email.
'''
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send password reset email: {str(e)}")
        return jsonify({'error': 'Failed to send reset email'}), 500
    
    return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Reset user password."""
    data = request.get_json()
    
    if not data or not data.get('password'):
        return jsonify({'error': 'New password is required'}), 400
    
    user = User.objects(
        reset_token=token,
        reset_token_expires__gt=datetime.utcnow()
    ).first()
    
    if not user:
        return jsonify({'error': 'Invalid or expired reset token'}), 400
    
    # Update password
    user.set_password(data['password'])
    user.reset_token = None
    user.reset_token_expires = None
    user.save()
    
    return jsonify({'message': 'Password reset successful'}), 200 