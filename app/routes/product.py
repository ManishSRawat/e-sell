from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Product, Category, User, Review
from werkzeug.utils import secure_filename
import os
from datetime import datetime

product_bp = Blueprint('product', __name__)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@product_bp.route('/', methods=['GET'])
def get_products():
    """Get all products with optional filtering and pagination."""
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    category = request.args.get('category')
    search = request.args.get('search')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Build query
    query = {}
    if category:
        query['category'] = category
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    if min_price is not None:
        query['price'] = {'$gte': min_price}
    if max_price is not None:
        query['price'] = query.get('price', {})
        query['price']['$lte'] = max_price
    
    # Determine sort order
    sort_direction = -1 if sort_order == 'desc' else 1
    sort_field = sort_by if sort_by in ['name', 'price', 'created_at'] else 'created_at'
    
    # Get products with pagination
    products = Product.objects(**query).order_by(f"{sort_direction * sort_field}").skip((page - 1) * per_page).limit(per_page)
    total = Product.objects(**query).count()
    
    return jsonify({
        'products': [product.to_dict() for product in products],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }), 200

@product_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID."""
    product = Product.objects(id=product_id).first()
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify(product.to_dict()), 200

@product_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    """Create a new product (seller or admin only)."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    if not user or user.role not in ['seller', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.form.to_dict() if request.form else request.get_json()
    files = request.files.getlist('images') if hasattr(request, 'files') else []

    # Validate required fields
    required_fields = ['name', 'description', 'price', 'category', 'stock']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate category
    category = Category.objects(id=data['category']).first()
    if not category:
        return jsonify({'error': 'Invalid category'}), 400

    # Handle image uploads
    image_urls = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.utcnow().timestamp()}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            image_urls.append(f"/static/uploads/{unique_filename}")

    # Create product
    product = Product(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        category=category,
        stock=int(data['stock']),
        images=image_urls,
        seller=user
    )
    product.save()

    return jsonify({
        'message': 'Product created successfully',
        'product': product.to_dict()
    }), 201

@product_bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update a product (admin only)."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user or not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    product = Product.objects(id=product_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.form.to_dict()
    files = request.files.getlist('images')
    
    # Update fields if provided
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = float(data['price'])
    if 'stock' in data:
        product.stock = int(data['stock'])
    if 'category' in data:
        category = Category.objects(id=data['category']).first()
        if not category:
            return jsonify({'error': 'Invalid category'}), 400
        product.category = category
    
    # Handle image uploads
    if files:
        # Delete old images if requested
        if data.get('delete_old_images') == 'true':
            for image_url in product.images:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image_url.split('/')[-1]))
                except:
                    pass
            product.images = []
        
        # Add new images
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.utcnow().timestamp()}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                product.images.append(f"/static/uploads/{unique_filename}")
    
    product.updated_at = datetime.utcnow()
    product.save()
    
    return jsonify({
        'message': 'Product updated successfully',
        'product': product.to_dict()
    }), 200

@product_bp.route('/<product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete a product (admin only)."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user or not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    product = Product.objects(id=product_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Delete product images
    for image_url in product.images:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image_url.split('/')[-1]))
        except:
            pass
    
    product.delete()
    
    return jsonify({'message': 'Product deleted successfully'}), 200

@product_bp.route('/<product_id>/review', methods=['POST'])
@jwt_required()
def add_review(product_id):
    """Add a review to a product."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    product = Product.objects(id=product_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.get_json()
    
    if not data or 'rating' not in data:
        return jsonify({'error': 'Rating is required'}), 400
    
    rating = int(data['rating'])
    if not 1 <= rating <= 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Check if user has already reviewed this product
    existing_review = next(
        (review for review in product.reviews if str(review.user.id) == current_user_id),
        None
    )
    
    if existing_review:
        # Update existing review
        existing_review.rating = rating
        existing_review.comment = data.get('comment', '')
        existing_review.created_at = datetime.utcnow()
    else:
        # Add new review
        review = Review(
            user=user,
            rating=rating,
            comment=data.get('comment', '')
        )
        product.reviews.append(review)
    
    product.save()
    
    return jsonify({
        'message': 'Review added successfully',
        'product': product.to_dict()
    }), 200

@product_bp.route('/<product_id>/review', methods=['DELETE'])
@jwt_required()
def delete_review(product_id):
    """Delete a user's review from a product."""
    current_user_id = get_jwt_identity()
    
    product = Product.objects(id=product_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Find and remove the user's review
    product.reviews = [review for review in product.reviews if str(review.user.id) != current_user_id]
    product.save()
    
    return jsonify({
        'message': 'Review deleted successfully',
        'product': product.to_dict()
    }), 200 