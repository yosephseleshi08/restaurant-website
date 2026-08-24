"""
La Bella Cucina — Restaurant CMS Pro Edition v2.0
==================================================
Production-Ready Restaurant Management Platform
"""

from flask import (
    Flask, render_template, request, jsonify, redirect, url_for,
    session, flash, send_file, Response, abort
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import json
import os
import csv
import io
import secrets
import re
import requests
import cloudinary
import cloudinary.uploader
import threading
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
            'meta_description': 'Experience authentic Italian cuisine at La Bella Cucina.',
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
            'chef_bio': "With over 20 years of experience in Michelin-starred kitchens.",
            'chef_image': "https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=400&h=400&fit=crop",
            'interior_image': "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&h=600&fit=crop",
            'food_image': "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&h=600&fit=crop",
            'values': [
                {'title': 'Fresh Ingredients', 'description': 'We source locally and import directly from Italy.'},
                {'title': 'Family Recipes', 'description': 'Every sauce is made from scratch.'},
                {'title': 'Warm Hospitality', 'description': 'We treat every guest like family.'}
            ]
        },
        'testimonials': [
            {'name': 'Sarah M.', 'text': 'The best carbonara I have had outside of Rome!', 'rating': 5},
            {'name': 'James & Linda K.', 'text': 'We celebrated our anniversary here.', 'rating': 5},
            {'name': 'David R.', 'text': 'Authentic flavors, generous portions.', 'rating': 5},
            {'name': 'Maria G.', 'text': 'As an Italian expat, I can confirm this is the real deal.', 'rating': 5}
        ],
        'menu': {
            'appetizers': [
                {'name': 'Bruschetta al Pomodoro', 'description': 'Grilled sourdough with tomatoes, basil, garlic', 'price': 12.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1572695157369-7b5e6e5a04c5?w=500&h=350&fit=crop', 'dietary': ['vegetarian']},
                {'name': 'Calamari Fritti', 'description': 'Tender calamari fried and served with lemon aioli', 'price': 14.99, 'popular': False, 'image': 'https://images.unsplash.com/photo-1599084993091-41d2bd2722cc6?w=500&h=350&fit=crop', 'dietary': []},
                {'name': 'Burrata e Prosciutto', 'description': 'Creamy burrata with aged prosciutto and arugula', 'price': 16.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1529312266912-b33cf6227e24?w=500&h=350&fit=crop', 'dietary': []}
            ],
            'mains': [
                {'name': 'Spaghetti alla Carbonara', 'description': 'Classic Roman pasta with guanciale, pecorino, eggs', 'price': 22.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1612874742237-6526221588e3?w=500&h=350&fit=crop', 'dietary': []},
                {'name': 'Chicken Parmigiana', 'description': 'Hand-breaded chicken with marinara and mozzarella', 'price': 24.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1632778149955-e80f8ceca2e8?w=500&h=350&fit=crop', 'dietary': []},
                {'name': 'Margherita Pizza', 'description': 'San Marzano tomato, mozzarella, basil on wood-fired crust', 'price': 18.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=500&h=350&fit=crop', 'dietary': ['vegetarian']},
                {'name': 'Osso Buco alla Milanese', 'description': 'Braised veal shank with gremolata and saffron risotto', 'price': 34.99, 'popular': False, 'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=500&h=350&fit=crop', 'dietary': ['gluten-free']}
            ],
            'desserts': [
                {'name': 'Tiramisu Classico', 'description': 'Espresso-soaked ladyfingers with mascarpone cream', 'price': 10.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=500&h=350&fit=crop', 'dietary': ['vegetarian']},
                {'name': 'Panna Cotta', 'description': 'Vanilla bean custard with berry compote', 'price': 9.99, 'popular': False, 'image': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=500&h=350&fit=crop', 'dietary': ['vegetarian', 'gluten-free']}
            ],
            'beverages': [
                {'name': 'Espresso Doppio', 'description': 'Double shot of rich Italian espresso', 'price': 4.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500&h=350&fit=crop', 'dietary': ['vegetarian', 'gluten-free']},
                {'name': 'Aperol Spritz', 'description': 'Aperol, prosecco, and soda with orange', 'price': 12.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1560512823-8ea9f5b3028b?w=500&h=350&fit=crop', 'dietary': ['vegetarian', 'gluten-free']},
                {'name': 'Limonata Fresca', 'description': 'House-made lemonade with Sicilian lemons and mint', 'price': 6.99, 'popular': False, 'image': 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=500&h=350&fit=crop', 'dietary': ['vegetarian', 'gluten-free']}
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
            'page_subtitle': 'A glimpse into our kitchen and dining experience.',
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
            'page_subtitle': 'Host your next celebration with us.',
            'hero_image': 'https://images.unsplash.com/photo-1519167758481-83f55049b3b3?w=1920&h=800&fit=crop',
            'cta_title': 'Book Your Private Event',
            'cta_text': 'Contact us to discuss custom menus and special requests.',
            'services': [
                {'title': 'Private Dining Room', 'description': 'Intimate space for up to 24 guests.', 'icon': 'fa-utensils'},
                {'title': 'Full Restaurant Buyout', 'description': 'Host up to 80 guests exclusively.', 'icon': 'fa-building'},
                {'title': 'Catering & Off-Site', 'description': 'Full-service catering for events of any size.', 'icon': 'fa-truck'},
                {'title': 'Wine Pairing Dinners', 'description': 'Curated wine pairing experience.', 'icon': 'fa-wine-glass'}
            ],
            'upcoming_events': [
                {'title': 'Wine & Dine Wednesday', 'description': '3-course prix fixe with sommelier-selected wines.', 'date': 'Every Wednesday', 'image': 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600&h=400&fit=crop'},
                {'title': 'Sunday Family Feast', 'description': 'Family-style menu served at communal tables.', 'date': 'Every Sunday', 'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=400&fit=crop'},
                {'title': 'Pasta Making Class', 'description': 'Learn fresh pasta from Chef Marco.', 'date': 'First Saturday of the month', 'image': 'https://images.unsplash.com/photo-1551183053-bf91b1dca034?w=600&h=400&fit=crop'}
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

    @app.route('/menu')
    def menu_page():
        data = load_data()
        return render_template('menu.html',
            theme=data['theme'],
            restaurant=data['restaurant'],
            menu=data['menu'],
            seo=data['seo'],
            settings=data['settings'])





    # ─── Routes ────────────────────────────────────────────────────────

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

    @app.route('/')
    def home():
        data = load_data()
        return render_template('home.html',
            theme=data['theme'],
            restaurant=data['restaurant'],
            menu=data['menu'],
            testimonials=data['testimonials'],
            seo=data['seo'],
            settings=data['settings'])

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
                return redirect(url_for('dashboard'))
            flash('Invalid username or password', 'error')
        data = load_data()
        return render_template('login.html', theme=data['theme'], restaurant=data['restaurant'])

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        data = load_data()
        return render_template('dashboard.html',
            theme=data['theme'],
            restaurant=data['restaurant'],
            analytics=data['analytics'],
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
