from app import app, db
from models import User, WasteCollection, WasteListing, Product, Payout

with app.app_context():
    # Drop all tables
    db.drop_all()
    # Create all tables
    db.create_all()

    # Add test users
    staff = User(username='staff1', password='staffpass', role='staff')
    customer = User(username='customer1', password='customerpass', role='customer')
    waste_buyer = User(username='wastebuyer1', password='wastebuyerpass', role='waste_buyer')
    db.session.add_all([staff, customer, waste_buyer])
    db.session.commit()

    # Add test waste collection
    collection = WasteCollection(
        seller_id=customer.id,
        waste_details='Plastic bottles',
        weight=10.0,
        waste_type='plastic',
        status='pending',
        image_path=None  # Replace with 'images/uploads/sample.jpg' if you have a sample image
    )
    db.session.add(collection)

    # Add test waste listing
    listing = WasteListing(
        title='Plastic Scrap',
        description='Clean plastic waste',
        category='plastic',
        quantity=100,
        price=500.0,
        staff_id=staff.id,
        image_path=None
    )
    db.session.add(listing)

    # Add test product
    product = Product(
        name='Eco Bag',
        description='Recycled fabric bag',
        price=1000.0,
        staff_id=staff.id,
        image_path=None
    )
    db.session.add(product)

    # Add test payout
    payout = Payout(
        seller_id=customer.id,
        amount=5.0,
        status='Completed'
    )
    db.session.add(payout)

    db.session.commit()
    print("Database initialized with test data.")