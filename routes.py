import os
import uuid
from flask import render_template, redirect, url_for, request, flash
from app import app
from extensions import db
from forms import RegistrationForm, LoginForm, WasteCollectionForm, WasteListingForm, ProductForm
from models import User, WasteCollection, WasteListing, Product, CartItem, Order, Payout
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = 'static/images/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    products = Product.query.limit(3).all()  # Fetch up to 3 products for the homepage
    return render_template('index.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, role=form.role.data).first()
        if user and user.password == form.password.data:  # Use proper hashing in production
            login_user(user)
            flash('Logged in successfully!', 'success')
            if user.role == 'staff':
                return redirect(url_for('staff_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username, password, or role.', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'customer':
        collections = WasteCollection.query.filter_by(seller_id=current_user.id).all()
        payouts = Payout.query.filter_by(seller_id=current_user.id).all()
        return render_template('customer_dashboard.html', collections=collections, payouts=payouts)
    elif current_user.role == 'waste_buyer':
        return render_template('waste_buyer_dashboard.html')
    elif current_user.role == 'staff':
        return redirect(url_for('staff_dashboard'))
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))

@app.route('/staff_dashboard')
@login_required
def staff_dashboard():
    if current_user.role != 'staff':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    collections = WasteCollection.query.all()
    listings = WasteListing.query.all()
    products = Product.query.all()
    return render_template('staff_dashboard.html', collections=collections, listings=listings, products=products)

@app.route('/request_collection', methods=['GET', 'POST'])
@login_required
def request_collection():
    if current_user.role != 'customer':
        flash('Only customers can request waste collection.', 'error')
        return redirect(url_for('dashboard'))
    form = WasteCollectionForm()
    if form.validate_on_submit():
        collection = WasteCollection(
            seller_id=current_user.id,
            waste_details=form.waste_details.data,
            weight=form.weight.data,
            waste_type=form.waste_type.data
        )
        if form.image.data:
            image = form.image.data
            filename = f"{uuid.uuid4()}_{secure_filename(image.filename)}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                image.save(image_path)
                collection.image_path = f'images/uploads/{filename}'
            except Exception as e:
                flash(f'Error saving image: {str(e)}', 'error')
                return redirect(url_for('request_collection'))
        db.session.add(collection)
        db.session.commit()
        flash('Collection request submitted successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('request_collection.html', form=form)

@app.route('/collect_waste/<int:collection_id>', methods=['POST'])
@login_required
def collect_waste(collection_id):
    if current_user.role != 'staff':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    collection = WasteCollection.query.get_or_404(collection_id)
    collection.status = 'collected'
    collection.collection_date = datetime.utcnow()
    db.session.commit()
    flash('Waste marked as collected.', 'success')
    return redirect(url_for('staff_dashboard'))

@app.route('/approve_waste/<int:collection_id>', methods=['POST'])
@login_required
def approve_waste(collection_id):
    if current_user.role != 'staff':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    collection = WasteCollection.query.get_or_404(collection_id)
    collection.status = 'approved'
    payout_amount = collection.weight * 0.5  # ₹0.5 per kg
    payout = Payout(seller_id=collection.seller_id, amount=payout_amount, status='Completed')
    db.session.add(payout)
    db.session.commit()
    flash('Waste approved and payout initiated.', 'success')
    return redirect(url_for('staff_dashboard'))

@app.route('/list_waste', methods=['GET', 'POST'])
@login_required
def list_waste():
    if current_user.role != 'staff':
        flash('Only staff can list waste.', 'error')
        return redirect(url_for('index'))
    form = WasteListingForm()
    if form.validate_on_submit():
        waste = WasteListing(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            quantity=form.quantity.data,
            price=form.price.data,
            staff_id=current_user.id
        )
        if form.image.data:
            image = form.image.data
            filename = f"{uuid.uuid4()}_{secure_filename(image.filename)}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                image.save(image_path)
                waste.image_path = f'images/uploads/{filename}'
            except Exception as e:
                flash(f'Error saving image: {str(e)}', 'error')
                return redirect(url_for('list_waste'))
        else:
            waste.image_path = None
        db.session.add(waste)
        db.session.commit()
        flash('Waste listed successfully!', 'success')
        return redirect(url_for('staff_dashboard'))
    return render_template('list_waste_staff.html', form=form)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role != 'staff':
        flash('Only staff can add products.', 'error')
        return redirect(url_for('index'))
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            staff_id=current_user.id
        )
        if form.image.data:
            image = form.image.data
            filename = f"{uuid.uuid4()}_{secure_filename(image.filename)}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                image.save(image_path)
                product.image_path = f'images/uploads/{filename}'
            except Exception as e:
                flash(f'Error saving image: {str(e)}', 'error')
                return redirect(url_for('add_product'))
        else:
            product.image_path = None
        db.session.add(product)
        db.session.commit()
        flash('Product added to eco-marketplace.', 'success')
        return redirect(url_for('staff_dashboard'))
    return render_template('add_product_staff.html', form=form)

@app.route('/browse_waste')
@login_required
def browse_waste():
    if current_user.role != 'waste_buyer':
        flash('Only waste buyers can browse waste listings.', 'error')
        return redirect(url_for('dashboard'))
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    listings = WasteListing.query
    if search:
        listings = listings.filter(WasteListing.title.ilike(f'%{search}%'))
    if category:
        listings = listings.filter(WasteListing.category == category)
    listings = listings.all()
    categories = ['plastic', 'metal', 'fabric', 'wood']
    return render_template('browse_waste.html', listings=listings, categories=categories)

@app.route('/eco_marketplace')
@login_required
def eco_marketplace():
    if current_user.role != 'customer':
        flash('Only customers can access the eco-marketplace.', 'error')
        return redirect(url_for('dashboard'))
    search = request.args.get('search', '')
    products = Product.query
    if search:
        products = products.filter(Product.name.ilike(f'%{search}%'))
    products = products.all()
    return render_template('eco_marketplace.html', products=products)

@app.route('/add_to_cart/<string:item_type>/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_type, item_id):
    if item_type == 'waste' and current_user.role != 'waste_buyer':
        flash('Only waste buyers can add waste to cart.', 'error')
        return redirect(url_for('dashboard'))
    if item_type == 'product' and current_user.role != 'customer':
        flash('Only customers can add products to cart.', 'error')
        return redirect(url_for('dashboard'))
    if item_type == 'waste':
        item = WasteListing.query.get_or_404(item_id)
        if item.quantity < 1:
            flash('This item is out of stock.', 'error')
            return redirect(url_for('browse_waste'))
        cart_item = CartItem.query.filter_by(user_id=current_user.id, waste_listing_id=item_id).first()
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(user_id=current_user.id, waste_listing_id=item_id, quantity=1)
    elif item_type == 'product':
        item = Product.query.get_or_404(item_id)
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=item_id).first()
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(user_id=current_user.id, product_id=item_id, quantity=1)
    else:
        flash('Invalid item type.', 'error')
        return redirect(url_for('dashboard'))
    db.session.add(cart_item)
    db.session.commit()
    flash('Item added to cart!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/cart')
@login_required
def view_cart():
    if current_user.role not in ['customer', 'waste_buyer']:
        flash('Only customers and waste buyers can view the cart.', 'error')
        return redirect(url_for('dashboard'))
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = 0
    for item in cart_items:
        if item.waste_listing:
            total += item.waste_listing.price * item.quantity
        elif item.product:
            total += item.product.price * item.quantity
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if current_user.role not in ['customer', 'waste_buyer']:
        flash('Only customers and waste buyers can checkout.', 'error')
        return redirect(url_for('dashboard'))
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('view_cart'))
    total = 0
    for item in cart_items:
        if item.waste_listing:
            total += item.waste_listing.price * item.quantity
        elif item.product:
            total += item.product.price * item.quantity
    if request.method == 'POST':
        payment_status = request.form.get('payment_status', 'success')
        if payment_status == 'success':
            order = Order(user_id=current_user.id, total=total, status='Paid')
            db.session.add(order)
            for item in cart_items:
                if item.waste_listing:
                    item.waste_listing.quantity -= item.quantity
                db.session.delete(item)
            db.session.commit()
            flash('Payment successful! Order placed.', 'success')
            return redirect(url_for('order_confirmation', order_id=order.id))
        else:
            flash('Payment failed. Please try again.', 'error')
            return redirect(url_for('view_cart'))
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/order_confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard'))
    return render_template('order_confirmation.html', order=order)