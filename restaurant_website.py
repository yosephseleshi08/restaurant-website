from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json
import os
import csv
import io
import secrets
import requests
import atexit
import re
import shutil
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# ─── Security Configuration ──────────────────────────────────────────
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    secret_file = os.path.join(app.root_path, '.secret_key')
    if os.path.exists(secret_file):
        with open(secret_file, 'r') as f:
            app.config['SECRET_KEY'] = f.read().strip()
    else:
        app.config['SECRET_KEY'] = secrets.token_hex(32)
        with open(secret_file, 'w') as f:
            f.write(app.config['SECRET_KEY'])
        os.chmod(secret_file, 0o600)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600

# ─── Database: PostgreSQL or SQLite ─────────────────────────────────
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

# ─── Cloudinary Configuration ────────────────────────────────────────
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)
CLOUDINARY_ENABLED = all([
    os.environ.get('CLOUDINARY_CLOUD_NAME'),
    os.environ.get('CLOUDINARY_API_KEY'),
    os.environ.get('CLOUDINARY_API_SECRET')
])

# ─── Local Upload Fallback ─────────────────────────────────────────
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ─── Security Extensions ─────────────────────────────────────────────
csrf = CSRFProtect(app)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

if os.environ.get('FLASK_ENV') == 'production':
    Talisman(app, force_https=True, content_security_policy={
        'default-src': "'self'",
        'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdnjs.cloudflare.com"],
        'font-src': ["'self'", "https://fonts.gstatic.com"],
        'script-src': ["'self'", "https://cdn.jsdelivr.net"],
        'img-src': ["'self'", "data:", "https:", "blob:"]
    })

# ─── Data File & Backup Paths ────────────────────────────────────────
DATA_FILE = 'restaurant_data.json'
BACKUP_DIR = os.path.join(app.root_path, 'backups')
os.makedirs(BACKUP_DIR, exist_ok=True)


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

class Setting(db.Model):
    __tablename__ = 'settings'
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text)

