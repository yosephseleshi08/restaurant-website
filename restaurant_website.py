from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import os
import csv
import io
import secrets
import re
import sys

app = Flask(__name__)

# ─── Security Configuration ──────────────────────────────────────────
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# Disable CSRF for simplicity
app.config['WTF_CSRF_ENABLED'] = False
app.config['WTF_CSRF_TIME_LIMIT'] = None

# ─── Database ─────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///restaurant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db = SQLAlchemy(app)

# ─── Rate Limiting ────────────────────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# ─── Data File ──────────────────────────────────────────────────────
DATA_FILE = 'restaurant_data.json'

# ─── Database Models ─────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    guests = db.Column(db.String(10), nullable=False)
    special_requests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ─── Default Data ────────────────────────────────────────────────────
DEFAULT_DATA = {
    'theme': {
        'primary_color': '#E85D3A',
        'secondary_color': '#F4A261',
        'background_color': '#FFF8F0',
        'text_color': '#2D1B12',
        'card_bg': '#FFFFFF',
        'accent_color': '#2A9D8F',
        'font_family': "'Inter', sans-serif"
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
            {'name': 'Calamari Fritti', 'description': 'Tender calamari lightly fried and served with lemon aioli', 'price': 14.99, 'popular': False, 'image': 'https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6?w=500&h=350&fit=crop', 'dietary': []},
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
        'hero_image': 'https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=1920&h=800&fit=crop',
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
    }
}


