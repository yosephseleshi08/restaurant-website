from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

# Initialize the modular SQLAlchemy object
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='customer', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Establish data cohesion mapping
    reservations = db.relationship('Reservation', backref='customer', lazy=True, cascade="all, delete-orphan")


class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    party_size = db.Column(db.Integer, nullable=False)
    booking_time = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(20), default='confirmed', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_email = db.Column(db.String(120), nullable=False)
    message_body = db.Column(db.Text, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)