# ─── Default Data ────────────────────────────────────────────────────
DEFAULT_DATA = {
    'theme': {
        'primary_color': '#E85D3A', 'secondary_color': '#F4A261',
        'background_color': '#FFF8F0', 'text_color': '#2D1B12',
        'card_bg': '#FFFFFF', 'accent_color': '#2A9D8F',
        'font_family': "'Inter', sans-serif"
    },
    'restaurant': {
        'name': "La Bella Cucina",
        'tagline': "Authentic Italian Dining Experience",
        'address': "123 Main Street, Foodville, FD 12345",
        'phone': "(555) 123-4567", 'phone_link': "+15551234567",
        'email': "info@labellacucina.com",
        'hours': {
            'monday': '11:00 AM - 10:00 PM', 'tuesday': '11:00 AM - 10:00 PM',
            'wednesday': '11:00 AM - 10:00 PM', 'thursday': '11:00 AM - 10:00 PM',
            'friday': '11:00 AM - 11:00 PM', 'saturday': '10:00 AM - 11:00 PM',
            'sunday': '10:00 AM - 9:00 PM'
        },
        'social': {
            'instagram': 'labellacucina', 'facebook': 'LaBellaCucina',
            'twitter': 'LaBellaCucina', 'yelp': 'la-bella-cucina-foodville'
        },
        'google_maps_embed': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3022.1!2d-74.006!3d40.7128!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zNDDCsDQyJzQ2LjEiTiA3NMKwMDAnMjEuNiJX!5e0!3m2!1sen!2sus!4v1'
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


def get_setting(key, default=''):
    s = Setting.query.get(key)
    return s.value if s else default


def set_setting(key, value):
    s = Setting.query.get(key)
    if s:
        s.value = value
    else:
        s = Setting(key=key, value=value)
        db.session.add(s)
    db.session.commit()


def init_db():
    db.create_all()
    if User.query.count() == 0:
        temp_password = secrets.token_urlsafe(14)
        admin = User(username='admin', password_hash=generate_password_hash(temp_password))
        db.session.add(admin)
        defaults = [
            ('notification_email', 'owner@restaurant.com'),
            ('sendgrid_api_key', ''),
            ('from_email', 'noreply@yourplatform.com')
        ]
        for key, value in defaults:
            db.session.add(Setting(key=key, value=value))
        db.session.commit()
        print("\n" + "=" * 60)
        print("  FIRST-TIME ADMIN CREDENTIALS")
        print("=" * 60)
        print(f"  Username: admin")
        print(f"  Password: {temp_password}")
        print("=" * 60 + "\n")
        creds_file = os.path.join(app.root_path, '.admin_credentials')
        with open(creds_file, 'w') as f:
            f.write(f"Username: admin\nPassword: {temp_password}\nGenerated: {datetime.now().isoformat()}\n")
        os.chmod(creds_file, 0o600)


def backup_data():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_backup = os.path.join(BACKUP_DIR, f'restaurant_{timestamp}.json')
    try:
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if os.path.exists(db_path):
                db_backup = os.path.join(BACKUP_DIR, f'restaurant_{timestamp}.db')
                shutil.copy2(db_path, db_backup)
        with open(json_backup, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        all_backups = sorted([f for f in os.listdir(BACKUP_DIR)])
        for old in all_backups[:-60]:
            try:
                os.remove(os.path.join(BACKUP_DIR, old))
            except FileNotFoundError:
                pass
        print(f"[BACKUP] Saved at {timestamp}")
    except Exception as e:
        print(f"[BACKUP ERROR] {e}")


scheduler = BackgroundScheduler()
scheduler.add_job(func=backup_data, trigger="cron", hour=3, minute=0)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def send_notification(subject, body):
    try:
        api_key = os.environ.get('SENDGRID_API_KEY') or get_setting('sendgrid_api_key')
        from_email = os.environ.get('FROM_EMAIL') or get_setting('from_email', 'noreply@yourplatform.com')
        to_email = get_setting('notification_email')
        if not to_email:
            return False
        if not api_key:
            print(f"\n{'='*50}\nEMAIL NOTIFICATION (DEV MODE)\nTo: {to_email}\nSubject: {subject}\n{'-'*50}\n{body}\n{'='*50}\n")
            return True
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": from_email},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body}]
            },
            timeout=10
        )
        return response.status_code == 202
    except Exception as e:
        print(f"Email error: {e}")
        return False


def sanitize_input(text, max_length=500):
    if not text:
        return ""
    text = str(text).strip()
    return text[:max_length] if len(text) > max_length else text


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    digits = re.sub(r'\D', '', phone)
    return len(digits) >= 10


def get_reservation_capacity(date, time):
    max_guests = data['reservations'].get('max_guests_per_slot', 30)
    rows = Reservation.query.filter_by(date=date, time=time).all()
    booked = 0
    for row in rows:
        try:
            booked += 8 if row.guests == '8' else int(row.guests)
        except ValueError:
            booked += 2
    return max(0, max_guests - booked)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def upload_image_file(file):
    if CLOUDINARY_ENABLED and file:
        try:
            result = cloudinary.uploader.upload(file, folder="restaurant_uploads")
            return result.get('secure_url')
        except Exception as e:
            print(f"Cloudinary upload failed: {e}. Falling back to local.")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return url_for('static', filename=f'uploads/{filename}')
    return None


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


@app.context_processor
def inject_globals():
    return {
        'restaurant': data['restaurant'],
        'theme': data['theme'],
        'current_year': datetime.now().year
    }


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

@app.route('/reservations', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def reservations():
    success = False
    error_msg = None
    available_slots = data['reservations']['time_slots']
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name'), 100)
        email = sanitize_input(request.form.get('email'), 100)
        phone = sanitize_input(request.form.get('phone'), 50)
        date = request.form.get('date')
        time = request.form.get('time')
        guests = request.form.get('guests')
        special = sanitize_input(request.form.get('special_requests'), 500)
        if not all([name, email, phone, date, time, guests]):
            error_msg = "All required fields must be filled."
        elif not validate_email(email):
            error_msg = "Please enter a valid email address."
        elif not validate_phone(phone):
            error_msg = "Please enter a valid phone number."
        elif time not in available_slots:
            error_msg = "Invalid time slot selected."
        else:
            capacity = get_reservation_capacity(date, time)
            guest_count = 8 if guests == '8' else int(guests)
            if guest_count > capacity:
                error_msg = f"Sorry, only {capacity} seats remaining for {time} on {date}."
            else:
                res = Reservation(name=name, email=email, phone=phone,
                    date=date, time=time, guests=guests, special_requests=special)
                db.session.add(res)
                db.session.commit()
                send_notification(f"New Reservation: {name}",
                    f"Name: {name}\nEmail: {email}\nPhone: {phone}\nDate: {date}\nTime: {time}\nGuests: {guests}\nRequests: {special or 'None'}")
                data['analytics']['total_reservations'] = data['analytics'].get('total_reservations', 0) + 1
                save_data(data)
                success = True
    return render_template('reservations.html',
        theme=data['theme'], restaurant=data['restaurant'],
        reservations=data['reservations'], success=success, error_msg=error_msg)

@app.route('/contact', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def contact():
    success = False
    error_msg = None
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name'), 100)
        email = sanitize_input(request.form.get('email'), 100)
        subject = sanitize_input(request.form.get('subject'), 100)
        message = sanitize_input(request.form.get('message'), 2000)
        if not all([name, email, subject, message]):
            error_msg = "All fields are required."
        elif not validate_email(email):
            error_msg = "Please enter a valid email address."
        else:
            msg = ContactMessage(name=name, email=email, subject=subject, message=message)
            db.session.add(msg)
            db.session.commit()
            send_notification(f"New Contact Message: {subject}", f"From: {name} ({email})\n\n{message}")
            success = True
    return render_template('contact.html',
        theme=data['theme'], restaurant=data['restaurant'], success=success, error_msg=error_msg)

@app.route('/about')
def about():
    return render_template('about.html',
        theme=data['theme'], restaurant=data['restaurant'], about=data['about'])

@app.route('/order')
def order_online():
    return render_template('order.html',
        theme=data['theme'], restaurant=data['restaurant'], online_ordering=data['online_ordering'])

@app.route('/gallery')
def gallery():
    return render_template('gallery.html',
        theme=data['theme'], restaurant=data['restaurant'], gallery=data['gallery'])

@app.route('/events')
def events():
    return render_template('events.html',
        theme=data['theme'], restaurant=data['restaurant'], events=data['events'])


# ========================================
# AUTH & ADMIN ROUTES
# ========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Simple hardcoded login for testing
        if username == 'admin' and password == 'admin123':
            session['user_id'] = 1
            session['username'] = 'admin'
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'error')
    return render_template('login.html', theme=data['theme'], restaurant=data['restaurant'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/debug_users')
def debug_users():
    from restaurant_website import User
    users = User.query.all()
    result = []
    for u in users:
        result.append(f"ID: {u.id}, Username: {u.username}")
    return "<br>".join(result) if result else "No users found!"

@app.route('/dashboard')
@admin_required
def dashboard():
    rows = Reservation.query.order_by(Reservation.created_at.desc()).limit(10).all()
    total_reservations = Reservation.query.count()
    total_messages = ContactMessage.query.count()
    analytics = data['analytics'].copy()
    analytics['total_reservations'] = total_reservations
    analytics['total_messages'] = total_messages
    return render_template('dashboard.html',
        theme=data['theme'], restaurant=data['restaurant'],
        analytics=analytics,
        reservations=[{'name': r.name, 'date': r.date, 'time': r.time,
            'guests': r.guests, 'phone': r.phone} for r in rows])

@app.route('/editor')
@admin_required
def editor():
    return render_template('editor.html',
        theme=data['theme'], restaurant=data['restaurant'],
        about=data['about'], menu=data['menu'], testimonials=data['testimonials'],
        online_ordering=data['online_ordering'], gallery=data['gallery'],
        events=data['events'], analytics=data['analytics'])

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    if request.method == 'POST':
        set_setting('notification_email', request.form.get('notification_email', '').strip())
        set_setting('sendgrid_api_key', request.form.get('sendgrid_api_key', '').strip())
        set_setting('from_email', request.form.get('from_email', 'noreply@yourplatform.com').strip())
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        if new_password:
            if len(new_password) < 8:
                flash('Password must be at least 8 characters', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match', 'error')
            else:
                user = User.query.get(session['user_id'])
                if not check_password_hash(user.password_hash, current_password):
                    flash('Current password is incorrect', 'error')
                else:
                    user.password_hash = generate_password_hash(new_password)
                    db.session.commit()
                    flash('Password updated successfully', 'success')
        return redirect(url_for('admin_settings'))
    settings = {
        'notification_email': get_setting('notification_email'),
        'sendgrid_api_key': get_setting('sendgrid_api_key'),
        'from_email': get_setting('from_email', 'noreply@yourplatform.com')
    }
    return render_template('admin_settings.html',
        theme=data['theme'], restaurant=data['restaurant'], settings=settings)

@app.route('/admin/test-email', methods=['POST'])
@admin_required
def test_email():
    success = send_notification(
        "Test Email from Restaurant Website",
        "This is a test notification. If you're reading this, your email configuration is working!"
    )
    flash('Test email sent!' if success else 'Failed to send test email.', 'success' if success else 'error')
    return redirect(url_for('admin_settings'))

@app.route('/api/upload_image', methods=['POST'])
@admin_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    url = upload_image_file(file)
    if url:
        return jsonify({'success': True, 'url': url})
    return jsonify({'success': False, 'error': 'Upload failed'})

@app.route('/api/export/reservations')
@admin_required
def export_reservations():
    rows = Reservation.query.order_by(Reservation.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Date', 'Time', 'Guests', 'Special Requests', 'Created At'])
    for r in rows:
        writer.writerow([r.id, r.name, r.email, r.phone, r.date, r.time, r.guests, r.special_requests, r.created_at])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'reservations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/api/export/messages')
@admin_required
def export_messages():
    rows = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Subject', 'Message', 'Created At'])
    for r in rows:
        writer.writerow([r.id, r.name, r.email, r.subject, r.message, r.created_at])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'messages_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


# ========================================
# API ROUTES (PROTECTED)
# ========================================

@app.route('/api/update_theme', methods=['POST'])
@admin_required
def update_theme():
    theme_updates = request.json
    for key, value in theme_updates.items():
        if key in data['theme']:
            data['theme'][key] = value
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/update_restaurant', methods=['POST'])
@admin_required
def update_restaurant():
    updates = request.json
    for key, value in updates.items():
        if key in data['restaurant']:
            data['restaurant'][key] = value
    save_data(data)
    return jsonify({'success': True})

@app.route('/create_tables')
def create_tables():
    from restaurant_website import db
    try:
        db.create_all()
        return "✅ Database tables created successfully! <a href='/dashboard'>Go to Dashboard</a>"
    except Exception as e:
        return f"❌ Error: {e}"

@app.route('/api/update_hours', methods=['POST'])
@admin_required
def update_hours():
    data['restaurant']['hours'] = request.json
    save_data(data)
    return jsonify({'success': True})

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

@app.route('/init_db')
def init_db():
    from restaurant_website import db
    db.create_all()
    return "✅ Database tables created successfully! <a href='/'>Go Home</a>"

@app.route('/api/menu/add', methods=['POST'])
@admin_required
def add_menu_item():
    item_data = request.json
    category = item_data.get('category')
    item = {
        'name': sanitize_input(item_data.get('name'), 100),
        'description': sanitize_input(item_data.get('description'), 500),
        'price': float(item_data.get('price', 0)),
        'popular': item_data.get('popular', False),
        'image': sanitize_input(item_data.get('image', ''), 500),
        'dietary': item_data.get('dietary', [])
    }
    if category in data['menu']:
        data['menu'][category].append(item)
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Category not found'})

@app.route('/api/menu/delete', methods=['POST'])
@admin_required
def delete_menu_item():
    item_data = request.json
    category = item_data.get('category')
    index = int(item_data.get('index', -1))
    if category in data['menu'] and 0 <= index < len(data['menu'][category]):
        data['menu'][category].pop(index)
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/menu/update', methods=['POST'])
@admin_required
def update_menu_item():
    item_data = request.json
    category = item_data.get('category')
    index = int(item_data.get('index', -1))
    if category in data['menu'] and 0 <= index < len(data['menu'][category]):
        data['menu'][category][index] = {
            'name': sanitize_input(item_data.get('name'), 100),
            'description': sanitize_input(item_data.get('description'), 500),
            'price': float(item_data.get('price', 0)),
            'popular': item_data.get('popular', False),
            'image': sanitize_input(item_data.get('image', ''), 500),
            'dietary': item_data.get('dietary', [])
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
# ERROR HANDLERS
# ========================================

@app.errorhandler(429)
def ratelimit_handler(e):
    flash('Too many requests. Please slow down.', 'error')
    return redirect(request.url or url_for('home'))

@app.errorhandler(404)
def not_found(e):
    return render_template('home.html',
        theme=data['theme'], restaurant=data['restaurant'],
        menu=data['menu'], testimonials=data['testimonials'],
        online_ordering=data['online_ordering'], featured=get_featured_items()), 404
    
@app.route('/reset_password')
def reset_password():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.password_hash = generate_password_hash('admin123')
        db.session.commit()
        return "✅ Password reset to: <strong>admin123</strong><br><a href='/login'>Go to Login</a>"
    return "❌ Admin user not found!"
# ========================================
# MAIN
# ========================================

# At the bottom of your file, make sure this is there:
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This creates tables if they don't exist
    app.run(debug=False, host='0.0.0.0', port=5000)
    print("=" * 60)
    print("  RESTAURANT WEBSITE — PRODUCTION READY v2")
    print("=" * 60)
    print("  Public Site:  http://127.0.0.1:5000")
    print("  Admin Login:  http://127.0.0.1:5000/login")
    print("  Dashboard:    http://127.0.0.1:5000/dashboard")
    print("  Editor:       http://127.0.0.1:5000/editor")
    print("  Settings:     http://127.0.0.1:5000/admin/settings")
    print("=" * 60)
    print(f"  Database: {app.config['SQLALCHEMY_DATABASE_URI'][:40]}...")
    print(f"  Cloudinary: {'ENABLED' if CLOUDINARY_ENABLED else 'DISABLED (local fallback)'}")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=5000)
