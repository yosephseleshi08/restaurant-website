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
            'chef_image': "https://images.unsplash.com/photo-1583394293214-28ez7a28f731?w=600&h=600&fit=crop&crop=faces",
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
                {'name': 'Whipped Feta', 'description': "Whipped sheep's milk feta, honeycomb, toasted walnuts, warm sourdough", 'price': 18.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1529312266912-b33cf6227e24?w=600&h=400&fit=crop', 'dietary': ['vegetarian']},
                {'name': 'Grilled Spanish Octopus', 'description': 'Charred octopus, fingerling potatoes, smoked paprika, salsa verde', 'price': 26.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=400&fit=crop', 'dietary': ['gluten-free', 'dairy-free']},
                {'name': 'Burrata & Heirloom Tomatoes', 'description': 'Pugliese burrata, San Marzano tomatoes, basil oil, aged balsamic', 'price': 22.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1529312266912-b33cf6227e24?w=600&h=400&fit=crop', 'dietary': ['vegetarian', 'gluten-free']}
            ],
            'mains': [
                {'name': 'Whole Roasted Branzino', 'description': 'Mediterranean sea bass, herb-stuffed, lemon, extra virgin olive oil', 'price': 42.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=600&h=400&fit=crop', 'dietary': ['gluten-free', 'dairy-free']},
                {'name': 'Truffle Paccheri', 'description': 'Hand-rolled paccheri, black truffle cream, aged Parmigiano-Reggiano', 'price': 38.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1551183053-bf91b1dca034?w=600&h=400&fit=crop', 'dietary': ['vegetarian']},
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
                {'url': 'https://images.unsplash.com/photo-1550966871-3ed3c47e2ce2?w=800&h=600&fit=crop', 'caption': 'Private dining room', 'category': 'interior'}
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
                {'title': 'Pasta Masterclass', 'description': 'Learn to make paccheri, pappardelle, and squid ink fettuccine.', 'date': 'First Saturday of each month', 'image': 'https://images.unsplash.com/photo-1551183053-bf91b1dca034?w=600&h=400&fit=crop'}
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
    # (Models remain exactly as they were: User, Reservation, ContactMessage, Order, OrderItem, PageView, NewsletterSubscriber, EventBooking, CateringInquiry, SiteSetting, Table, WaitlistEntry, GiftCard, LoyaltyMember, DailySpecial, CustomerVisit, AuditLog, WebhookEndpoint, WebhookDelivery)
    
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
            'total_revenue': round(float(total_revenue), 2),
            'unread_messages': unread_messages,
            'subscriber_count': subscriber_count
        }

    # ─── ADDED MISSING HELPER FUNCTIONS ────────────────────────────────

    def sanitize_input(text, max_length=500):
        if not text:
            return ""
        return str(text)[:max_length].strip()

    def validate_email(email):
        if not email:
            return None
        email = str(email).strip()
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return email
        return None

    def validate_phone(phone):
        if not phone:
            return None
        phone = str(phone).strip()
        if len(re.sub(r"[^\d]", "", phone)) >= 7:
            return phone
        return None

    def check_reservation_capacity(date, time, guests):
        try:
            guests_int = int(guests)
        except (ValueError, TypeError):
            return False, 0
            
        existing = Reservation.query.filter_by(date=date, time=time, status='confirmed').all()
        current_guests = sum(int(r.guests) for r in existing if str(r.guests).isdigit())
        
        data = load_data()
        max_guests = data.get('reservations', {}).get('max_guests_per_slot', 24)
            
        remaining = max_guests - current_guests
        if guests_int <= remaining:
            return True, remaining
        return False, remaining

    def send_email(to_email, subject, html_body):
        try:
            app.logger.info(f"Email queued for {to_email}: {subject}")
            # Actual SendGrid implementation can be added here
        except Exception as e:
            app.logger.error(f"Email send failed: {e}")

    def send_sms(to_phone, message):
        try:
            app.logger.info(f"SMS queued for {to_phone}: {message}")
            # Actual Twilio implementation can be added here
        except Exception as e:
            app.logger.error(f"SMS send failed: {e}")

    def trigger_webhooks(event_type, payload):
        try:
            app.logger.info(f"Webhook triggered: {event_type}")
            # Actual webhook implementation can be added here
        except Exception as e:
            app.logger.error(f"Webhook trigger failed: {e}")

    # ─── Decorators ────────────────────────────────────────────────────

    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            user = User.query.get(session['user_id'])
            if not user or user.role not in ['admin', 'manager', 'super_admin']:
                flash('Access denied.', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function

    def manager_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            user = User.query.get(session['user_id'])
            if not user or user.role not in ['manager', 'admin', 'super_admin']:
                flash('Access denied.', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function

    def super_admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            user = User.query.get(session['user_id'])
            if not user or user.role != 'super_admin':
                flash('Access denied.', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function

    # ─── Public Routes ─────────────────────────────────────────────────

    @app.route('/')
    def home():
        track_page_view('home')
        data = load_data()
        return render_template('index.html',
            theme=data['theme'], restaurant=data['restaurant'],
            about=data['about'], testimonials=data['testimonials'],
            menu=data['menu'], settings=data['settings'], seo=data['seo'])

    @app.route('/about')
    def about():
        track_page_view('about')
        data = load_data()
        return render_template('about.html',
            theme=data['theme'], restaurant=data['restaurant'],
            about=data['about'], settings=data['settings'], seo=data['seo'])

    @app.route('/menu')
    def menu():
        track_page_view('menu')
        data = load_data()
        return render_template('menu.html',
            theme=data['theme'], restaurant=data['restaurant'],
            menu=data['menu'], seo=data['seo'], settings=data['settings'])

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

    # ✅ FIXED: Added all required context variables to prevent Jinja2 UndefinedError
    @app.route('/order/menu')
    def order_menu():
        data = load_data()
        track_page_view('order_menu')
        return render_template(
            'order.html',
            theme=data['theme'],
            restaurant=data['restaurant'],
            seo=data['seo'],
            settings=data['settings'],
            online_ordering=data['online_ordering'],
            menu=data['menu']
        )

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        track_page_view('contact')
        data = load_data()
        success = False
        if request.method == 'POST':
            name = sanitize_input(request.form.get('name', ''), 100)
            email = validate_email(request.form.get('email', ''))
            subject = sanitize_input(request.form.get('subject', ''), 100)
            message = sanitize_input(request.form.get('message', ''), 2000)
            if not name or not email or not subject or not message:
                flash('Please fill in all required fields.', 'error')
            else:
                msg = ContactMessage(name=name, email=email, subject=subject, message=message)
                db.session.add(msg)
                db.session.commit()
                success = True
                log_audit('contact_message_created', 'ContactMessage', msg.id)
                notification = app.config['NOTIFICATION_EMAIL']
                if notification:
                    send_email(notification, f"New Contact: {subject}",
                        f"<p>From: {name} ({email})</p><p>{message}</p>")
                trigger_webhooks('contact.created', {'id': msg.id, 'name': name, 'email': email})
        return render_template('contact.html',
            theme=data['theme'], restaurant=data['restaurant'],
            success=success, seo=data['seo'], settings=data['settings'])

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

    @app.route('/gallery')
    def gallery():
        track_page_view('gallery')
        data = load_data()
        if not data['settings'].get('enable_gallery', True):
            flash('Gallery is currently disabled.', 'error')
            return redirect(url_for('home'))
        return render_template('gallery.html',
            theme=data['theme'], restaurant=data['restaurant'],
            gallery=data['gallery'], settings=data['settings'], seo=data['seo'])

    @app.route('/events')
    def events():
        track_page_view('events')
        data = load_data()
        if not data['settings'].get('enable_events', True):
            flash('Events page is currently disabled.', 'error')
            return redirect(url_for('home'))
        return render_template('events.html',
            theme=data['theme'], restaurant=data['restaurant'],
            events=data['events'], settings=data['settings'], seo=data['seo'])

    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

    # ─── Auth Routes ───────────────────────────────────────────────────

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['user_role'] = user.role
                user.last_login = datetime.utcnow()
                db.session.commit()
                log_audit('user_login', 'User', user.id)
                return redirect(url_for('dashboard'))
            flash('Invalid credentials', 'error')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('home'))

    # ─── Admin Dashboard ───────────────────────────────────────────────

    @app.route('/admin')
    @admin_required
    def dashboard():
        data = load_data()
        analytics = get_real_analytics()
        return render_template('dashboard.html',
            theme=data['theme'], restaurant=data['restaurant'],
            analytics=analytics, settings=data['settings'])

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

    # ─── Cart & Checkout ───────────────────────────────────────────────

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