# ─── Helpers ─────────────────────────────────────────────────────────
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
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            current = json.load(f)
        return deep_merge(DEFAULT_DATA, current)
    return DEFAULT_DATA.copy()


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def init_db():
    """Initialize database - creates tables and admin user"""
    db.create_all()
    if User.query.count() == 0:
        # Use fixed password for simplicity
        admin = User(username='admin', password_hash=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()
        print("\n" + "=" * 60)
        print("  ADMIN CREDENTIALS")
        print("=" * 60)
        print("  Username: admin")
        print("  Password: admin123")
        print("=" * 60 + "\n")


data = load_data()


def get_featured_items():
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


from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ========================================
# PUBLIC ROUTES
# ========================================

@app.route('/')
def home():
    return render_template('home.html',
        theme=data['theme'], restaurant=data['restaurant'],
        menu=data['menu'], testimonials=data['testimonials'],
        online_ordering=data['online_ordering'], featured=get_featured_items())

@app.route('/menu')
def menu_page():
    return render_template('menu.html',
        theme=data['theme'], restaurant=data['restaurant'], menu=data['menu'])

@app.route('/about')
def about():
    return render_template('about.html',
        theme=data['theme'], restaurant=data['restaurant'], about=data['about'])

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    success = False
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        if name and email and subject and message:
            msg = ContactMessage(name=name, email=email, subject=subject, message=message)
            db.session.add(msg)
            db.session.commit()
            success = True
    return render_template('contact.html',
        theme=data['theme'], restaurant=data['restaurant'], success=success)

@app.route('/reservations', methods=['GET', 'POST'])
def reservations():
    success = False
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        date = request.form.get('date')
        time = request.form.get('time')
        guests = request.form.get('guests')
        special = request.form.get('special_requests', '').strip()
        if name and email and phone and date and time and guests:
            res = Reservation(name=name, email=email, phone=phone,
                date=date, time=time, guests=guests, special_requests=special)
            db.session.add(res)
            db.session.commit()
            success = True
    return render_template('reservations.html',
        theme=data['theme'], restaurant=data['restaurant'],
        reservations=data['reservations'], success=success)

@app.route('/order')
def order_online():
    return render_template('order.html',
        theme=data['theme'], restaurant=data['restaurant'],
        online_ordering=data['online_ordering'])

@app.route('/gallery')
def gallery():
    return render_template('gallery.html',
        theme=data['theme'], restaurant=data['restaurant'], gallery=data['gallery'])

@app.route('/events')
def events():
    return render_template('events.html',
        theme=data['theme'], restaurant=data['restaurant'], events=data['events'])


# ========================================
# AUTH ROUTES
# ========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', theme=data['theme'], restaurant=data['restaurant'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ========================================
# ADMIN ROUTES
# ========================================

@app.route('/dashboard')
@admin_required
def dashboard():
    try:
        rows = Reservation.query.order_by(Reservation.created_at.desc()).limit(10).all()
        reservations = [{'name': r.name, 'date': r.date, 'time': r.time,
            'guests': r.guests, 'phone': r.phone} for r in rows]
    except:
        reservations = []
    
    analytics = data['analytics'].copy()
    analytics['total_reservations'] = Reservation.query.count()
    
    return render_template('dashboard.html',
        theme=data['theme'], restaurant=data['restaurant'],
        analytics=analytics, reservations=reservations)

@app.context_processor
def inject_globals():
    return {
        'restaurant': data['restaurant'],
        'theme': data['theme'],
        'current_year': datetime.now().year,
        'csrf_token': lambda: ''  # Empty CSRF token
    }

@app.route('/editor')
@admin_required
def editor():
    return render_template('editor.html',
        theme=data['theme'], restaurant=data['restaurant'],
        about=data['about'], menu=data['menu'], testimonials=data['testimonials'],
        online_ordering=data['online_ordering'], gallery=data['gallery'],
        events=data['events'], analytics=data['analytics'])

@app.route('/create_admin')
def create_admin():
    """Create admin user if not exists"""
    if User.query.count() == 0:
        admin = User(username='admin', password_hash=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()
        return "✅ Admin created! Username: admin, Password: admin123"
    return "✅ Admin already exists!"


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
            user.password_hash = generate_password_hash(new_pass)
            db.session.commit()
            flash('Password changed successfully! Please log in again.', 'success')
            session.clear()
            return redirect(url_for('login'))
    return render_template('change_password.html', theme=data['theme'], restaurant=data['restaurant'])

# ========================================
# API ROUTES
# ========================================

@app.route('/api/update_theme', methods=['POST'])
@admin_required
def update_theme():
    data['theme'].update(request.json)
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/update_restaurant', methods=['POST'])
@admin_required
def update_restaurant():
    data['restaurant'].update(request.json)
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/update_hours', methods=['POST'])
@admin_required
def update_hours():
    data['restaurant']['hours'] = request.json
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/export/reservations')
@admin_required
def export_reservations():
    try:
        rows = Reservation.query.order_by(Reservation.created_at.desc()).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Date', 'Time', 'Guests', 'Special Requests', 'Created At'])
        
        # Write data
        for r in rows:
            writer.writerow([
                r.id,
                r.name,
                r.email,
                r.phone,
                r.date,
                r.time,
                r.guests,
                r.special_requests or '',
                r.created_at.strftime('%Y-%m-%d %H:%M') if r.created_at else ''
            ])
        
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'reservations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    except Exception as e:
        return f"Error exporting: {e}", 500

@app.route('/api/update_social', methods=['POST'])
@admin_required
def update_social():
    data['restaurant']['social'] = request.json
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/update_about', methods=['POST'])
@admin_required
def update_about():
    updates = request.json
    for key, value in updates.items():
        if key in data['about'] and key not in ['values', 'chef_stats']:
            data['about'][key] = value
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/update_testimonials', methods=['POST'])
@admin_required
def update_testimonials():
    data['testimonials'] = request.json.get('testimonials', [])
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/menu/add', methods=['POST'])
@admin_required
def add_menu_item():
    item = request.json
    category = item.get('category')
    if category in data['menu']:
        data['menu'][category].append({
            'name': item['name'],
            'description': item['description'],
            'price': float(item['price']),
            'popular': item.get('popular', False),
            'image': item.get('image', ''),
            'dietary': item.get('dietary', [])
        })
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/menu/delete', methods=['POST'])
@admin_required
def delete_menu_item():
    category = request.json.get('category')
    index = int(request.json.get('index', -1))
    if category in data['menu'] and 0 <= index < len(data['menu'][category]):
        data['menu'][category].pop(index)
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/menu/update', methods=['POST'])
@admin_required
def update_menu_item():
    item = request.json
    category = item.get('category')
    index = int(item.get('index', -1))
    if category in data['menu'] and 0 <= index < len(data['menu'][category]):
        data['menu'][category][index] = {
            'name': item.get('name'),
            'description': item.get('description'),
            'price': float(item.get('price', 0)),
            'popular': item.get('popular', False),
            'image': item.get('image', ''),
            'dietary': item.get('dietary', [])
        }
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/update_sales', methods=['POST'])
@admin_required
def update_sales():
    sales = request.json.get('sales', [])
    if len(sales) == 7:
        data['analytics']['daily_sales'] = sales
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/update_revenue', methods=['POST'])
@admin_required
def update_revenue():
    revenue = request.json.get('revenue', [])
    if len(revenue) == 6:
        data['analytics']['monthly_revenue'] = revenue
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/reset_data', methods=['POST'])
@admin_required
def reset_data():
    global data
    data = DEFAULT_DATA.copy()
    save_data(data)
    return jsonify({'success': True})


# ========================================
# MAIN - THIS IS THE FIX!
# ========================================

# ========================================
# INITIALIZE DATABASE ON STARTUP (REQUIRED FOR RENDER/GUNICORN)
# ========================================
with app.app_context():
    init_db()  # Creates tables and admin user even when not run as __main__

# ========================================
# MAIN
# ========================================

if __name__ == '__main__':
    print("=" * 60)
    print("  RESTAURANT WEBSITE — PERFECT EDITION")
    print("=" * 60)
    print("  Login:    admin / admin123")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
