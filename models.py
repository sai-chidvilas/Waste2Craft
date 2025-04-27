from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # customer, waste_buyer, staff

class WasteCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    waste_details = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    waste_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='pending')
    collection_date = db.Column(db.DateTime)
    image_path = db.Column(db.String(200))
    seller = db.relationship('User', backref='collections')

class WasteListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(200))
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    staff = db.relationship('User', backref='waste_listings')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(200))
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    staff = db.relationship('User', backref='products')

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    waste_listing_id = db.Column(db.Integer, db.ForeignKey('waste_listing.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    user = db.relationship('User', backref='cart_items')
    waste_listing = db.relationship('WasteListing')
    product = db.relationship('Product')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='orders')

class Payout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seller = db.relationship('User', backref='payouts')