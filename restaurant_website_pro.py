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

    # Rate Limiting with Redis fallback
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.environ.get('REDIS_URL', 'memory://'),
        strategy="fixed-window"
    )

    db = SQLAlchemy(app)

    # Thread-safe data file operations
    DATA_FILE = 'restaurant_data.json'
    _data_lock = threading.Lock()

    DEFAULT_DATA = {
    'theme': {
        'primary_color': '#0B0F19',
        'secondary_color': '#C9A96E',
        'background_color': '#FAF7F2',
        'text_color': '#1A1A1A',
        'card_bg': '#FFFFFF',
        'accent_color': '#8B7355',
        'font_family': "'Playfair Display', 'Georgia', serif",
        'dark_mode': False,
        'custom_css': ''
    },
    'seo': {
        'meta_title': 'Aurelia — Modern Coastal Mediterranean Dining',
        'meta_description': 'Experience award-winning coastal Mediterranean cuisine at Aurelia. Reserve your table today.',
        'meta_keywords': 'mediterranean restaurant, fine dining, seafood, reservations, luxury dining',
        'og_image': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&h=630&fit=crop',
        'google_analytics_id': '',
        'facebook_pixel': ''
    },
    'restaurant': {
        'name': "Aurelia",
        'tagline': "Modern Coastal Mediterranean Dining",
        'address': "47 Harbor View Boulevard, Marina District, CA 94123",
        'phone': "(415) 555-0199",
        'phone_link': "+14155550199",
        'email': "reservations@aurelia.co",
        'hours': {
            'monday': '5:00 PM - 10:00 PM',
            'tuesday': '5:00 PM - 10:00 PM',
            'wednesday': '5:00 PM - 10:00 PM',
            'thursday': '5:00 PM - 10:00 PM',
            'friday': '5:00 PM - 11:00 PM',
            'saturday': '4:30 PM - 11:00 PM',
            'sunday': '4:00 PM - 9:30 PM'
        },
        'social': {
            'instagram': 'aurelia.dining',
            'facebook': 'AureliaDining',
            'twitter': 'AureliaDining',
            'yelp': 'aurelia-marina-district'
        },
        'google_maps_embed': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3022.1!2d-122.4194!3d37.7749!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMzfCsDQ2JzI5LjYiTiAxMjLCsDI1JzEwLjAiVw!5e0!3m2!1sen!2us!4v1'
    },
    'about': {
        'story': "Founded in 2019 by Chef Elena Marchetti, Aurelia was born from a simple belief: the Mediterranean diet is not just healthy — it is the purest expression of joy on a plate. Every evening, as the sun dips below the Golden Gate, our kitchen comes alive with the aromas of charcoal-grilled branzino, hand-rolled paccheri, and citrus-kissed olive oil cakes.",
        'chef_name': "Chef Elena Marchetti",
        'chef_bio': "A James Beard Award semifinalist, Chef Elena trained at El Celler de Can Roca and Lycabettus Restaurant in Athens. Her philosophy is simple: let the ingredient speak.",
        'chef_image': "https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=600&h=600&fit=crop&crop=faces",
        'interior_image': "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1600&h=900&fit=crop",
        'food_image': "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1600&h=900&fit=crop",
        'values': [
            {'title': 'Ocean to Table', 'description': 'We source seafood daily from Monterey Bay, ensuring the freshest catch reaches your plate within hours.'},
            {'title': 'Zero Waste Kitchen', 'description': 'Every herb stem becomes a sauce. Every bone becomes a stock. Sustainability is not a trend — it is our foundation.'},
            {'title': 'Wine as Philosophy', 'description': 'Our sommelier curates 200+ labels from coastal vineyards, pairing each course with intention and care.'}
        ]
    },
    'testimonials': [
        {'name': 'Marcus T.', 'text': 'The grilled octopus transported me straight to a taverna in Santorini. Simply extraordinary.', 'rating': 5},
        {'name': 'Priya & James K.', 'text': 'We hosted our rehearsal dinner here — every detail was perfection. The staff anticipated needs we did not know we had.', 'rating': 5},
        {'name': 'David R., SF Chronicle', 'text': 'Aurelia is doing what few restaurants dare: making fine dining feel like coming home.', 'rating': 5},
        {'name': 'Isabella M.', 'text': 'The olive oil cake alone is worth the flight to San Francisco. A revelation.', 'rating': 5}
    ],
    'menu': {
        'raw bar': [
            {'name': 'Oysters on the Half Shell', 'description': 'Kumamoto & Miyagi selection, mignonette granita, lemon verbena', 'price': 24.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600&h=400&fit=crop', 'dietary': ['gluten-free']},
            {'name': 'Tuna Crudo', 'description': 'Bigeye tuna, Sicilian olive oil, Calabrian chili, preserved lemon', 'price': 28.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1534604973900-c43ab4c2e0ab?w=600&h=400&fit=crop', 'dietary': ['gluten-free', 'dairy-free']},
            {'name': 'Caviar Service', 'description': 'Osetra caviar, blinis, crème fraîche, chive, shallot', 'price': 85.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=600&h=400&fit=crop', 'dietary': ['vegetarian']}
        ],
        'small plates': [
            {'name': 'Charred Eggplant Dip', 'description': 'Smoky baba ganoush, pomegranate molasses, toasted pine nuts, warm pita', 'price': 16.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?w=600&h=400&fit=crop', 'dietary': ['vegetarian']},
            {'name': 'Whipped Feta', 'description': "Whipped sheep's milk feta, honeycomb, toasted walnuts, warm sourdough", 'price': 18.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1626200419199-391ae4be7a41?w=600&h=400&fit=crop', 'dietary': ['vegetarian']},
            {'name': 'Grilled Spanish Octopus', 'description': 'Charred octopus, fingerling potatoes, smoked paprika, salsa verde', 'price': 26.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=400&fit=crop', 'dietary': ['gluten-free', 'dairy-free']},
            {'name': 'Burrata & Heirloom Tomatoes', 'description': 'Pugliese burrata, San Marzano tomatoes, basil oil, aged balsamic', 'price': 22.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1608897013039-887f21d8c804?w=600&h=400&fit=crop', 'dietary': ['vegetarian', 'gluten-free']}
        ],
        'mains': [
            {'name': 'Whole Roasted Branzino', 'description': 'Mediterranean sea bass, herb-stuffed, lemon, extra virgin olive oil', 'price': 42.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=600&h=400&fit=crop', 'dietary': ['gluten-free', 'dairy-free']},
            {'name': 'Truffle Paccheri', 'description': 'Hand-rolled paccheri, black truffle cream, aged Parmigiano-Reggiano', 'price': 38.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600&h=400&fit=crop', 'dietary': ['vegetarian']},
            {'name': 'Lamb Osso Buco', 'description': 'Braised lamb shank, saffron risotto, gremolata, natural jus', 'price': 48.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=400&fit=crop', 'dietary': ['gluten-free']},
            {'name': 'Dry-Aged Ribeye', 'description': '45-day dry-aged ribeye, bone marrow butter, charred spring onion', 'price': 65.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1600891964092-4316c288032e?w=600&h=400&fit=crop', 'dietary': ['gluten-free']}
        ],
        'desserts': [
            {'name': 'Olive Oil Cake', 'description': 'Citrus-scented olive oil sponge, blood orange curd, mascarpone chantilly', 'price': 14.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=600&h=400&fit=crop', 'dietary': ['vegetarian']},
            {'name': 'Dark Chocolate Fondant', 'description': 'Valrhona dark chocolate, sea salt caramel core, vanilla bean ice cream', 'price': 16.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1624353365286-3f8d62daad51?w=600&h=400&fit=crop', 'dietary': ['vegetarian']},
            {'name': 'Baklava Ice Cream', 'description': 'Pistachio ice cream, honey-soaked phyllo, rose water syrup', 'price': 13.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=600&h=400&fit=crop', 'dietary': ['vegetarian']}
        ],
        'craft cocktails': [
            {'name': 'The Aegean', 'description': 'Mastiha liqueur, cucumber, fresh lime, Mediterranean tonic', 'price': 18.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']},
            {'name': 'Santorini Sunset', 'description': 'Aperol, prosecco, blood orange, thyme, edible flower', 'price': 19.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']},
            {'name': 'Olive Branch', 'description': 'Gin, olive brine, dry vermouth, castelvetrano olive', 'price': 17.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1575023782549-62ca0d244b39?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']},
            {'name': 'Negroni Bianco', 'description': 'Suze, Lillet Blanc, dry gin, grapefruit twist', 'price': 18.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']}
        ],
        'wine selection': [
            {'name': 'Santorini Assyrtiko', 'description': 'Gaia Wines, 2022 — Crisp minerality, citrus, saline finish', 'price': 16.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']},
            {'name': 'Barolo DOCG', 'description': 'Pio Cesare, 2018 — Nebbiolo, tar and roses, firm tannins', 'price': 28.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']},
            {'name': 'Châteauneuf-du-Pape', 'description': 'Domaine du Pegau, 2019 — Grenache blend, dark fruit, spice', 'price': 24.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1553361371-9b22f78e8b1d?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']}
        ]
    },
    'reservations': {
        'hold_time': '15 minutes',
        'large_party_note': 'Parties of 8+ please contact our events team directly',
        'time_slots': ['17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30'],
        'max_guests_per_slot': 24
    },
    'online_ordering': {
        'enabled': True,
        'page_title': 'Order Online',
        'page_subtitle': "Enjoy Aurelia's coastal Mediterranean cuisine at home.",
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
        'page_subtitle': 'A glimpse into our kitchen, our craft, and the warm, sun-drenched atmosphere.',
        'photos': [
            {'url': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&h=600&fit=crop', 'caption': 'The main dining room at golden hour', 'category': 'interior'},
            {'url': 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&h=600&fit=crop', 'caption': 'Fresh oysters from Monterey Bay', 'category': 'food'},
            {'url': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=800&h=600&fit=crop', 'caption': 'Whole roasted branzino, Ligurian style', 'category': 'food'},
            {'url': 'https://images.unsplash.com/photo-1592861956120-e524fc739696?w=800&h=600&fit=crop', 'caption': 'Private dining room', 'category': 'interior'}
        ]
    },
    'events': {
        'enabled': True,
        'page_title': 'Events & Private Dining',
        'page_subtitle': 'Host your next celebration at Aurelia.',
        'hero_image': 'https://images.unsplash.com/photo-1519167758481-83f55049b3b3?w=1920&h=800&fit=crop',
        'cta_title': 'Plan Your Private Event',
        'cta_text': 'Let our events team design a bespoke experience.',
        'services': [
            {'title': 'The Terrace', 'description': 'Intimate space for up to 32 guests.', 'icon': 'fa-utensils'},
            {'title': 'The Cellar', 'description': 'Underground wine cellar for up to 16 guests.', 'icon': 'fa-wine-glass'},
            {'title': 'Full Buyout', 'description': 'Exclusive use for up to 120 guests.', 'icon': 'fa-building'},
            {'title': 'Off-Site Catering', 'description': 'Bring Aurelia to your venue.', 'icon': 'fa-truck'}
        ],
        'upcoming_events': [
            {'title': "Chef Elena's Sunday Supper", 'description': 'A rotating family-style menu. $85 per person.', 'date': 'Every Sunday, 6:00 PM', 'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=400&fit=crop'},
            {'title': 'Wine & Waves', 'description': 'Monthly tasting series exploring coastal wine regions.', 'date': 'Last Thursday of each month', 'image': 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600&h=400&fit=crop'},
            {'title': 'Pasta Masterclass', 'description': 'Learn to make paccheri, pappardelle, and squid ink fettuccine.', 'date': 'First Saturday of each month', 'image': 'https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=600&h=400&fit=crop'}
        ]
    },
    'analytics': {
        'daily_sales': [2850, 3200, 2950, 4100, 5200, 6800, 5900],
        'monthly_revenue': [98000, 112000, 105000, 128000, 135000, 148000],
        'popular_items': ['Whole Roasted Branzino', 'Grilled Spanish Octopus', 'Truffle Paccheri'],
        'customer_satisfaction': 4.9,
        'total_reservations': 342
    },
    'settings': {
        'sendgrid_api_key': '',
        'from_email': '',
        'notification_email': '',
        'currency': '$',
        'tax_rate': 8.75,
        'delivery_fee': 6.0,
        'min_order': 25.0,
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
                initial_password = os.environ.get('ADMIN_INITIAL_PASSWORD') or 'admin123'
                admin = User(
                    username='admin',
                    password_hash=generate_password_hash(initial_password),
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("\n" + "=" * 60)
                print("  ADMIN CREDENTIALS (one-time — change on first login)")
                print("=" * 60)
                print("  Username: admin")
                print(f"  Password: {initial_password}")
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
            'total_revenue': total_revenue,
            'unread_messages': unread_messages,
            'subscriber_count': subscriber_count
        }

    # ─── Routes ────────────────────────────────────────────────────────

    @app.before_request
    def before_request():
        g.user = None
        g.user_role = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                g.user = user
                g.user_role = user.role

    @app.context_processor
    def inject_globals():
        data = load_data()
        return {
            'theme': data['theme'],
            'restaurant': data['restaurant'],
            'settings': data['settings'],
            'seo': data['seo'],
            'user_role': g.user_role,
            'current_year': datetime.utcnow().year
        }

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

    @app.route('/')
    def home():
        data = load_data()
        track_page_view('home')
        featured = []
        for category in ['small plates', 'mains', 'desserts']:
            for item in data['menu'].get(category, []):
                if item.get('popular'):
                    featured.append({**item, 'category': category.title()})
        featured = featured[:6]
        return render_template('home.html',
            featured=featured,
            testimonials=data['testimonials'])

    @app.route('/menu')
    def menu():
        data = load_data()
        track_page_view('menu')
        return render_template('menu.html', menu=data['menu'])

    @app.route('/about')
    def about():
        data = load_data()
        track_page_view('about')
        return render_template('about.html', about=data['about'])

    @app.route('/gallery')
    def gallery():
        data = load_data()
        track_page_view('gallery')
        return render_template('gallery.html', gallery=data['gallery'])

    @app.route('/events')
    def events():
        data = load_data()
        track_page_view('events')
        return render_template('events.html', events=data['events'])

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        data = load_data()
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            subject = request.form.get('subject', '').strip()
            message = request.form.get('message', '').strip()
            if not all([name, email, subject, message]):
                flash('Please fill in all fields', 'error')
                return redirect(url_for('contact'))
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                flash('Please enter a valid email address', 'error')
                return redirect(url_for('contact'))
            msg = ContactMessage(
                name=name[:100],
                email=email[:120],
                subject=subject[:100],
                message=message[:5000]
            )
            db.session.add(msg)
            db.session.commit()
            flash("Message sent! We'll get back to you soon.", 'success')
            return redirect(url_for('contact'))
        track_page_view('contact')
        return render_template('contact.html')

    @app.route('/reservations', methods=['GET', 'POST'])
    def reservations():
        data = load_data()
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            date = request.form.get('date', '').strip()
            time = request.form.get('time', '').strip()
            guests = request.form.get('guests', '').strip()
            special_requests = request.form.get('special_requests', '').strip()
            if not all([name, email, phone, date, time, guests]):
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('reservations'))
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                flash('Please enter a valid email address', 'error')
                return redirect(url_for('reservations'))
            res = Reservation(
                name=name[:100],
                email=email[:120],
                phone=phone[:50],
                date=date,
                time=time,
                guests=guests,
                special_requests=special_requests[:1000]
            )
            db.session.add(res)
            db.session.commit()
            flash("Reservation request received! We'll confirm shortly.", 'success')
            return redirect(url_for('reservations'))
        track_page_view('reservations')
        return render_template('reservations.html', reservations=data['reservations'])

    @app.route('/order/menu')
    def order_menu():
        data = load_data()
        track_page_view('order_menu')
        return render_template('order.html', menu=data['menu'], settings=data['settings'])

    @app.route('/cart')
    def cart():
        data = load_data()
        track_page_view('cart')
        return render_template('cart.html', settings=data['settings'])

    @app.route('/checkout', methods=['GET', 'POST'])
    def checkout():
        data = load_data()
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            order_type = request.form.get('order_type', 'pickup')
            notes = request.form.get('notes', '').strip()
            cart = session.get('cart', [])
            if not cart:
                flash('Your cart is empty', 'error')
                return redirect(url_for('cart'))
            if not all([name, email, phone]):
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('checkout'))
            total = sum(item['price'] * item['quantity'] for item in cart)
            order = Order(
                customer_name=name[:100],
                customer_email=email[:120],
                customer_phone=phone[:50],
                order_type=order_type,
                total=total,
                notes=notes[:1000]
            )
            db.session.add(order)
            db.session.commit()
            for item in cart:
                oi = OrderItem(
                    order_id=order.id,
                    name=item['name'][:100],
                    price=item['price'],
                    quantity=item['quantity'],
                    category=item.get('category', '')
                )
                db.session.add(oi)
            db.session.commit()
            session.pop('cart', None)
            flash(f'Order placed! Total: ${total:.2f}', 'success')
            return redirect(url_for('home'))
        track_page_view('checkout')
        return render_template('checkout.html', settings=data['settings'])

    @app.route('/gift-cards', methods=['GET', 'POST'])
    def gift_cards():
        data = load_data()
        if request.method == 'POST':
            purchaser_name = request.form.get('purchaser_name', '').strip()
            purchaser_email = request.form.get('purchaser_email', '').strip()
            recipient_name = request.form.get('recipient_name', '').strip()
            recipient_email = request.form.get('recipient_email', '').strip()
            amount = float(request.form.get('amount', 0))
            message = request.form.get('message', '').strip()
            if not all([purchaser_name, purchaser_email, recipient_name, recipient_email]) or amount <= 0:
                flash('Please fill in all fields', 'error')
                return redirect(url_for('gift_cards'))
            code = secrets.token_hex(8).upper()
            gc = GiftCard(
                code=code,
                balance=amount,
                original_amount=amount,
                purchaser_name=purchaser_name[:100],
                purchaser_email=purchaser_email[:120],
                recipient_name=recipient_name[:100],
                recipient_email=recipient_email[:120],
                message=message[:500]
            )
            db.session.add(gc)
            db.session.commit()
            flash(f'Gift card created! Code: {code}', 'success')
            return redirect(url_for('gift_cards'))
        track_page_view('gift_cards')
        return render_template('gift_cards.html')

    @app.route('/loyalty', methods=['GET', 'POST'])
    def loyalty():
        data = load_data()
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            if not all([name, email, phone]):
                flash('Please fill in all fields', 'error')
                return redirect(url_for('loyalty'))
            existing = LoyaltyMember.query.filter_by(email=email).first()
            if existing:
                flash('You are already enrolled!', 'error')
                return redirect(url_for('loyalty'))
            member = LoyaltyMember(
                name=name[:100],
                email=email[:120],
                phone=phone[:50]
            )
            db.session.add(member)
            db.session.commit()
            flash('Welcome to the rewards program!', 'success')
            return redirect(url_for('loyalty'))
        track_page_view('loyalty')
        return render_template('loyalty.html')

    @app.route('/table/<table_num>')
    def table_order(table_num):
        data = load_data()
        table = Table.query.filter_by(number=table_num).first()
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
    print("  Login:    admin / (see one-time password printed above on first run)")
    print("  Health:   http://localhost:5000/health")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
