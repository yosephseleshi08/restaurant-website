"""
La Bella Cucina — Restaurant CMS Pro Edition v2.0
==================================================
11/10 Production-Ready Restaurant Management Platform
Critical Fixes: XSS protection, input validation, thread-safe JSON, email bug fix
Premium Additions: Audit logging, webhooks, health checks, capacity management
"""

from flask import (
    Flask, render_template, request, jsonify, redirect, url_for, 
    session, flash, send_file, Response, abort, g
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from functools import wraps
import json
import os
import csv
import io
import secrets
import re
import sys
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.api
import threading
import uuid
import hashlib

# ─── App Factory ────────────────────────────────────────────────────

def create_app(config_name="production"):
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Security Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

    # Cloudinary
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
        api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET', '')
    )

    # SendGrid
    app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY', '')
    app.config['FROM_EMAIL'] = os.environ.get('FROM_EMAIL', 'noreply@restaurant.com')
    app.config['NOTIFICATION_EMAIL'] = os.environ.get('NOTIFICATION_EMAIL', '')

    # Twilio
    app.config['TWILIO_SID'] = os.environ.get('TWILIO_SID', '')
    app.config['TWILIO_TOKEN'] = os.environ.get('TWILIO_TOKEN', '')
    app.config['TWILIO_PHONE'] = os.environ.get('TWILIO_PHONE', '')

    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///restaurant.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
    }

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.environ.get('REDIS_URL', 'memory://'),
    strategy="fixed-window"  # ← CHANGE TO THIS
)

    db = SQLAlchemy(app)

    # Thread-safe data file operations
    DATA_FILE = 'restaurant_data.json'
    _data_lock = threading.Lock()

    DEFAULT_DATA = {
        'theme': {
            'primary_color': '#E85D3A',
            'secondary_color': '#F4A261',
            'background_color': '#FFF8F0',
            'text_color': '#2D1B12',
            'card_bg': '#FFFFFF',
            'accent_color': '#2A9D8F',
            'font_family': "'Inter', sans-serif",
            'dark_mode': False,
            'custom_css': ''
        },
        'seo': {
            'meta_title': 'La Bella Cucina — Authentic Italian Dining Experience',
            'meta_description': 'Experience authentic Italian cuisine at La Bella Cucina. Fresh ingredients, family recipes, warm hospitality. Book your table today.',
            'meta_keywords': 'italian restaurant, pasta, pizza, fine dining, reservations',
            'og_image': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&h=630&fit=crop',
            'google_analytics_id': '',
            'facebook_pixel': ''
        },
        'restaurant': {
            'name': "La Bella Cucina",
            'tagline': "Authentic Italian Dining Experience",
            'address': "123 Main Street, Foodville, FD 12345",
            'phone': "(555) 123-4567",
            'phone_link': "+15551234567",
            'email': "info@labellacucina.com",
            'hours': {
                'monday': '11:00 AM - 10:00 PM',
                'tuesday': '11:00 AM - 10:00 PM',
                'wednesday': '11:00 AM - 10:00 PM',
                'thursday': '11:00 AM - 10:00 PM',
                'friday': '11:00 AM - 11:00 PM',
                'saturday': '10:00 AM - 11:00 PM',
                'sunday': '10:00 AM - 9:00 PM'
            },
            'social': {
                'instagram': 'labellacucina',
                'facebook': 'LaBellaCucina',
                'twitter': 'LaBellaCucina',
                'yelp': 'la-bella-cucina-foodville'
            },
            'google_maps_embed': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3022.1!2d-74.006!3d40.7128!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zNDDCsDQyJzQ2LjEiTiA3NMKwMDAnMjEuNiJX!5e0!3m2!1sen!2us!4v1'
        },
        'about': {
            'story': "Founded in 2010 by Chef Marco Rossi, La Bella Cucina brings the heart of Tuscany to your table.",
            'chef_name': "Chef Marco Rossi",
            'chef_bio': "With over 20 years of experience in Michelin-starred kitchens across Rome and Florence.",
            'chef_image': "https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=400&h=400&fit=crop",
            'interior_image': "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&h=600&fit=crop",
            'food_image': "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&h=600&fit=crop",
            'values': [
                {'title': 'Fresh Ingredients', 'description': 'We source locally and import directly from Italy every week.'},
                {'title': 'Family Recipes', 'description': 'Every sauce and dough is made from scratch using time-honored techniques.'},
                {'title': 'Warm Hospitality', 'description': 'We treat every guest like family from the moment you walk through our doors.'}
            ]
        },
        'testimonials': [
            {'name': 'Sarah M.', 'text': 'The best carbonara I have had outside of Rome!', 'rating': 5},
            {'name': 'James & Linda K.', 'text': 'We celebrated our anniversary here and the staff made us feel so special.', 'rating': 5},
            {'name': 'David R.', 'text': 'Authentic flavors, generous portions, and the wine selection is incredible.', 'rating': 5},
            {'name': 'Maria G.', 'text': 'As an Italian expat, I can confirm this is the real deal.', 'rating': 5}
        ],
        'menu': {
            'appetizers': [
                {'name': 'Bruschetta al Pomodoro', 'description': 'Grilled sourdough topped with fresh tomatoes, basil, garlic, and extra virgin olive oil', 'price': 12.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1572695157369-7b5e6e5a04c5?w=500&h=350&fit=crop', 'dietary': ['vegetarian']},
                {'name': 'Calamari Fritti', 'description': 'Tender calamari lightly fried and served with lemon aioli', 'price': 14.99, 'popular': False, 'image': 'https://images.unsplash.com/photo-1599084993091-41d2bd2722cc6?w=500&h=350&fit=crop', 'dietary': []},
                {'name': 'Burrata e Prosciutto', 'description': 'Creamy burrata cheese with aged prosciutto di Parma, arugula, and balsamic glaze', 'price': 16.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1529312266912-b33cf6227e24?w=500&h=350&fit=crop', 'dietary': []}
            ],
            'mains': [
                {'name': 'Spaghetti alla Carbonara', 'description': 'Classic Roman pasta with guanciale, pecorino romano, farm eggs, and cracked black pepper', 'price': 22.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1612874742237-6526221588e3?w=500&h=350&fit=crop', 'dietary': []},
                {'name': 'Chicken Parmigiana', 'description': 'Hand-breaded chicken breast with San Marzano marinara, fresh mozzarella, and parmesan', 'price': 24.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1632778149955-e80f8ceca2e8?w=500&h=350&fit=crop', 'dietary': []},
                {'name': 'Margherita Pizza', 'description': 'San Marzano tomato sauce, fresh fior di latte mozzarella, basil, and EVOO on wood-fired crust', 'price': 18.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=500&h=350&fit=crop', 'dietary': ['vegetarian']},
                {'name': 'Osso Buco alla Milanese', 'description': 'Braised veal shank in white wine and gremolata, served with saffron risotto', 'price': 34.99, 'popular': False, 'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=500&h=350&fit=crop', 'dietary': ['gluten-free']}
            ],
            'desserts': [
                {'name': 'Tiramisu Classico', 'description': 'Layers of espresso-soaked ladyfingers and mascarpone cream, dusted with Valrhona cocoa', 'price': 10.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=500&h=350&fit=crop', 'dietary': ['vegetarian']},
                {'name': 'Panna Cotta', 'description': 'Silky vanilla bean custard with seasonal berry compote and fresh mint', 'price': 9.99, 'popular': False, 'image': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=500&h=350&fit=crop', 'dietary': ['vegetarian', 'gluten-free']}
            ],
            'beverages': [
                {'name': 'Espresso Doppio', 'description': 'Double shot of rich Italian espresso, roasted in-house', 'price': 4.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500&h=350&fit=crop', 'dietary': ['vegetarian', 'gluten-free']},
                {'name': 'Aperol Spritz', 'description': 'Aperol, prosecco, and soda with a fresh orange slice and green olive', 'price': 12.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1560512823-8ea9f5b3028b?w=500&h=350&fit=crop', 'dietary': ['vegetarian', 'gluten-free']},
                {'name': 'Limonata Fresca', 'description': 'House-made lemonade with fresh Sicilian lemons, mint, and a touch of honey', 'price': 6.99, 'popular': False, 'image': 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=500&h=350&fit=crop', 'dietary': ['vegetarian', 'gluten-free']}
            ]
        },
        'reservations': {
            'hold_time': '15 minutes',
            'large_party_note': 'Parties of 8+ please call directly',
            'time_slots': ['17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00'],
            'max_guests_per_slot': 30
        },
        'online_ordering': {
            'enabled': True,
            'page_title': 'Order Online',
            'page_subtitle': 'Enjoy our authentic Italian cuisine from the comfort of your home.',
            'platforms': [
                {'name': 'DoorDash', 'url': 'https://doordash.com', 'icon': 'fa-motorcycle', 'active': True, 'color': '#FF3008'},
                {'name': 'UberEats', 'url': 'https://ubereats.com', 'icon': 'fa-utensils', 'active': True, 'color': '#06C167'},
                {'name': 'Grubhub', 'url': 'https://grubhub.com', 'icon': 'fa-hamburger', 'active': True, 'color': '#F63440'},
                {'name': 'Toast', 'url': 'https://toasttab.com', 'icon': 'fa-receipt', 'active': False, 'color': '#4A90D9'}
            ]
        },
        'gallery': {
            'enabled': True,
            'page_title': 'Gallery',
            'page_subtitle': 'A glimpse into our kitchen, our dishes, and the warm atmosphere that awaits you.',
            'photos': [
                {'url': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&h=600&fit=crop', 'caption': 'Our signature dining room', 'category': 'interior'},
                {'url': 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800&h=600&fit=crop', 'caption': 'Wood-fired Margherita Pizza', 'category': 'food'},
                {'url': 'https://images.unsplash.com/photo-1612874742237-6526221588e3?w=800&h=600&fit=crop', 'caption': 'Spaghetti alla Carbonara', 'category': 'food'},
                {'url': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&h=600&fit=crop', 'caption': 'Elegant dining atmosphere', 'category': 'interior'},
                {'url': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=800&h=600&fit=crop', 'caption': 'Tiramisu Classico', 'category': 'food'},
                {'url': 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&h=600&fit=crop', 'caption': 'Our open kitchen', 'category': 'interior'},
                {'url': 'https://images.unsplash.com/photo-1560512823-8ea9f5b3028b?w=800&h=600&fit=crop', 'caption': 'Aperol Spritz', 'category': 'drinks'},
                {'url': 'https://images.unsplash.com/photo-1550966871-3ed3c47e2ce2?w=800&h=600&fit=crop', 'caption': 'Private dining room', 'category': 'interior'}
            ]
        },
        'events': {
            'enabled': True,
            'page_title': 'Events & Private Dining',
            'page_subtitle': 'Host your next celebration with us. From intimate dinners to large gatherings, we create unforgettable experiences.',
            'hero_image': 'https://images.unsplash.com/photo-1519167758481-83f55049b3b3?w=1920&h=800&fit=crop',
            'cta_title': 'Book Your Private Event',
            'cta_text': 'Let us help you plan the perfect occasion. Contact us to discuss custom menus and special requests.',
            'services': [
                {'title': 'Private Dining Room', 'description': 'An intimate space for up to 24 guests, perfect for family celebrations and business meetings.', 'icon': 'fa-utensils'},
                {'title': 'Full Restaurant Buyout', 'description': 'Host up to 80 guests for a truly exclusive experience. Ideal for weddings and corporate events.', 'icon': 'fa-building'},
                {'title': 'Catering & Off-Site', 'description': 'Bring the flavors of La Bella Cucina to your venue. Full-service catering for events of any size.', 'icon': 'fa-truck'},
                {'title': 'Wine Pairing Dinners', 'description': 'Elevate your event with a curated wine pairing experience.', 'icon': 'fa-wine-glass'}
            ],
            'upcoming_events': [
                {'title': 'Wine & Dine Wednesday', 'description': 'Every Wednesday, enjoy a 3-course prix fixe menu paired with sommelier-selected wines. $65 per person.', 'date': 'Every Wednesday', 'image': 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600&h=400&fit=crop'},
                {'title': 'Sunday Family Feast', 'description': 'A rotating family-style menu featuring classic Italian dishes served at communal tables.', 'date': 'Every Sunday', 'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=400&fit=crop'},
                {'title': 'Pasta Making Class', 'description': 'Learn the art of fresh pasta from Chef Marco. Includes hands-on instruction and dinner.', 'date': 'First Saturday of the month', 'image': 'https://images.unsplash.com/photo-1551183053-bf91b1dca034?w=600&h=400&fit=crop'}
            ]
        },
        'analytics': {
            'daily_sales': [1250, 1420, 1380, 1680, 2100, 2450, 1800],
            'monthly_revenue': [45000, 52000, 49000, 58000, 62000, 68000],
            'popular_items': ['Spaghetti Carbonara', 'Chicken Parmigiana', 'Margherita Pizza'],
            'customer_satisfaction': 4.8,
            'total_reservations': 156
        },
        'settings': {
            'sendgrid_api_key': '',
            'from_email': '',
            'notification_email': '',
            'currency': '$',
            'tax_rate': 8.5,
            'delivery_fee': 5.0,
            'min_order': 15.0,
            'cookie_consent': True,
            'enable_online_ordering': True,
            'enable_reservations': True,
            'enable_events': True,
            'enable_gallery': True,
            'enable_loyalty': True,
            'enable_gift_cards': True,
            'enable_waitlist': True,
            'enable_table_management': True,
            'enable_kitchen_display': True,
            'webhook_secret': secrets.token_hex(16)
        }
    }

    # ─── Database Models ───────────────────────────────────────────────

    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(255), nullable=False)
        role = db.Column(db.String(20), default='admin', index=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        last_login = db.Column(db.DateTime)

    class Reservation(db.Model):
        __tablename__ = 'reservations'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), nullable=False, index=True)
        phone = db.Column(db.String(50), nullable=False)
        date = db.Column(db.String(20), nullable=False, index=True)
        time = db.Column(db.String(10), nullable=False, index=True)
        guests = db.Column(db.String(10), nullable=False)
        special_requests = db.Column(db.Text)
        status = db.Column(db.String(20), default='pending', index=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    class ContactMessage(db.Model):
        __tablename__ = 'contact_messages'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), nullable=False, index=True)
        subject = db.Column(db.String(100), nullable=False)
        message = db.Column(db.Text, nullable=False)
        status = db.Column(db.String(20), default='new', index=True)
        reply = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class Order(db.Model):
        __tablename__ = 'orders'
        id = db.Column(db.Integer, primary_key=True)
        customer_name = db.Column(db.String(100), nullable=False)
        customer_email = db.Column(db.String(120), nullable=False, index=True)
        customer_phone = db.Column(db.String(50), nullable=False)
        order_type = db.Column(db.String(20), default='pickup', index=True)
        total = db.Column(db.Float, default=0.0)
        status = db.Column(db.String(20), default='pending', index=True)
        notes = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    class OrderItem(db.Model):
        __tablename__ = 'order_items'
        id = db.Column(db.Integer, primary_key=True)
        order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
        name = db.Column(db.String(100), nullable=False)
        price = db.Column(db.Float, nullable=False)
        quantity = db.Column(db.Integer, default=1)
        category = db.Column(db.String(50))
        order = db.relationship('Order', backref=db.backref('items', lazy='dynamic'))

    class PageView(db.Model):
        __tablename__ = 'page_views'
        id = db.Column(db.Integer, primary_key=True)
        page = db.Column(db.String(100), nullable=False, index=True)
        ip_address = db.Column(db.String(45))
        user_agent = db.Column(db.String(500))
        referrer = db.Column(db.String(500))
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    class NewsletterSubscriber(db.Model):
        __tablename__ = 'newsletter_subscribers'
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True, nullable=False, index=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class EventBooking(db.Model):
        __tablename__ = 'event_bookings'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), nullable=False)
        phone = db.Column(db.String(50), nullable=False)
        event_type = db.Column(db.String(100), nullable=False)
        event_date = db.Column(db.String(20))
        guests = db.Column(db.String(10))
        message = db.Column(db.Text)
        status = db.Column(db.String(20), default='pending')
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class CateringInquiry(db.Model):
        __tablename__ = 'catering_inquiries'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), nullable=False)
        phone = db.Column(db.String(50), nullable=False)
        event_date = db.Column(db.String(20))
        guests = db.Column(db.String(10))
        message = db.Column(db.Text)
        status = db.Column(db.String(20), default='pending')
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class SiteSetting(db.Model):
        __tablename__ = 'site_settings'
        id = db.Column(db.Integer, primary_key=True)
        key = db.Column(db.String(100), unique=True, nullable=False, index=True)
        value = db.Column(db.Text)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class Table(db.Model):
        __tablename__ = 'tables'
        id = db.Column(db.Integer, primary_key=True)
        number = db.Column(db.String(10), unique=True, nullable=False, index=True)
        capacity = db.Column(db.Integer, default=2)
        x_pos = db.Column(db.Float, default=0)
        y_pos = db.Column(db.Float, default=0)
        status = db.Column(db.String(20), default='available', index=True)
        current_guests = db.Column(db.Integer, default=0)
        notes = db.Column(db.Text)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class WaitlistEntry(db.Model):
        __tablename__ = 'waitlist'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        phone = db.Column(db.String(50), nullable=False, index=True)
        guests = db.Column(db.String(10), nullable=False)
        notified = db.Column(db.Boolean, default=False, index=True)
        seated = db.Column(db.Boolean, default=False, index=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    class GiftCard(db.Model):
        __tablename__ = 'gift_cards'
        id = db.Column(db.Integer, primary_key=True)
        code = db.Column(db.String(20), unique=True, nullable=False, index=True)
        balance = db.Column(db.Float, default=0.0)
        original_amount = db.Column(db.Float, default=0.0)
        purchaser_name = db.Column(db.String(100))
        purchaser_email = db.Column(db.String(120))
        recipient_name = db.Column(db.String(100))
        recipient_email = db.Column(db.String(120))
        message = db.Column(db.Text)
        status = db.Column(db.String(20), default='active', index=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        expires_at = db.Column(db.DateTime)

    class LoyaltyMember(db.Model):
        __tablename__ = 'loyalty_members'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False, index=True)
        phone = db.Column(db.String(50))
        points = db.Column(db.Integer, default=0)
        lifetime_spend = db.Column(db.Float, default=0.0)
        visits = db.Column(db.Integer, default=0)
        last_visit = db.Column(db.DateTime)
        birthday = db.Column(db.String(20))
        allergies = db.Column(db.Text)
        preferences = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class DailySpecial(db.Model):
        __tablename__ = 'daily_specials'
        id = db.Column(db.Integer, primary_key=True)
        day_of_week = db.Column(db.String(10), nullable=False, index=True)
        title = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)
        price = db.Column(db.Float)
        image = db.Column(db.String(500))
        active = db.Column(db.Boolean, default=True, index=True)

    class CustomerVisit(db.Model):
        __tablename__ = 'customer_visits'
        id = db.Column(db.Integer, primary_key=True)
        loyalty_id = db.Column(db.Integer, db.ForeignKey('loyalty_members.id'), index=True)
        order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
        reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'))
        spend = db.Column(db.Float, default=0.0)
        rating = db.Column(db.Integer)
        notes = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class AuditLog(db.Model):
        __tablename__ = 'audit_logs'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
        action = db.Column(db.String(100), nullable=False, index=True)
        entity_type = db.Column(db.String(50), nullable=False)
        entity_id = db.Column(db.String(50))
        old_value = db.Column(db.Text)
        new_value = db.Column(db.Text)
        ip_address = db.Column(db.String(45))
        user_agent = db.Column(db.String(500))
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    class WebhookEndpoint(db.Model):
        __tablename__ = 'webhook_endpoints'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        url = db.Column(db.String(500), nullable=False)
        event_types = db.Column(db.Text)
        secret = db.Column(db.String(100))
        active = db.Column(db.Boolean, default=True, index=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class WebhookDelivery(db.Model):
        __tablename__ = 'webhook_deliveries'
        id = db.Column(db.Integer, primary_key=True)
        endpoint_id = db.Column(db.Integer, db.ForeignKey('webhook_endpoints.id'))
        event_type = db.Column(db.String(50), nullable=False)
        payload = db.Column(db.Text)
        response_status = db.Column(db.Integer)
        response_body = db.Column(db.Text)
        success = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ─── Helpers ───────────────────────────────────────────────────────

    def deep_merge(default, current):
        if isinstance(default, dict) and isinstance(current, dict):
            result = current.copy()
            for key, value in default.items():
                if key not in result:
                    result[key] = value
                else:
                    result[key] = deep_merge(value, result[key])
            return result
        return current

    def load_data():
        with _data_lock:
            if os.path.exists(DATA_FILE):
                try:
                    with open(DATA_FILE, 'r', encoding='utf-8') as f:
                        current = json.load(f)
                    return deep_merge(DEFAULT_DATA, current)
                except (json.JSONDecodeError, IOError):
                    return DEFAULT_DATA.copy()
            return DEFAULT_DATA.copy()

    def save_data(data_obj):
        with _data_lock:
            try:
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data_obj, f, indent=2, ensure_ascii=False)
            except IOError as e:
                app.logger.error(f"Failed to save data: {e}")

    def init_db():
        with app.app_context():
            db.create_all()
            if User.query.count() == 0:
                admin = User(
                    username='admin', 
                    password_hash=generate_password_hash('admin123'), 
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("\n" + "=" * 60)
                print("  ADMIN CREDENTIALS")
                print("=" * 60)
                print("  Username: admin")
                print("  Password: admin123")
                print("=" * 60 + "\n")

    def track_page_view(page):
        try:
            pv = PageView(
                page=page,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:500],
                referrer=request.referrer
            )
            db.session.add(pv)
            db.session.commit()
        except Exception:
            db.session.rollback()

    def log_audit(action, entity_type, entity_id=None, old_value=None, new_value=None):
        try:
            log = AuditLog(
                user_id=session.get('user_id'),
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id) if entity_id else None,
                old_value=json.dumps(old_value) if old_value else None,
                new_value=json.dumps(new_value) if new_value else None,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:500]
            )
            db.session.add(log)
            db.session.commit()
        except Exception:
            db.session.rollback()

    def get_real_analytics():
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        total_views = PageView.query.count()
        week_views = PageView.query.filter(PageView.created_at >= week_ago).count()
        total_reservations = Reservation.query.count()
        pending_reservations = Reservation.query.filter_by(status='pending').count()
        today_reservations = Reservation.query.filter(
            Reservation.date == today.strftime('%Y-%m-%d')
        ).count()
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        total_revenue = db.session.query(db.func.sum(Order.total)).filter(
            Order.status.in_(['completed', 'ready'])
        ).scalar() or 0
        unread_messages = ContactMessage.query.filter_by(status='new').count()
        subscriber_count = NewsletterSubscriber.query.count()
        return {
            'total_views': total_views,
            'week_views': week_views,
            'total_reservations': total_reservations,
            'pending_reservations': pending_reservations,
            'today_reservations': today_reservations,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_revenue': round(total_revenue, 2),
            'unread_messages': unread_messages,
            'subscriber_count': subscriber_count
        }

    def get_featured_items():
        data = load_data()
        featured = []
        for category, items in data['menu'].items():
            for item in items:
                if item.get('popular') and len(featured) < 3:
                    featured.append(item)
        if len(featured) < 3:
            for category, items in data['menu'].items():
                if items and len(featured) < 3:
                    if items[0] not in featured:
                        featured.append(items[0])
                if len(featured) >= 3:
                    break
        return featured[:3]

    def sanitize_input(value, max_length=500):
        if value is None:
            return ''
        value = str(value).strip()
        value = re.sub(r'<script.*?>.*?</script>', '', value, flags=re.DOTALL | re.IGNORECASE)
        value = re.sub(r'<[^>]+>', '', value)
        if len(value) > max_length:
            value = value[:max_length]
        return value

    def validate_email(email):
        if not email:
            return None
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email.strip()):
            return email.strip().lower()
        return None

    def validate_phone(phone):
        if not phone:
            return False
        digits = re.sub(r'\D', '', phone)
        return len(digits) >= 7

    def check_reservation_capacity(date, time, guests):
        data = load_data()
        max_guests = data['reservations'].get('max_guests_per_slot', 30)
        existing = Reservation.query.filter_by(date=date, time=time).filter(
            Reservation.status.notin_(['cancelled', 'no-show', 'completed'])
        ).all()
        total_guests = sum(int(r.guests) for r in existing if r.guests.isdigit())
        requested = int(guests) if guests.isdigit() else 0
        remaining = max_guests - total_guests
        return (requested <= remaining, remaining)

    def send_email(to_email, subject, html_content, text_content=None):
        data = load_data()
        restaurant_name = data['restaurant']['name']
        api_key = app.config['SENDGRID_API_KEY']
        from_email = app.config['FROM_EMAIL']
        if not api_key:
            print(f"[EMAIL] To: {to_email} | Subject: {subject}")
            return True
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'personalizations': [{'to': [{'email': to_email}]}],
                'from': {'email': from_email, 'name': restaurant_name},
                'subject': subject,
                'content': [
                    {'type': 'text/plain', 'value': text_content or html_content},
                    {'type': 'text/html', 'value': html_content}
                ]
            }
            resp = requests.post(
                'https://api.sendgrid.com/v3/mail/send', 
                headers=headers, json=payload, timeout=10
            )
            return resp.status_code in (200, 201, 202)
        except Exception as e:
            app.logger.error(f"[EMAIL ERROR] {e}")
            return False

    def send_sms(to_phone, message):
        sid = app.config['TWILIO_SID']
        token = app.config['TWILIO_TOKEN']
        phone = app.config['TWILIO_PHONE']
        if not all([sid, token, phone]):
            print(f"[SMS] To: {to_phone} | {message}")
            return True
        try:
            resp = requests.post(
                f'https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json',
                auth=(sid, token),
                data={'From': phone, 'To': to_phone, 'Body': message},
                timeout=10
            )
            return resp.status_code == 201
        except Exception as e:
            app.logger.error(f"[SMS ERROR] {e}")
            return False

    def trigger_webhooks(event_type, payload):
        endpoints = WebhookEndpoint.query.filter_by(active=True).all()
        for ep in endpoints:
            try:
                event_types = json.loads(ep.event_types or '[]')
                if event_type in event_types:
                    sig = hashlib.sha256(
                        f"{ep.secret}{json.dumps(payload)}".encode()
                    ).hexdigest()
                    resp = requests.post(
                        ep.url,
                        json=payload,
                        headers={
                            'X-Webhook-Signature': sig,
                            'X-Event-Type': event_type,
                            'Content-Type': 'application/json'
                        },
                        timeout=10
                    )
                    delivery = WebhookDelivery(
                        endpoint_id=ep.id,
                        event_type=event_type,
                        payload=json.dumps(payload),
                        response_status=resp.status_code,
                        response_body=resp.text[:1000],
                        success=resp.status_code < 400
                    )
                    db.session.add(delivery)
                    db.session.commit()
            except Exception as e:
                app.logger.error(f"Webhook error: {e}")
                db.session.rollback()

    # ─── Decorators ────────────────────────────────────────────────────

    def admin_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            user = User.query.get(session['user_id'])
            if not user or user.role not in ('admin', 'manager', 'staff'):
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated

    def manager_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            user = User.query.get(session['user_id'])
            if not user or user.role not in ('admin', 'manager'):
                flash('Manager access required', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated

    def super_admin_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            user = User.query.get(session['user_id'])
            if not user or user.role != 'admin':
                flash('Admin access required', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated

    # ─── Context Processors ────────────────────────────────────────────

    @app.context_processor
    def inject_globals():
        data = load_data()
        return {
            'restaurant': data['restaurant'],
            'theme': data['theme'],
            'seo': data['seo'],
            'settings': data.get('settings', {}),
            'current_year': datetime.now().year,
            'csrf_token': lambda: session.get('_csrf_token', ''),
            'cart_count': len(session.get('cart', [])),
            'user_role': session.get('role', None)
        }

    # ─── Error Handlers ────────────────────────────────────────────────

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Not found'}), 404
        data = load_data()
        return render_template('home.html', 
            theme=data['theme'], 
            restaurant=data['restaurant'],
            menu=data['menu'], 
            testimonials=data['testimonials'],
            online_ordering=data['online_ordering'], 
            featured=get_featured_items(),
            seo=data['seo'], 
            settings=data['settings']
        ), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Server error: {e}")
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
        return "Internal Server Error", 500

    @app.errorhandler(429)
    def rate_limit(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Rate limit exceeded'}), 429
        flash('Too many requests. Please slow down.', 'error')
        return redirect(request.referrer or url_for('home'))

    # ─── Health Check ──────────────────────────────────────────────────

    @app.route('/health')
    def health_check():
        try:
            db.session.execute(db.text('SELECT 1'))
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '2.0.0-pro',
                'database': 'connected'
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 503

    # ─── Public Routes ─────────────────────────────────────────────────

    @app.route('/')
    def home():
        track_page_view('home')
        data = load_data()
        return render_template('home.html',
            theme=data['theme'], restaurant=data['restaurant'],
            menu=data['menu'], testimonials=data['testimonials'],
            online_ordering=data['online_ordering'], featured=get_featured_items(),
            seo=data['seo'], settings=data['settings'])

    @app.route('/menu')
    def menu_page():
        track_page_view('menu')
        data = load_data()
        return render_template('menu.html',
            theme=data['theme'], restaurant=data['restaurant'], menu=data['menu'],
            seo=data['seo'], settings=data['settings'])

    @app.route('/about')
    def about():
        track_page_view('about')
        data = load_data()
        return render_template('about.html',
            theme=data['theme'], restaurant=data['restaurant'], about=data['about'],
            current_year=datetime.now().year, seo=data['seo'])

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        track_page_view('contact')
        success = False
        error_msg = None
        data = load_data()
        if request.method == 'POST':
            name = sanitize_input(request.form.get('name', ''), 100)
            email = validate_email(request.form.get('email', ''))
            subject = sanitize_input(request.form.get('subject', ''), 100)
            message = sanitize_input(request.form.get('message', ''), 2000)
            if not name or not email or not subject or not message:
                error_msg = "Please fill in all required fields with valid data."
            else:
                try:
                    msg = ContactMessage(name=name, email=email, subject=subject, message=message)
                    db.session.add(msg)
                    db.session.commit()
                    success = True
                    log_audit('contact_created', 'ContactMessage', msg.id)
                    notification = app.config['NOTIFICATION_EMAIL']
                    if notification:
                        html = f"""<h2>New Contact Message</h2><p><strong>From:</strong> {name} ({email})</p><p><strong>Subject:</strong> {subject}</p><p>{message}</p>"""
                        send_email(notification, f"New Contact: {subject}", html)
                except Exception:
                    db.session.rollback()
                    error_msg = "Something went wrong. Please try again."
        return render_template('contact.html',
            theme=data['theme'], restaurant=data['restaurant'], success=success,
            error_msg=error_msg, seo=data['seo'])

    @app.route('/reservations', methods=['GET', 'POST'])
    def reservations():
        track_page_view('reservations')
        data = load_data()
        if not data['settings'].get('enable_reservations', True):
            flash('Reservations are currently disabled.', 'error')
            return redirect(url_for('home'))
        success = False
        error_msg = None
        if request.method == 'POST':
            name = sanitize_input(request.form.get('name', ''), 100)
            email = validate_email(request.form.get('email', ''))
            phone = request.form.get('phone', '').strip()
            date = request.form.get('date')
            time = request.form.get('time')
            guests = request.form.get('guests')
            special = sanitize_input(request.form.get('special_requests', ''), 500)
            if not name or not email or not validate_phone(phone) or not date or not time or not guests:
                error_msg = "Please fill in all required fields with valid data."
            else:
                ok, remaining = check_reservation_capacity(date, time, guests)
                if not ok:
                    error_msg = f"Sorry, only {remaining} seats remaining for this time slot. Please choose another time."
                else:
                    try:
                        res = Reservation(name=name, email=email, phone=phone,
                            date=date, time=time, guests=guests, special_requests=special)
                        db.session.add(res)
                        db.session.commit()
                        success = True
                        log_audit('reservation_created', 'Reservation', res.id)
                        html = f"""<h2>Reservation Confirmed</h2><p>Hi {name},</p><p>Your reservation at {data['restaurant']['name']} has been received.</p><ul><li><strong>Date:</strong> {date}</li><li><strong>Time:</strong> {time}</li><li><strong>Guests:</strong> {guests}</li></ul><p>We look forward to seeing you!</p>"""
                        send_email(email, f"Reservation Confirmed — {data['restaurant']['name']}", html)
                        notification = app.config['NOTIFICATION_EMAIL']
                        if notification:
                            send_email(notification, "New Reservation",
                                f"<p>New reservation from {name} for {guests} on {date} at {time}</p>")
                        trigger_webhooks('reservation.created', {
                            'id': res.id, 'name': name, 'email': email,
                            'date': date, 'time': time, 'guests': guests
                        })
                    except Exception:
                        db.session.rollback()
                        error_msg = "Something went wrong. Please try again."
        return render_template('reservations.html',
            theme=data['theme'], restaurant=data['restaurant'],
            reservations=data['reservations'], success=success, error_msg=error_msg,
            seo=data['seo'])


    @app.route('/widget/reservation')
    def widget_reservation():
        data = load_data()
        return render_template('widget_reservation.html',
            theme=data['theme'], restaurant=data['restaurant'],
            reservations=data['reservations'], seo=data['seo'])

    @app.route('/order')
    def order_online():
        track_page_view('order')
        data = load_data()
        if not data['settings'].get('enable_online_ordering', True):
            flash('Online ordering is currently disabled.', 'error')
            return redirect(url_for('home'))
        return render_template('order.html',
            theme=data['theme'], restaurant=data['restaurant'],
            online_ordering=data['online_ordering'], menu=data['menu'],
            seo=data['seo'], settings=data['settings'])

    @app.route('/gallery')
    def gallery():
        track_page_view('gallery')
        data = load_data()
        if not data['settings'].get('enable_gallery', True):
            return redirect(url_for('home'))
        return render_template('gallery.html',
            theme=data['theme'], restaurant=data['restaurant'], gallery=data['gallery'],
            seo=data['seo'])

    @app.route('/events')
    def events():
        track_page_view('events')
        data = load_data()
        if not data['settings'].get('enable_events', True):
            return redirect(url_for('home'))
        return render_template('events.html',
            theme=data['theme'], restaurant=data['restaurant'], events=data['events'],
            seo=data['seo'])

    # ─── Cart & Checkout ───────────────────────────────────────────────

    @app.route('/order/menu')
    def order_menu():
        data = load_data()
        if not data['settings'].get('enable_online_ordering', True):
            flash('Online ordering is currently disabled.', 'error')
            return redirect(url_for('home'))
        track_page_view('order_menu')
        return render_template('orders.html',
            theme=data['theme'], restaurant=data['restaurant'],
            menu=data['menu'], settings=data['settings'], seo=data['seo'])

    @app.route('/cart')
    def cart():
        data = load_data()
        cart_items = session.get('cart', [])
        total = sum(item['price'] * item['quantity'] for item in cart_items)
        tax = round(total * (data['settings'].get('tax_rate', 8.5) / 100), 2)
        delivery_fee = data['settings'].get('delivery_fee', 5.0) if session.get('order_type') == 'delivery' else 0
        grand_total = round(total + tax + delivery_fee, 2)
        return render_template('cart.html',
            theme=data['theme'], restaurant=data['restaurant'],
            cart=cart_items, total=total, tax=tax, delivery_fee=delivery_fee,
            grand_total=grand_total, settings=data['settings'], seo=data['seo'])

    @app.route('/api/cart/add', methods=['POST'])
    @limiter.limit("30 per minute")
    def cart_add():
        item = request.json
        if not item or 'name' not in item or 'price' not in item:
            return jsonify({'success': False, 'message': 'Invalid item'}), 400
        cart = session.get('cart', [])
        for c in cart:
            if c['name'] == item['name']:
                c['quantity'] += item.get('quantity', 1)
                session['cart'] = cart
                return jsonify({'success': True, 'count': len(cart)})
        cart.append({
            'name': sanitize_input(item['name'], 100),
            'price': float(item['price']),
            'quantity': max(1, int(item.get('quantity', 1))),
            'category': sanitize_input(item.get('category', ''), 50),
            'image': sanitize_input(item.get('image', ''), 500)
        })
        session['cart'] = cart
        return jsonify({'success': True, 'count': len(cart)})

    @app.route('/api/cart/remove', methods=['POST'])
    def cart_remove():
        name = request.json.get('name')
        cart = session.get('cart', [])
        cart = [c for c in cart if c['name'] != name]
        session['cart'] = cart
        return jsonify({'success': True})

    @app.route('/api/cart/clear', methods=['POST'])
    def cart_clear():
        session['cart'] = []
        return jsonify({'success': True})

    @app.route('/checkout', methods=['GET', 'POST'])
    def checkout():
        data = load_data()
        if not data['settings'].get('enable_online_ordering', True):
            return redirect(url_for('home'))
        cart_items = session.get('cart', [])
        if not cart_items:
            flash('Your cart is empty', 'error')
            return redirect(url_for('order_menu'))
        total = sum(item['price'] * item['quantity'] for item in cart_items)
        tax = round(total * (data['settings'].get('tax_rate', 8.5) / 100), 2)
        delivery_fee = data['settings'].get('delivery_fee', 5.0) if request.form.get('order_type') == 'delivery' else 0
        grand_total = round(total + tax + delivery_fee, 2)
        if request.method == 'POST':
            name = sanitize_input(request.form.get('name', ''), 100)
            email = validate_email(request.form.get('email', ''))
            phone = request.form.get('phone', '').strip()
            order_type = request.form.get('order_type', 'pickup')
            notes = sanitize_input(request.form.get('notes', ''), 1000)
            if not name or not email or not validate_phone(phone):
                flash('Please fill in all required fields with valid data.', 'error')
            else:
                try:
                    order = Order(
                        customer_name=name, customer_email=email, customer_phone=phone,
                        order_type=order_type, total=grand_total, status='pending', notes=notes
                    )
                    db.session.add(order)
                    db.session.flush()
                    for item in cart_items:
                        oi = OrderItem(
                            order_id=order.id, name=item['name'], price=item['price'],
                            quantity=item['quantity'], category=item.get('category', '')
                        )
                        db.session.add(oi)
                    db.session.commit()
                    session['cart'] = []
                    log_audit('order_created', 'Order', order.id, None, {'total': grand_total})
                    html = f"""<h2>Order Confirmed</h2><p>Hi {name},</p><p>Your order #{order.id} at {data['restaurant']['name']} has been received.</p><p><strong>Total:</strong> ${grand_total}</p><p>We'll notify you when it's ready!</p>"""
                    send_email(email, f"Order Confirmed — #{order.id}", html)
                    notification = app.config['NOTIFICATION_EMAIL']
                    if notification:
                        send_email(notification, f"New Order #{order.id}",
                            f"<p>New order from {name} for ${grand_total}</p>")
                    trigger_webhooks('order.created', {
                        'id': order.id, 'customer': name, 'total': grand_total, 'type': order_type
                    })
                    flash(f'Order #{order.id} placed successfully!', 'success')
                    return redirect(url_for('home'))
                except Exception:
                    db.session.rollback()
                    flash('Something went wrong. Please try again.', 'error')
        return render_template('checkout.html',
            theme=data['theme'], restaurant=data['restaurant'],
            cart=cart_items, total=total, tax=tax, delivery_fee=delivery_fee,
            grand_total=grand_total, settings=data['settings'], seo=data['seo'])

    # ─── Newsletter ────────────────────────────────────────────────────

    @app.route('/api/newsletter/subscribe', methods=['POST'])
    @limiter.limit("10 per minute")
    def newsletter_subscribe():
        email = validate_email(request.json.get('email', ''))
        if not email:
            return jsonify({'success': False, 'message': 'Invalid email address'})
        existing = NewsletterSubscriber.query.filter_by(email=email).first()
        if existing:
            return jsonify({'success': False, 'message': 'Already subscribed!'})
        sub = NewsletterSubscriber(email=email)
        db.session.add(sub)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Subscribed successfully!'})

    # ─── Auth Routes ───────────────────────────────────────────────────

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = sanitize_input(request.form.get('username', ''), 80)
            password = request.form.get('password', '')
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                user.last_login = datetime.utcnow()
                db.session.commit()
                log_audit('user_login', 'User', user.id)
                return redirect(url_for('dashboard'))
            flash('Invalid username or password', 'error')
            log_audit('login_failed', 'User', None, {'username': username})
        data = load_data()
        return render_template('login.html', theme=data['theme'], restaurant=data['restaurant'])

    @app.route('/logout')
    def logout():
        log_audit('user_logout', 'User', session.get('user_id'))
        session.clear()
        return redirect(url_for('home'))

    # ─── Admin Routes ──────────────────────────────────────────────────

    @app.route('/dashboard')
    @admin_required
    def dashboard():
        data = load_data()
        real_stats = get_real_analytics()
        recent_reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(10).all()
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        recent_messages = ContactMessage.query.filter_by(status='new').order_by(ContactMessage.created_at.desc()).limit(5).all()
        week_ago = datetime.utcnow().date() - timedelta(days=7)
        views_by_page = {}
        for pv in PageView.query.filter(PageView.created_at >= week_ago).all():
            views_by_page[pv.page] = views_by_page.get(pv.page, 0) + 1
        daily_views = []
        for i in range(7):
            day = datetime.utcnow().date() - timedelta(days=6-i)
            count = PageView.query.filter(db.func.date(PageView.created_at) == day).count()
            daily_views.append(count)
        return render_template('dashboard.html',
            theme=data['theme'], restaurant=data['restaurant'],
            analytics=data['analytics'], real_stats=real_stats,
            reservations=recent_reservations, orders=recent_orders,
            messages=recent_messages, views_by_page=views_by_page,
            daily_views=daily_views, seo=data['seo'])

    @app.route('/editor')
    @manager_required
    def editor():
        data = load_data()
        return render_template('editor.html',
            theme=data['theme'], restaurant=data['restaurant'],
            about=data['about'], menu=data['menu'], testimonials=data['testimonials'],
            online_ordering=data['online_ordering'], gallery=data['gallery'],
            events=data['events'], analytics=data['analytics'],
            seo=data['seo'], settings=data['settings'])


    @app.route('/admin/test-email', methods=['POST'])
    @super_admin_required
    def test_email():
        data = load_data()
        to_email = app.config['NOTIFICATION_EMAIL'] or app.config['FROM_EMAIL']
        if not to_email:
            flash('No notification email configured. Set one in Settings first.', 'error')
            return redirect(url_for('admin_settings'))
        html = f"""<h2>Test Email from {data['restaurant']['name']}</h2><p>This is a test email to confirm your email configuration is working correctly.</p><p>Sent at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>"""
        if send_email(to_email, f"Test Email — {data['restaurant']['name']}", html):
            flash('Test email sent successfully! Check your inbox.', 'success')
        else:
            flash('Failed to send test email. Check your SendGrid API key and from email.', 'error')
        return redirect(url_for('admin_settings'))

    @app.route('/change_password', methods=['GET', 'POST'])
    @admin_required
    def change_password():
        if request.method == 'POST':
            current = request.form.get('current_password', '')
            new_pass = request.form.get('new_password', '')
            confirm = request.form.get('confirm_password', '')
            user = User.query.get(session['user_id'])
            if not check_password_hash(user.password_hash, current):
                flash('Current password is incorrect', 'error')
            elif len(new_pass) < 6:
                flash('New password must be at least 6 characters', 'error')
            elif new_pass != confirm:
                flash('New passwords do not match', 'error')
            else:
                old_hash = user.password_hash
                user.password_hash = generate_password_hash(new_pass)
                db.session.commit()
                log_audit('password_changed', 'User', user.id, {'old_hash': old_hash[:20]})
                flash('Password changed successfully! Please log in again.', 'success')
                session.clear()
                return redirect(url_for('login'))
        data = load_data()
        return render_template('change_password.html', theme=data['theme'], restaurant=data['restaurant'])

    @app.route('/admin/settings', methods=['GET', 'POST'])
    @super_admin_required
    def admin_settings():
        data = load_data()
        if request.method == 'POST':
            old_settings = data['settings'].copy()
            data['settings']['sendgrid_api_key'] = sanitize_input(request.form.get('sendgrid_api_key', ''), 200)
            data['settings']['from_email'] = validate_email(request.form.get('from_email', '')) or ''
            data['settings']['notification_email'] = validate_email(request.form.get('notification_email', '')) or ''
            data['settings']['currency'] = sanitize_input(request.form.get('currency', '$'), 5)
            data['settings']['tax_rate'] = float(request.form.get('tax_rate', 8.5) or 0)
            data['settings']['delivery_fee'] = float(request.form.get('delivery_fee', 5.0) or 0)
            data['settings']['min_order'] = float(request.form.get('min_order', 15.0) or 0)
            data['settings']['enable_online_ordering'] = bool(request.form.get('enable_online_ordering'))
            data['settings']['enable_reservations'] = bool(request.form.get('enable_reservations'))
            data['settings']['enable_events'] = bool(request.form.get('enable_events'))
            data['settings']['enable_gallery'] = bool(request.form.get('enable_gallery'))
            data['settings']['cookie_consent'] = bool(request.form.get('cookie_consent'))
            save_data(data)
            log_audit('settings_updated', 'Settings', None, old_settings, data['settings'])
            flash('Settings saved successfully', 'success')
        return render_template('admin_settings.html',
            theme=data['theme'], restaurant=data['restaurant'],
            settings=data.get('settings', {}))

    @app.route('/admin/messages')
    @admin_required
    def messages_inbox():
        status_filter = request.args.get('status', 'all')
        query = ContactMessage.query
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        msgs = query.order_by(ContactMessage.created_at.desc()).all()
        data = load_data()
        return render_template('messages.html',
            theme=data['theme'], restaurant=data['restaurant'],
            messages=msgs, status_filter=status_filter)

    @app.route('/admin/messages/<int:id>/reply', methods=['POST'])
    @admin_required
    def message_reply(id):
        msg = ContactMessage.query.get_or_404(id)
        reply_text = sanitize_input(request.form.get('reply', ''), 2000)
        if reply_text:
            msg.reply = reply_text
            msg.status = 'replied'
            db.session.commit()
            log_audit('message_replied', 'ContactMessage', msg.id)
            html = f"""<h2>Reply from {load_data()['restaurant']['name']}</h2><p>Hi {msg.name},</p><p>{reply_text}</p><p>Best regards,<br>{load_data()['restaurant']['name']}</p>"""
            send_email(msg.email, f"Re: {msg.subject}", html)
            flash('Reply sent', 'success')
        return redirect(url_for('messages_inbox'))

    @app.route('/admin/messages/<int:id>/archive', methods=['POST'])
    @admin_required
    def message_archive(id):
        msg = ContactMessage.query.get_or_404(id)
        msg.status = 'archived'
        db.session.commit()
        log_audit('message_archived', 'ContactMessage', msg.id)
        flash('Message archived', 'success')
        return redirect(url_for('messages_inbox'))

    @app.route('/admin/reservations')
    @admin_required
    def reservations_admin():
        status_filter = request.args.get('status', 'all')
        date_filter = request.args.get('date', '')
        query = Reservation.query
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        if date_filter:
            query = query.filter_by(date=date_filter)
        res = query.order_by(Reservation.date.desc(), Reservation.time.asc()).all()
        data = load_data()
        return render_template('reservations_admin.html',
            theme=data['theme'], restaurant=data['restaurant'],
            reservations=res, status_filter=status_filter, date_filter=date_filter)

    @app.route('/admin/reservations/<int:id>/status', methods=['POST'])
    @admin_required
    def reservation_status(id):
        res = Reservation.query.get_or_404(id)
        new_status = request.json.get('status')
        if new_status in ('pending', 'confirmed', 'cancelled', 'completed', 'no-show'):
            old_status = res.status
            res.status = new_status
            db.session.commit()
            log_audit('reservation_status_changed', 'Reservation', res.id, {'status': old_status}, {'status': new_status})
            if new_status == 'confirmed':
                html = f"""<h2>Reservation Confirmed</h2><p>Hi {res.name},</p><p>Your reservation for {res.guests} guests on {res.date} at {res.time} has been confirmed.</p><p>We look forward to seeing you!</p>"""
                send_email(res.email, f"Reservation Confirmed — {load_data()['restaurant']['name']}", html)
            elif new_status == 'cancelled':
                html = f"""<h2>Reservation Cancelled</h2><p>Hi {res.name},</p><p>Your reservation for {res.guests} guests on {res.date} at {res.time} has been cancelled.</p><p>If you have questions, please contact us.</p>"""
                send_email(res.email, f"Reservation Cancelled — {load_data()['restaurant']['name']}", html)
            trigger_webhooks('reservation.updated', {'id': res.id, 'status': new_status})
            return jsonify({'success': True})
        return jsonify({'success': False})

    @app.route('/admin/orders')
    @admin_required
    def orders_admin():
        status_filter = request.args.get('status', 'all')
        query = Order.query
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        orders = query.order_by(Order.created_at.desc()).all()
        data = load_data()
        return render_template('orders_admin.html',
            theme=data['theme'], restaurant=data['restaurant'],
            orders=orders, status_filter=status_filter, settings=data['settings'])

    @app.route('/admin/orders/<int:id>/status', methods=['POST'])
    @admin_required
    def order_status(id):
        order = Order.query.get_or_404(id)
        new_status = request.json.get('status')
        if new_status in ('pending', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled'):
            old_status = order.status
            order.status = new_status
            db.session.commit()
            log_audit('order_status_changed', 'Order', order.id, {'status': old_status}, {'status': new_status})
            if new_status in ('confirmed', 'ready', 'cancelled'):
                html = f"""<h2>Order Update</h2><p>Hi {order.customer_name},</p><p>Your order #{order.id} status has been updated to: <strong>{new_status.title()}</strong>.</p>"""
                send_email(order.customer_email, f"Order Update — #{order.id}", html)
            trigger_webhooks('order.updated', {'id': order.id, 'status': new_status})
            return jsonify({'success': True})
        return jsonify({'success': False})

    @app.route('/admin/staff')
    @super_admin_required
    def staff_management():
        staff = User.query.all()
        data = load_data()
        return render_template('staff.html',
            theme=data['theme'], restaurant=data['restaurant'],
            staff=staff)

    @app.route('/admin/staff/add', methods=['POST'])
    @super_admin_required
    def staff_add():
        username = sanitize_input(request.form.get('username', ''), 80)
        password = request.form.get('password', '')
        role = request.form.get('role', 'staff')
        if not username or not password or len(password) < 6:
            flash('Username and password (min 6 chars) required', 'error')
            return redirect(url_for('staff_management'))
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('staff_management'))
        user = User(username=username, password_hash=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.commit()
        log_audit('staff_added', 'User', user.id, None, {'username': username, 'role': role})
        flash(f'Staff member {username} added', 'success')
        return redirect(url_for('staff_management'))

    @app.route('/admin/staff/<int:id>/delete', methods=['POST'])
    @super_admin_required
    def staff_delete(id):
        user = User.query.get_or_404(id)
        if user.id == session['user_id']:
            flash('Cannot delete yourself', 'error')
            return redirect(url_for('staff_management'))
        db.session.delete(user)
        db.session.commit()
        log_audit('staff_deleted', 'User', user.id)
        flash('Staff member removed', 'success')
        return redirect(url_for('staff_management'))

    # ─── API Routes ────────────────────────────────────────────────────

    @app.route('/api/update_theme', methods=['POST'])
    @manager_required
    def update_theme():
        data = load_data()
        old_theme = data['theme'].copy()
        data['theme'].update(request.json)
        save_data(data)
        log_audit('theme_updated', 'Theme', None, old_theme, data['theme'])
        return jsonify({'success': True})

    @app.route('/api/update_restaurant', methods=['POST'])
    @manager_required
    def update_restaurant():
        data = load_data()
        old = data['restaurant'].copy()
        data['restaurant'].update(request.json)
        save_data(data)
        log_audit('restaurant_info_updated', 'Restaurant', None, old, data['restaurant'])
        return jsonify({'success': True})

    @app.route('/api/update_hours', methods=['POST'])
    @manager_required
    def update_hours():
        data = load_data()
        old = data['restaurant']['hours'].copy()
        data['restaurant']['hours'] = request.json
        save_data(data)
        log_audit('hours_updated', 'Hours', None, old, data['restaurant']['hours'])
        return jsonify({'success': True})

    @app.route('/api/export/reservations')
    @admin_required
    def export_reservations():
        try:
            rows = Reservation.query.order_by(Reservation.created_at.desc()).all()
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Date', 'Time', 'Guests', 'Status', 'Special Requests', 'Created At'])
            for r in rows:
                writer.writerow([r.id, r.name, r.email, r.phone, r.date, r.time, r.guests, r.status, r.special_requests or '', r.created_at.strftime('%Y-%m-%d %H:%M') if r.created_at else ''])
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'reservations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
        except Exception as e:
            return f"Error exporting: {e}", 500

    @app.route('/api/export/messages')
    @admin_required
    def export_messages():
        try:
            rows = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Name', 'Email', 'Subject', 'Message', 'Status', 'Reply', 'Created At'])
            for r in rows:
                writer.writerow([r.id, r.name, r.email, r.subject, r.message, r.status, r.reply or '', r.created_at.strftime('%Y-%m-%d %H:%M') if r.created_at else ''])
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'messages_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
        except Exception as e:
            return f"Error exporting: {e}", 500

    @app.route('/api/export/orders')
    @admin_required
    def export_orders():
        try:
            rows = Order.query.order_by(Order.created_at.desc()).all()
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Customer', 'Email', 'Phone', 'Type', 'Total', 'Status', 'Notes', 'Created At'])
            for r in rows:
                writer.writerow([r.id, r.customer_name, r.customer_email, r.customer_phone, r.order_type, r.total, r.status, r.notes or '', r.created_at.strftime('%Y-%m-%d %H:%M') if r.created_at else ''])
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'orders_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
        except Exception as e:
            return f"Error exporting: {e}", 500

    @app.route('/api/update_social', methods=['POST'])
    @manager_required
    def update_social():
        data = load_data()
        old = data['restaurant']['social'].copy()
        data['restaurant']['social'] = request.json
        save_data(data)
        log_audit('social_updated', 'Social', None, old, data['restaurant']['social'])
        return jsonify({'success': True})

    @app.route('/api/update_about', methods=['POST'])
    @manager_required
    def update_about():
        data = load_data()
        updates = request.json
        for key, value in updates.items():
            if key in data['about'] and key not in ['values']:
                data['about'][key] = value
        save_data(data)
        log_audit('about_updated', 'About', None, None, updates)
        return jsonify({'success': True})

    @app.route('/api/update_testimonials', methods=['POST'])
    @manager_required
    def update_testimonials():
        data = load_data()
        old = data['testimonials'].copy()
        data['testimonials'] = request.json.get('testimonials', [])
        save_data(data)
        log_audit('testimonials_updated', 'Testimonials', None, old, data['testimonials'])
        return jsonify({'success': True})

    @app.route('/api/menu/add', methods=['POST'])
    @manager_required
    def add_menu_item():
        item = request.json
        category = item.get('category')
        data = load_data()
        if category in data['menu']:
            data['menu'][category].append({
                'name': sanitize_input(item['name'], 100),
                'description': sanitize_input(item['description'], 500),
                'price': float(item['price']),
                'popular': item.get('popular', False),
                'image': sanitize_input(item.get('image', ''), 500),
                'dietary': item.get('dietary', [])
            })
            save_data(data)
            log_audit('menu_item_added', 'Menu', None, None, {'category': category, 'name': item['name']})
            return jsonify({'success': True})
        return jsonify({'success': False})

    @app.route('/api/menu/delete', methods=['POST'])
    @manager_required
    def delete_menu_item():
        category = request.json.get('category')
        index = int(request.json.get('index', -1))
        data = load_data()
        if category in data['menu'] and 0 <= index < len(data['menu'][category]):
            old = data['menu'][category][index]
            data['menu'][category].pop(index)
            save_data(data)
            log_audit('menu_item_deleted', 'Menu', None, old, None)
            return jsonify({'success': True})
        return jsonify({'success': False})

    @app.route('/api/menu/update', methods=['POST'])
    @manager_required
    def update_menu_item():
        payload = request.json
        category = payload.get('category')
        index = int(payload.get('index', -1))
        item_data = payload.get('item', payload)
        data = load_data()
        if category in data['menu'] and 0 <= index < len(data['menu'][category]):
            old = data['menu'][category][index]
            data['menu'][category][index] = {
                'name': sanitize_input(item_data.get('name'), 100),
                'description': sanitize_input(item_data.get('description'), 500),
                'price': float(item_data.get('price', 0)),
                'popular': item_data.get('popular', False),
                'image': sanitize_input(item_data.get('image', ''), 500),
                'dietary': item_data.get('dietary', [])
            }
            save_data(data)
            log_audit('menu_item_updated', 'Menu', None, old, data['menu'][category][index])
            return jsonify({'success': True})
        return jsonify({'success': False})

    @app.route('/api/update_sales', methods=['POST'])
    @manager_required
    def update_sales():
        data = load_data()
        sales = request.json.get('sales', [])
        if len(sales) == 7:
            old = data['analytics']['daily_sales'].copy()
            data['analytics']['daily_sales'] = sales
            save_data(data)
            log_audit('sales_updated', 'Analytics', None, old, sales)
            return jsonify({'success': True})
        return jsonify({'success': False})

    @app.route('/api/update_revenue', methods=['POST'])
    @manager_required
    def update_revenue():
        data = load_data()
        revenue = request.json.get('revenue', [])
        if len(revenue) == 6:
            old = data['analytics']['monthly_revenue'].copy()
            data['analytics']['monthly_revenue'] = revenue
            save_data(data)
            log_audit('revenue_updated', 'Analytics', None, old, revenue)
            return jsonify({'success': True})
        return jsonify({'success': False})

    @app.route('/api/update_seo', methods=['POST'])
    @manager_required
    def update_seo():
        data = load_data()
        old = data['seo'].copy()
        data['seo'].update(request.json)
        save_data(data)
        log_audit('seo_updated', 'SEO', None, old, data['seo'])
        return jsonify({'success': True})

    @app.route('/api/upload_image', methods=['POST'])
    @manager_required
    def upload_image():
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image provided'})
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No image selected'})
        try:
            upload_result = cloudinary.uploader.upload(file, folder="restaurant")
            return jsonify({'success': True, 'url': upload_result['secure_url']})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    @app.route('/api/update_custom_css', methods=['POST'])
    @manager_required
    def update_custom_css():
        data = load_data()
        old = data['theme'].get('custom_css', '')
        data['theme']['custom_css'] = request.json.get('custom_css', '')
        save_data(data)
        log_audit('custom_css_updated', 'Theme', None, None, None)
        return jsonify({'success': True})

    @app.route('/api/reset_data', methods=['POST'])
    @super_admin_required
    def reset_data():
        save_data(DEFAULT_DATA.copy())
        log_audit('data_reset', 'System', None, None, None)
        return jsonify({'success': True})

    @app.route('/api/backup')
    @super_admin_required
    def backup_data():
        data = load_data()
        backup = {
            'data': data,
            'exported_at': datetime.utcnow().isoformat(),
            'db_stats': {
                'users': User.query.count(),
                'reservations': Reservation.query.count(),
                'orders': Order.query.count(),
                'messages': ContactMessage.query.count(),
                'subscribers': NewsletterSubscriber.query.count(),
                'page_views': PageView.query.count()
            }
        }
        output = io.BytesIO(json.dumps(backup, indent=2, ensure_ascii=False).encode('utf-8'))
        return send_file(output, mimetype='application/json',
            as_attachment=True, download_name=f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

    @app.route('/api/restore', methods=['POST'])
    @super_admin_required
    def restore_data():
        if 'backup' not in request.files:
            return jsonify({'success': False, 'message': 'No backup file provided'})
        file = request.files['backup']
        try:
            backup = json.load(file)
            restored = deep_merge(DEFAULT_DATA, backup.get('data', {}))
            save_data(restored)
            log_audit('data_restored', 'System', None, None, None)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    # ─── Webhook Management ────────────────────────────────────────────

    @app.route('/api/webhooks', methods=['GET', 'POST'])
    @super_admin_required
    def manage_webhooks():
        if request.method == 'POST':
            ep = WebhookEndpoint(
                name=sanitize_input(request.json.get('name', ''), 100),
                url=sanitize_input(request.json.get('url', ''), 500),
                event_types=json.dumps(request.json.get('event_types', [])),
                secret=secrets.token_hex(16)
            )
            db.session.add(ep)
            db.session.commit()
            log_audit('webhook_created', 'WebhookEndpoint', ep.id)
            return jsonify({'success': True, 'id': ep.id, 'secret': ep.secret})
        endpoints = WebhookEndpoint.query.all()
        return jsonify([{
            'id': e.id, 'name': e.name, 'url': e.url,
            'event_types': json.loads(e.event_types or '[]'),
            'active': e.active
        } for e in endpoints])

    # ─── SEO / Static Routes ───────────────────────────────────────────

    @app.route('/sitemap.xml')
    def sitemap():
        pages = [
            {'loc': request.url_root, 'priority': '1.0', 'changefreq': 'daily'},
            {'loc': request.url_root + 'menu', 'priority': '0.9', 'changefreq': 'weekly'},
            {'loc': request.url_root + 'about', 'priority': '0.8', 'changefreq': 'monthly'},
            {'loc': request.url_root + 'contact', 'priority': '0.8', 'changefreq': 'monthly'},
            {'loc': request.url_root + 'reservations', 'priority': '0.9', 'changefreq': 'daily'},
            {'loc': request.url_root + 'order', 'priority': '0.8', 'changefreq': 'weekly'},
            {'loc': request.url_root + 'gallery', 'priority': '0.7', 'changefreq': 'weekly'},
            {'loc': request.url_root + 'events', 'priority': '0.7', 'changefreq': 'weekly'},
        ]
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for page in pages:
            xml += f"  <url>\n"
            xml += f"    <loc>{page['loc']}</loc>\n"
            xml += f"    <priority>{page['priority']}</priority>\n"
            xml += f"    <changefreq>{page['changefreq']}</changefreq>\n"
            xml += f"  </url>\n"
        xml += '</urlset>'
        return Response(xml, mimetype='application/xml')

    @app.route('/robots.txt')
    def robots():
        content = f"""User-agent: *\nAllow: /\nSitemap: {request.url_root}sitemap.xml\n"""
        return Response(content, mimetype='text/plain')

    @app.route('/manifest.json')
    def manifest():
        data = load_data()
        return jsonify({
            "name": data['restaurant']['name'],
            "short_name": data['restaurant']['name'],
            "description": data['restaurant']['tagline'],
            "start_url": "/",
            "display": "standalone",
            "background_color": data['theme']['background_color'],
            "theme_color": data['theme']['primary_color'],
            "icons": [
                {"src": "/static/icon.svg", "sizes": "any", "type": "image/svg+xml"},
                {"src": "/static/icon-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "/static/icon-512.png", "sizes": "512x512", "type": "image/png"}
            ]
        })

    @app.route('/api/schema')
    def schema_json():
        data = load_data()
        return jsonify({
            "@context": "https://schema.org",
            "@type": "Restaurant",
            "name": data['restaurant']['name'],
            "description": data['restaurant']['tagline'],
            "address": {
                "@type": "PostalAddress",
                "streetAddress": data['restaurant']['address']
            },
            "telephone": data['restaurant']['phone'],
            "email": data['restaurant']['email'],
            "openingHours": [f"Mo-Su {h}" for h in data['restaurant']['hours'].values()],
            "servesCuisine": "Italian",
            "priceRange": "$$",
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": str(data['analytics']['customer_satisfaction']),
                "reviewCount": str(len(data['testimonials']))
            }
        })


    # ─── Gift Cards ────────────────────────────────────────────────────

    @app.route('/gift-cards')
    def gift_cards():
        data = load_data()
        if not data['settings'].get('enable_gift_cards', True):
            flash('Gift cards are currently disabled.', 'error')
            return redirect(url_for('home'))
        track_page_view('gift_cards')
        return render_template('gift_cards.html',
            theme=data['theme'], restaurant=data['restaurant'],
            settings=data['settings'], seo=data['seo'])

    @app.route('/api/gift-card/purchase', methods=['POST'])
    @limiter.limit("10 per minute")
    def gift_card_purchase():
        data = load_data()
        payload = request.json
        amount = float(payload.get('amount', 0))
        if amount < 10:
            return jsonify({'success': False, 'message': 'Minimum amount is $10'})
        code = secrets.token_hex(8).upper()
        gc = GiftCard(
            code=code,
            balance=amount,
            original_amount=amount,
            purchaser_name=sanitize_input(payload.get('purchaser_name', ''), 100),
            purchaser_email=validate_email(payload.get('purchaser_email', '')) or '',
            recipient_name=sanitize_input(payload.get('recipient_name', ''), 100),
            recipient_email=validate_email(payload.get('recipient_email', '')) or '',
            message=sanitize_input(payload.get('message', ''), 500),
            status='active'
        )
        db.session.add(gc)
        db.session.commit()
        log_audit('gift_card_purchased', 'GiftCard', gc.id, None, {'amount': amount, 'code': code})
        if gc.recipient_email:
            html = f"""<h2>You Received a Gift Card!</h2><p>Hi {gc.recipient_name or 'there'},</p><p>{gc.purchaser_name or 'Someone'} has sent you a ${amount:.2f} gift card for {data['restaurant']['name']}.</p><p><strong>Code:</strong> {code}</p><p>Present this code on your next visit.</p>"""
            send_email(gc.recipient_email, f"Gift Card from {gc.purchaser_name or 'Someone'}", html)
        trigger_webhooks('gift_card.purchased', {'id': gc.id, 'amount': amount, 'code': code})
        return jsonify({'success': True, 'code': code})

    @app.route('/api/gift-card/balance', methods=['POST'])
    def gift_card_balance():
        code = request.json.get('code', '').upper().strip()
        gc = GiftCard.query.filter_by(code=code).first()
        if not gc:
            return jsonify({'success': False, 'message': 'Invalid gift card code'})
        return jsonify({'success': True, 'balance': round(gc.balance, 2), 'status': gc.status})

    # ─── Loyalty Program ───────────────────────────────────────────────

    @app.route('/loyalty')
    def loyalty():
        data = load_data()
        if not data['settings'].get('enable_loyalty', True):
            flash('Loyalty program is currently disabled.', 'error')
            return redirect(url_for('home'))
        track_page_view('loyalty')
        return render_template('loyalty.html',
            theme=data['theme'], restaurant=data['restaurant'],
            settings=data['settings'], seo=data['seo'])

    @app.route('/api/loyalty/enroll', methods=['POST'])
    @limiter.limit("10 per minute")
    def loyalty_enroll():
        payload = request.json
        email = validate_email(payload.get('email', ''))
        if not email:
            return jsonify({'success': False, 'message': 'Valid email required'})
        existing = LoyaltyMember.query.filter_by(email=email).first()
        if existing:
            return jsonify({'success': False, 'message': 'Already enrolled! Check your points below.'})
        member = LoyaltyMember(
            name=sanitize_input(payload.get('name', ''), 100),
            email=email,
            phone=sanitize_input(payload.get('phone', ''), 50),
            birthday=payload.get('birthday', ''),
            points=50
        )
        db.session.add(member)
        db.session.commit()
        log_audit('loyalty_enrolled', 'LoyaltyMember', member.id)
        trigger_webhooks('loyalty.enrolled', {'id': member.id, 'email': email, 'name': member.name})
        return jsonify({'success': True, 'message': f'Welcome to the rewards program! You have 50 bonus points.'})

    @app.route('/api/loyalty/check', methods=['POST'])
    def loyalty_check():
        email = validate_email(request.json.get('email', ''))
        if not email:
            return jsonify({'success': False, 'message': 'Valid email required'})
        member = LoyaltyMember.query.filter_by(email=email).first()
        if not member:
            return jsonify({'success': False, 'message': 'Member not found. Enroll above!'})
        return jsonify({
            'success': True,
            'name': member.name,
            'points': member.points,
            'lifetime_spend': round(member.lifetime_spend, 2),
            'visits': member.visits
        })

    # ─── Waitlist ──────────────────────────────────────────────────────

    @app.route('/waitlist', methods=['GET', 'POST'])
    def waitlist():
        data = load_data()
        if not data['settings'].get('enable_waitlist', True):
            flash('Waitlist is currently disabled.', 'error')
            return redirect(url_for('home'))
        track_page_view('waitlist')
        success = False
        if request.method == 'POST':
            name = sanitize_input(request.form.get('name', ''), 100)
            phone = request.form.get('phone', '').strip()
            guests = request.form.get('guests', '')
            if not name or not validate_phone(phone) or not guests:
                flash('Please fill in all required fields with valid data.', 'error')
            else:
                entry = WaitlistEntry(name=name, phone=phone, guests=guests)
                db.session.add(entry)
                db.session.commit()
                success = True
                log_audit('waitlist_joined', 'WaitlistEntry', entry.id)
                trigger_webhooks('waitlist.joined', {'id': entry.id, 'name': name, 'guests': guests})
        queue = WaitlistEntry.query.filter_by(seated=False).count()
        wait_estimate = max(queue * 15, 0)
        return render_template('waitlist.html',
            theme=data['theme'], restaurant=data['restaurant'],
            success=success, wait_estimate=wait_estimate,
            settings=data['settings'], seo=data['seo'])

    @app.route('/admin/waitlist')
    @admin_required
    def waitlist_admin():
        entries = WaitlistEntry.query.filter_by(seated=False).order_by(WaitlistEntry.created_at.asc()).all()
        data = load_data()
        return render_template('waitlist_admin.html',
            theme=data['theme'], restaurant=data['restaurant'],
            entries=entries, datetime=datetime, settings=data['settings'])

    @app.route('/admin/waitlist/<int:id>/notify', methods=['POST'])
    @admin_required
    def waitlist_notify(id):
        entry = WaitlistEntry.query.get_or_404(id)
        entry.notified = True
        db.session.commit()
        log_audit('waitlist_notified', 'WaitlistEntry', entry.id)
        send_sms(entry.phone, f"Your table at {load_data()['restaurant']['name']} is ready! Please see the host within 5 minutes.")
        flash('Guest notified via SMS', 'success')
        return redirect(url_for('waitlist_admin'))

    @app.route('/admin/waitlist/<int:id>/seat', methods=['POST'])
    @admin_required
    def waitlist_seat(id):
        entry = WaitlistEntry.query.get_or_404(id)
        entry.seated = True
        db.session.commit()
        log_audit('waitlist_seated', 'WaitlistEntry', entry.id)
        flash('Guest marked as seated', 'success')
        return redirect(url_for('waitlist_admin'))

    # ─── Table Management ──────────────────────────────────────────────

    @app.route('/admin/tables')
    @admin_required
    def tables_admin():
        tables = Table.query.all()
        data = load_data()
        return render_template('tables_admin.html',
            theme=data['theme'], restaurant=data['restaurant'],
            tables=tables, settings=data['settings'])

    @app.route('/api/tables/update', methods=['POST'])
    @admin_required
    def table_update():
        payload = request.json
        number = str(payload.get('number', ''))
        if not number:
            return jsonify({'success': False, 'message': 'Table number required'})
        table = Table.query.filter_by(number=number).first()
        if not table:
            table = Table(number=number)
            db.session.add(table)
        if 'capacity' in payload:
            table.capacity = int(payload['capacity'])
        if 'x_pos' in payload:
            table.x_pos = float(payload['x_pos'])
        if 'y_pos' in payload:
            table.y_pos = float(payload['y_pos'])
        if 'status' in payload:
            table.status = payload['status']
        if 'current_guests' in payload:
            table.current_guests = int(payload['current_guests'])
        db.session.commit()
        log_audit('table_updated', 'Table', table.id, None, {'number': number, 'status': table.status})
        return jsonify({'success': True})

    @app.route('/api/tables/delete', methods=['POST'])
    @admin_required
    def table_delete():
        number = request.json.get('number')
        table = Table.query.filter_by(number=number).first()
        if table:
            db.session.delete(table)
            db.session.commit()
            log_audit('table_deleted', 'Table', table.id)
        return jsonify({'success': True})

    # ─── Kitchen Display ───────────────────────────────────────────────

    @app.route('/kitchen')
    @admin_required
    def kitchen_display():
        data = load_data()
        if not data['settings'].get('enable_kitchen_display', True):
            flash('Kitchen display is currently disabled.', 'error')
            return redirect(url_for('dashboard'))
        orders = Order.query.filter(
            Order.status.in_(['pending', 'preparing', 'ready'])
        ).order_by(Order.created_at.asc()).all()
        return render_template('kitchen.html',
            theme=data['theme'], restaurant=data['restaurant'],
            orders=orders, settings=data['settings'])

    @app.route('/kitchen/orders')
    @admin_required
    def kitchen_orders_json():
        orders = Order.query.filter(
            Order.status.in_(['pending', 'preparing', 'ready'])
        ).order_by(Order.created_at.asc()).all()
        return jsonify([{
            'id': o.id,
            'status': o.status,
            'customer_name': o.customer_name,
            'order_type': o.order_type,
            'created_at': o.created_at.isoformat() if o.created_at else None,
            'items': [{'name': i.name, 'quantity': i.quantity, 'price': i.price} for i in o.items],
            'notes': o.notes
        } for o in orders])

    # ─── Customer CRM ──────────────────────────────────────────────────

    @app.route('/admin/customers')
    @admin_required
    def customers_admin():
        members = LoyaltyMember.query.order_by(LoyaltyMember.created_at.desc()).all()
        data = load_data()
        return render_template('customers_admin.html',
            theme=data['theme'], restaurant=data['restaurant'],
            members=members, settings=data['settings'])

    @app.route('/admin/customers/<int:id>')
    @admin_required
    def customer_detail(id):
        member = LoyaltyMember.query.get_or_404(id)
        orders = Order.query.filter_by(customer_email=member.email).order_by(Order.created_at.desc()).limit(10).all()
        reservations = Reservation.query.filter_by(email=member.email).order_by(Reservation.created_at.desc()).limit(10).all()
        data = load_data()
        return render_template('customer_detail.html',
            theme=data['theme'], restaurant=data['restaurant'],
            member=member, orders=orders, reservations=reservations,
            settings=data['settings'])

    # ─── QR Table Ordering ─────────────────────────────────────────────

    @app.route('/table/<number>')
    def table_order(number):
        data = load_data()
        table = Table.query.filter_by(number=number).first()
        if not table:
            abort(404)
        track_page_view('table_order')
        return render_template('table_order.html',
            theme=data['theme'], restaurant=data['restaurant'],
            table=table, menu=data['menu'],
            settings=data['settings'], cart_count=len(session.get('cart', [])),
            seo=data['seo'])

    # ─── Main ──────────────────────────────────────────────────────────

    with app.app_context():
        init_db()

    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("  RESTAURANT CMS PRO — v2.0")
    print("=" * 60)
    print("  Login:    admin / admin123")
    print("  Health:   http://localhost:5000/health")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
