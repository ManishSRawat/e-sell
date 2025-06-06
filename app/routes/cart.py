from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Cart, CartItem, Product, User
from datetime import datetime

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    """Get the current user's cart."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    cart = Cart.objects(user=user).first()
    
    if not cart:
        cart = Cart(user=user, items=[])
        cart.save()
    
    return jsonify(cart.to_dict()), 200

@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add a product to the cart."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify({'error': 'Product ID and quantity are required'}), 400
    
    product = Product.objects(id=data['product_id']).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    quantity = int(data['quantity'])
    if quantity <= 0:
        return jsonify({'error': 'Quantity must be greater than 0'}), 400
    
    if quantity > product.stock:
        return jsonify({'error': 'Requested quantity exceeds available stock'}), 400
    
    # Get or create cart
    cart = Cart.objects(user=user).first()
    if not cart:
        cart = Cart(user=user, items=[])
    
    # Check if product is already in cart
    existing_item = next(
        (item for item in cart.items if str(item.product.id) == data['product_id']),
        None
    )
    
    if existing_item:
        # Update quantity if product exists in cart
        new_quantity = existing_item.quantity + quantity
        if new_quantity > product.stock:
            return jsonify({'error': 'Total quantity exceeds available stock'}), 400
        existing_item.quantity = new_quantity
        existing_item.added_at = datetime.utcnow()
    else:
        # Add new item to cart
        cart_item = CartItem(
            product=product,
            quantity=quantity
        )
        cart.items.append(cart_item)
    
    cart.updated_at = datetime.utcnow()
    cart.save()
    
    return jsonify({
        'message': 'Product added to cart successfully',
        'cart': cart.to_dict()
    }), 200

@cart_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_cart_item():
    """Update cart item quantity."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify({'error': 'Product ID and quantity are required'}), 400
    
    cart = Cart.objects(user=user).first()
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    product = Product.objects(id=data['product_id']).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    quantity = int(data['quantity'])
    if quantity <= 0:
        return jsonify({'error': 'Quantity must be greater than 0'}), 400
    
    if quantity > product.stock:
        return jsonify({'error': 'Requested quantity exceeds available stock'}), 400
    
    # Find and update cart item
    cart_item = next(
        (item for item in cart.items if str(item.product.id) == data['product_id']),
        None
    )
    
    if not cart_item:
        return jsonify({'error': 'Product not found in cart'}), 404
    
    cart_item.quantity = quantity
    cart_item.added_at = datetime.utcnow()
    cart.updated_at = datetime.utcnow()
    cart.save()
    
    return jsonify({
        'message': 'Cart updated successfully',
        'cart': cart.to_dict()
    }), 200

@cart_bp.route('/remove/<product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(product_id):
    """Remove a product from the cart."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    cart = Cart.objects(user=user).first()
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    # Remove item from cart
    cart.items = [item for item in cart.items if str(item.product.id) != product_id]
    cart.updated_at = datetime.utcnow()
    cart.save()
    
    return jsonify({
        'message': 'Product removed from cart successfully',
        'cart': cart.to_dict()
    }), 200

@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """Clear all items from the cart."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    cart = Cart.objects(user=user).first()
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    cart.items = []
    cart.updated_at = datetime.utcnow()
    cart.save()
    
    return jsonify({
        'message': 'Cart cleared successfully',
        'cart': cart.to_dict()
    }), 200 