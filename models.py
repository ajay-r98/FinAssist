from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize the database instance
db = SQLAlchemy()

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=True)  # Allow NULL values
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, nullable=False)


    user = db.relationship('User', backref=db.backref('transactions', lazy=True))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
