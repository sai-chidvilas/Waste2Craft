from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///waste2craft.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
print("SQLAlchemy initialized")

class TestModel(db.Model):
    __tablename__ = 'test_model'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class EcoProduct(db.Model):
    __tablename__ = 'eco_product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(100))

with app.app_context():
    print("Creating tables")
    db.drop_all()
    print("Dropped all tables")
    db.create_all()
    print("Called db.create_all()")

    # Verify tables
    conn = sqlite3.connect('waste2craft.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    print(f"Tables in database: {table_names}")
    conn.close()

    if 'eco_product' in table_names:
        print("Table 'eco_product' created successfully")
    else:
        print("Error: Table 'eco_product' was not created")