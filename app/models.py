from datetime import datetime
from mongoengine import (
    Document, StringField, EmailField, FloatField, 
    IntField, ListField, ReferenceField, DateTimeField,
    BooleanField, EmbeddedDocument, EmbeddedDocumentField,
    DictField
)
from werkzeug.security import generate_password_hash, check_password_hash

class User(Document):
    """User model for authentication and user management."""
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    first_name = StringField(required=True, max_length=50)
    last_name = StringField(required=True, max_length=50)
    is_admin = BooleanField(default=False)
    is_active = BooleanField(default=True)
    verification_token = StringField()
    reset_token = StringField()
    reset_token_expires = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    role = StringField(default='buyer', choices=['buyer', 'seller', 'admin'])
    
    meta = {'collection': 'users'}

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': str(self.id),
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Category(Document):
    """Product category model."""
    name = StringField(required=True, unique=True)
    description = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'categories'}

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

class Review(EmbeddedDocument):
    """Product review embedded document."""
    user = ReferenceField(User, required=True)
    rating = IntField(required=True, min_value=1, max_value=5)
    comment = StringField()
    created_at = DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        return {
            'user': str(self.user.id),
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }

class Product(Document):
    """Product model for the e-commerce store."""
    name = StringField(required=True)
    description = StringField(required=True)
    price = FloatField(required=True, min_value=0)
    category = ReferenceField(Category, required=True)
    stock = IntField(required=True, min_value=0)
    images = ListField(StringField())  # URLs to product images
    reviews = ListField(EmbeddedDocumentField(Review))
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    seller = ReferenceField(User, required=True)
    
    meta = {
        'collection': 'products',
        'indexes': [
            'name',
            'category',
            ('name', 'category')  # Compound index
        ]
    }

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': str(self.category.id),
            'stock': self.stock,
            'images': self.images,
            'reviews': [review.to_dict() for review in self.reviews],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class CartItem(EmbeddedDocument):
    """Cart item embedded document."""
    product = ReferenceField(Product, required=True)
    quantity = IntField(required=True, min_value=1)
    added_at = DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        return {
            'product': str(self.product.id),
            'quantity': self.quantity,
            'added_at': self.added_at.isoformat()
        }

class Cart(Document):
    """Shopping cart model."""
    user = ReferenceField(User, required=True, unique=True)
    items = ListField(EmbeddedDocumentField(CartItem))
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'carts'}

    def to_dict(self):
        return {
            'id': str(self.id),
            'user': str(self.user.id),
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class OrderItem(EmbeddedDocument):
    """Order item embedded document."""
    product = ReferenceField(Product, required=True)
    quantity = IntField(required=True, min_value=1)
    price_at_time = FloatField(required=True)  # Price when order was placed

    def to_dict(self):
        return {
            'product': str(self.product.id),
            'quantity': self.quantity,
            'price_at_time': self.price_at_time
        }

class Order(Document):
    """Order model for tracking purchases."""
    user = ReferenceField(User, required=True)
    items = ListField(EmbeddedDocumentField(OrderItem))
    total_amount = FloatField(required=True)
    status = StringField(required=True, choices=[
        'pending', 'processing', 'shipped', 'delivered', 'cancelled'
    ])
    shipping_address = DictField(required=True)
    payment_status = StringField(required=True, choices=[
        'pending', 'completed', 'failed', 'refunded'
    ])
    payment_id = StringField()  # For payment gateway reference
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'orders',
        'indexes': [
            'user',
            'status',
            'payment_status',
            'created_at'
        ]
    }

    def to_dict(self):
        return {
            'id': str(self.id),
            'user': str(self.user.id),
            'items': [item.to_dict() for item in self.items],
            'total_amount': self.total_amount,
            'status': self.status,
            'shipping_address': self.shipping_address,
            'payment_status': self.payment_status,
            'payment_id': self.payment_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 