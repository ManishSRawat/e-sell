from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Category, User
from datetime import datetime

category_bp = Blueprint('category', __name__)

@category_bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    if not user or not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Category name is required'}), 400

    if Category.objects(name=data['name']).first():
        return jsonify({'error': 'Category already exists'}), 400

    category = Category(
        name=data['name'],
        description=data.get('description', ''),
        created_at=datetime.utcnow()
    )
    category.save()
    return jsonify({'message': 'Category created', 'category': category.to_dict()}), 201

@category_bp.route('/', methods=['GET'])
def get_categories():
    categories = Category.objects()
    return jsonify({'categories': [cat.to_dict() for cat in categories]}), 200 