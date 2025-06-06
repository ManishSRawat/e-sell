from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Order, OrderItem, Cart, Product, User
from app import mail
from flask_mail import Message
from datetime import datetime

order_bp = Blueprint('order', __name__)

@order_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """Get all orders for the current user."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get query parameters for filtering
    status = request.args.get('status')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Build query
    query = {'user': user}
    if status:
        query['status'] = status
    
    # Get orders with pagination
    orders = Order.objects(**query).order_by('-created_at').skip((page - 1) * per_page).limit(per_page)
    total = Order.objects(**query).count()
    
    return jsonify({
        'orders': [order.to_dict() for order in orders],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }), 200

@order_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get a specific order by ID."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    order = Order.objects(id=order_id, user=user).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify(order.to_dict()), 200

@order_bp.route('/create', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new order from the cart."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if not data or 'shipping_address' not in data:
        return jsonify({'error': 'Shipping address is required'}), 400
    
    # Get user's cart
    cart = Cart.objects(user=user).first()
    if not cart or not cart.items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Validate stock and calculate total
    order_items = []
    total_amount = 0
    
    for cart_item in cart.items:
        product = cart_item.product
        
        # Check stock
        if cart_item.quantity > product.stock:
            return jsonify({
                'error': f'Insufficient stock for {product.name}',
                'product_id': str(product.id)
            }), 400
        
        # Create order item
        order_item = OrderItem(
            product=product,
            quantity=cart_item.quantity,
            price_at_time=product.price
        )
        order_items.append(order_item)
        
        # Update total
        total_amount += product.price * cart_item.quantity
        
        # Update product stock
        product.stock -= cart_item.quantity
        product.save()
    
    # Create order
    order = Order(
        user=user,
        items=order_items,
        total_amount=total_amount,
        status='pending',
        shipping_address=data['shipping_address'],
        payment_status='pending'
    )
    order.save()
    
    # Clear cart
    cart.items = []
    cart.updated_at = datetime.utcnow()
    cart.save()
    
    # Send order confirmation email
    try:
        msg = Message(
            'Order Confirmation',
            recipients=[user.email]
        )
        msg.body = f'''Hello {user.first_name},

Thank you for your order! Your order details are as follows:

Order ID: {order.id}
Total Amount: ${order.total_amount:.2f}
Status: {order.status}

Shipping Address:
{order.shipping_address.get('street')}
{order.shipping_address.get('city')}, {order.shipping_address.get('state')} {order.shipping_address.get('zip')}
{order.shipping_address.get('country')}

We will notify you when your order ships.

Thank you for shopping with us!
'''
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send order confirmation email: {str(e)}")
    
    return jsonify({
        'message': 'Order created successfully',
        'order': order.to_dict()
    }), 201

@order_bp.route('/<order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    order = Order.objects(id=order_id, user=user).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Check if order can be cancelled
    if order.status not in ['pending', 'processing']:
        return jsonify({'error': 'Order cannot be cancelled in its current status'}), 400
    
    # Update order status
    order.status = 'cancelled'
    order.updated_at = datetime.utcnow()
    
    # Restore product stock
    for item in order.items:
        product = item.product
        product.stock += item.quantity
        product.save()
    
    order.save()
    
    # Send cancellation email
    try:
        msg = Message(
            'Order Cancelled',
            recipients=[user.email]
        )
        msg.body = f'''Hello {user.first_name},

Your order #{order.id} has been cancelled.

If you did not request this cancellation, please contact our customer service immediately.

Thank you for your understanding.
'''
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send cancellation email: {str(e)}")
    
    return jsonify({
        'message': 'Order cancelled successfully',
        'order': order.to_dict()
    }), 200

@order_bp.route('/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """Update order status (admin only)."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user or not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    order = Order.objects(id=order_id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    new_status = data['status']
    if new_status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        return jsonify({'error': 'Invalid status'}), 400
    
    # Update order status
    order.status = new_status
    order.updated_at = datetime.utcnow()
    order.save()
    
    # Send status update email
    try:
        msg = Message(
            'Order Status Update',
            recipients=[order.user.email]
        )
        msg.body = f'''Hello {order.user.first_name},

Your order #{order.id} status has been updated to: {new_status}

You can track your order status by logging into your account.

Thank you for shopping with us!
'''
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send status update email: {str(e)}")
    
    return jsonify({
        'message': 'Order status updated successfully',
        'order': order.to_dict()
    }), 200

@order_bp.route('/<order_id>/payment', methods=['POST'])
@jwt_required()
def update_payment_status(order_id):
    """Update order payment status."""
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    order = Order.objects(id=order_id, user=user).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()
    
    if not data or 'payment_status' not in data or 'payment_id' not in data:
        return jsonify({'error': 'Payment status and payment ID are required'}), 400
    
    new_payment_status = data['payment_status']
    if new_payment_status not in ['pending', 'completed', 'failed', 'refunded']:
        return jsonify({'error': 'Invalid payment status'}), 400
    
    # Update payment status
    order.payment_status = new_payment_status
    order.payment_id = data['payment_id']
    order.updated_at = datetime.utcnow()
    
    # If payment is completed, update order status to processing
    if new_payment_status == 'completed' and order.status == 'pending':
        order.status = 'processing'
    
    order.save()
    
    return jsonify({
        'message': 'Payment status updated successfully',
        'order': order.to_dict()
    }), 200 