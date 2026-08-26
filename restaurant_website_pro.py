"""
La Bella Cucina — Restaurant CMS Pro Edition v2.0
==================================================
11/10 Production-Ready Restaurant Management Platform
"""

from flask import (
    Flask, render_template, request, jsonify, redirect, url_for, 
    session, flash, send_file, Response, abort, g
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
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

def create_app(config_name="production"):
    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
        api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET', '')
    )

    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///restaurant.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.environ.get('REDIS_URL', 'memory://'),
        strategy="fixed-window"
    )

    db = SQLAlchemy(app)
    DATA_FILE = 'restaurant_data.json'
    _data_lock = threading.Lock()

    DEFAULT_DATA = {
        'theme': {
            'primary_color': '#0B0F19', 'secondary_color': '#C9A96E', 'background_color': '#FAF7F2',
            'text_color': '#1A1A1A', 'card_bg': '#FFFFFF', 'accent_color': '#8B7355',
            'font_family': "'Playfair Display', 'Georgia', serif", 'dark_mode': False, 'custom_css': ''
        },
        'seo': {
            'meta_title': 'Aurelia — Modern Coastal Mediterranean Dining',
            'meta_description': 'Experience award-winning coastal Mediterranean cuisine at Aurelia.',
            'meta_keywords': 'mediterranean restaurant, fine dining, seafood, reservations',
            'og_image': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&h=630&fit=crop',
            'google_analytics_id': '', 'facebook_pixel': ''
        },
        'restaurant': {
            'name': "Aurelia", 'tagline': "Modern Coastal Mediterranean Dining",
            'address': "47 Harbor View Boulevard, Marina District, CA 94123",
            'phone': "(415) 555-0199", 'phone_link': "+14155550199", 'email': "reservations@aurelia.co",
            'hours': {'monday': '5:00 PM - 10:00 PM', 'tuesday': '5:00 PM - 10:00 PM', 'wednesday': '5:00 PM - 10:00 PM',
                      'thursday': '5:00 PM - 10:00 PM', 'friday': '5:00 PM - 11:00 PM', 'saturday': '4:30 PM - 11:00 PM', 'sunday': '4:00 PM - 9:30 PM'},
            'social': {'instagram': 'aurelia.dining', 'facebook': 'AureliaDining', 'twitter': 'AureliaDining', 'yelp': 'aurelia-marina-district'},
            'google_maps_embed': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3022.1!2d-122.4194!3d37.7749!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMzfCsDQ2JzI5LjYiTiAxMjLCsDI1JzEwLjAiVw!5e0!3m2!1sen!2us!4v1'
        },
        'about': {
            'story': "Founded in 2019 by Chef Elena Marchetti, Aurelia was born from a simple belief: the Mediterranean diet is not just healthy — it is the purest expression of joy on a plate.",
            'chef_name': "Chef Elena Marchetti",
            'chef_bio': "A James Beard Award semifinalist, Chef Elena trained at El Celler de Can Roca. Her philosophy is simple: let the ingredient speak.",
            'chef_image': "https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=600&h=600&fit=crop&crop=faces",
            'interior_image': "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1600&h=900&fit=crop",
            'food_image': "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1600&h=900&fit=crop",
            'values': [
                {'title': 'Ocean to Table', 'description': 'We source seafood daily from Monterey Bay.'},
                {'title': 'Zero Waste Kitchen', 'description': 'Every herb stem becomes a sauce. Sustainability is our foundation.'},
                {'title': 'Wine as Philosophy', 'description': 'Our sommelier curates 200+ labels from coastal vineyards.'}
            ]
        },
        'testimonials': [
            {'name': 'Marcus T.', 'text': 'The grilled octopus transported me straight to a taverna in Santorini. Simply extraordinary.', 'rating': 5},
            {'name': 'Priya & James K.', 'text': 'We hosted our rehearsal dinner here — every detail was perfection.', 'rating': 5},
            {'name': 'David R., SF Chronicle', 'text': 'Aurelia is doing what few restaurants dare: making fine dining feel like coming home.', 'rating': 5},
            {'name': 'Isabella M.', 'text': 'The olive oil cake alone is worth the flight to San Francisco. A revelation.', 'rating': 5}
        ],
        'menu': {
            'raw bar': [
                {'name': 'Oysters on the Half Shell', 'description': 'Kumamoto & Miyagi selection, mignonette granita, lemon verbena', 'price': 24.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600&h=400&fit=crop', 'dietary': ['gluten-free']},
                {'name': 'Tuna Crudo', 'description': 'Bigeye tuna, Sicilian olive oil, Calabrian chili, preserved lemon', 'price': 28.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1534604973900-c43ab4c2e0ab?w=600&h=400&fit=crop', 'dietary': ['gluten-free', 'dairy-free']}
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
                {'name': 'Dry-Aged Ribeye', 'description': '45-day dry-aged ribeye, bone marrow butter, charred spring onion', 'price': 65.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1600891964092-4316c288032e?w=600&h=400&fit=crop', 'dietary': ['gluten-free']}
            ],
            'desserts': [
                {'name': 'Olive Oil Cake', 'description': 'Citrus-scented olive oil sponge, blood orange curd, mascarpone chantilly', 'price': 14.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=600&h=400&fit=crop', 'dietary': ['vegetarian']},
                {'name': 'Dark Chocolate Fondant', 'description': 'Valrhona dark chocolate, sea salt caramel core, vanilla bean ice cream', 'price': 16.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1624353365286-3f8d62daad51?w=600&h=400&fit=crop', 'dietary': ['vegetarian']}
            ]
        },
        'reservations': {
            'hold_time': '15 minutes', 'large_party_note': 'Parties of 8+ please contact our events team directly',
            'time_slots': ['17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30'],
            'max_guests_per_slot': 24
        },
        'online_ordering': {
            'enabled': True, 'page_title': 'Order Online', 'page_subtitle': "Enjoy Aurelia's coastal Mediterranean cuisine at home.",
            'platforms': [
                {'name': 'DoorDash', 'url': 'https://doordash.com', 'icon': 'fa-motorcycle', 'active': True, 'color': '#FF3008'},
                {'name': 'UberEats', 'url': 'https://ubereats.com', 'icon': 'fa-utensils', 'active': True, 'color': '#06C167'}
            ]
        },
        'gallery': {
            'enabled': True, 'page_title': 'Gallery', 'page_subtitle': 'A glimpse into our kitchen, our craft, and the warm, sun-drenched atmosphere.',
            'photos': [
                {'url': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&h=600&fit=crop', 'caption': 'The main dining room at golden hour', 'category': 'interior'},
                {'url': 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&h=600&fit=crop', 'caption': 'Fresh oysters from Monterey Bay', 'category': 'food'},
                {'url': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=800&h=600&fit=crop', 'caption': 'Whole roasted branzino, Ligurian style', 'category': 'food'},
                {'url': 'https://images.unsplash.com/photo-1592861956120-e524fc739696?w=800&h=600&fit=crop', 'caption': 'Private dining room', 'category': 'interior'}
            ]
        },
        'events': {
            'enabled': True, 'page_title': 'Events & Private Dining', 'page_subtitle': 'Host your next celebration at Aurelia.',
            'hero_image': 'https://images.unsplash.com/photo-1519167758481-83f55049b3b3?w=1920&h=800&fit=crop',
            'cta_title': 'Plan Your Private Event', 'cta_text': 'Let our events team design a bespoke experience.',
            'services': [
                {'title': 'The Terrace', 'description': 'Intimate space for up to 32 guests.', 'icon': 'fa-utensils'},
                {'title': 'The Cellar', 'description': 'Underground wine cellar for up to 16 guests.', 'icon': 'fa-wine-glass'}
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
            'customer_satisfaction': 4.9, 'total_reservations': 342
        },
        'settings': {
            'currency': '$', 'tax_rate': 8.75, 'delivery_fee': 6.0, 'min_order': 25.0,
            'cookie_consent': True, 'enable_online_ordering': True, 'enable_reservations': True,
            'enable_events': True, 'enable_gallery': True, 'enable_loyalty': True,
            'enable_gift_cards': True, 'enable_waitlist': True, 'enable_table_management': True,
            'enable_kitchen_display': True
        }
    }

    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(255), nullable=False)
        role = db.Column(db.String(20), default='admin', index=True)

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
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

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
                admin = User(username='admin', password_hash=generate_password_hash(initial_password), role='admin')
                db.session.add(admin)
                db.session.commit()
                print("\n" + "=" * 60)
                print("  ADMIN CREDENTIALS: admin / " + initial_password)
                print("=" * 60 + "\n")

    def track_page_view(page):
        try:
            pv = PageView(page=page)
            db.session.add(pv)
            db.session.commit()
        except Exception:
            db.session.rollback()

    def get_featured_items(data):
        featured = []
        for category in ['small plates', 'mains', 'desserts']:
            for item in data['menu'].get(category, []):
                if item.get('popular'):
                    featured.append({**item, 'category': category.title()})
        return featured[:6]

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
            'theme': data['theme'], 'restaurant': data['restaurant'],
            'settings': data['settings'], 'seo': data['seo'],
            'user_role': g.user_role, 'current_year': datetime.utcnow().year
        }

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

    @app.route('/')
    def home():
        track_page_view('home')
        data = load_data()
        return render_template('home.html',
            theme=data['theme'], restaurant=data['restaurant'],
            menu=data['menu'], testimonials=data['testimonials'],
            online_ordering=data['online_ordering'], featured=get_featured_items(data),
            seo=data['seo'], settings=data['settings'])

    @app.route('/menu')
    def menu_page():
        track_page_view('menu')
        data = load_data()
        return render_template('menu.html', theme=data['theme'], restaurant=data['restaurant'], menu=data['menu'], seo=data['seo'], settings=data['settings'])

    @app.route('/about')
    def about():
        track_page_view('about')
        data = load_data()
        return render_template('about.html', theme=data['theme'], restaurant=data['restaurant'], about=data['about'], seo=data['seo'], settings=data['settings'])

    @app.route('/gallery')
    def gallery():
        track_page_view('gallery')
        data = load_data()
        return render_template('gallery.html', theme=data['theme'], restaurant=data['restaurant'], gallery=data['gallery'], seo=data['seo'], settings=data['settings'])

    @app.route('/events')
    def events():
        track_page_view('events')
        data = load_data()
        return render_template('events.html', theme=data['theme'], restaurant=data['restaurant'], events=data['events'], seo=data['seo'], settings=data['settings'])

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
            msg = ContactMessage(name=name[:100], email=email[:120], subject=subject[:100], message=message[:5000])
            db.session.add(msg)
            db.session.commit()
            flash("Message sent! We'll get back to you soon.", 'success')
            return redirect(url_for('contact'))
        track_page_view('contact')
        return render_template('contact.html', theme=data['theme'], restaurant=data['restaurant'], seo=data['seo'], settings=data['settings'])

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
            res = Reservation(name=name[:100], email=email[:120], phone=phone[:50], date=date, time=time, guests=guests, special_requests=special_requests[:1000])
            db.session.add(res)
            db.session.commit()
            flash("Reservation request received! We'll confirm shortly.", 'success')
            return redirect(url_for('reservations'))
        track_page_view('reservations')
        return render_template('reservations.html', theme=data['theme'], restaurant=data['restaurant'], reservations=data['reservations'], seo=data['seo'], settings=data['settings'])

    @app.route('/order/menu')
    def order_menu():
        data = load_data()
        track_page_view('order_menu')
        return render_template('order.html', theme=data['theme'], restaurant=data['restaurant'], menu=data['menu'], settings=data['settings'], seo=data['seo'])

    @app.route('/cart')
    def cart():
        data = load_data()
        track_page_view('cart')
        return render_template('cart.html', theme=data['theme'], restaurant=data['restaurant'], settings=data['settings'], seo=data['seo'])

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
            total = sum(item['price'] * item['quantity'] for item in cart)
            order = Order(customer_name=name[:100], customer_email=email[:120], customer_phone=phone[:50], order_type=order_type, total=total, notes=notes[:1000])
            db.session.add(order)
            db.session.commit()
            for item in cart:
                oi = OrderItem(order_id=order.id, name=item['name'][:100], price=item['price'], quantity=item['quantity'], category=item.get('category', ''))
                db.session.add(oi)
            db.session.commit()
            session.pop('cart', None)
            flash(f'Order placed! Total: ${total:.2f}', 'success')
            return redirect(url_for('home'))
        track_page_view('checkout')
        return render_template('checkout.html', theme=data['theme'], restaurant=data['restaurant'], settings=data['settings'], seo=data['seo'])

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                return redirect(url_for('dashboard'))
            flash('Invalid username or password', 'error')
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        data = load_data()
        return render_template('dashboard.html', theme=data['theme'], restaurant=data['restaurant'], analytics=data['analytics'], settings=data['settings'])

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('home'))

    with app.app_context():
        init_db()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
