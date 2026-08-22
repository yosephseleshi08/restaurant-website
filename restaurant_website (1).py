from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
import json
import os
import csv
import io
import secrets
import sqlite3
import smtplib
import ssl
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATA_FILE = 'restaurant_data.json'
DB_FILE = 'restaurant.db'

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
        'name': 'La Bella Cucina',
        'tagline': 'Authentic Italian Dining Experience',
        'address': '123 Main Street, Foodville, FD 12345',
        'phone': '(555) 123-4567',
        'phone_link': '+15551234567',
        'email': 'info@labellacucina.com',
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
        'google_maps_embed': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3022.1!2d-74.006!3d40.7128!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zNDDCsDQyJzQ2LjEiTiA3NMKwMDAnMjEuNiJX!5e0!3m2!1sen!2sus!4v1'
    },
    'home': {
        'hero_image': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1920&h=1080&fit=crop',
        'hero_subtitle': 'Est. 2010 — Foodville, FD',
        'hero_badge_1': '4.8 Rating',
        'hero_badge_2': 'Best of Foodville 2024',
        'hero_badge_3': 'Fresh Daily',
        'featured_title': "Chef's Selections",
        'featured_subtitle': 'Hand-picked favorites from our kitchen, crafted with imported Italian ingredients',
        'featured_items': ['Spaghetti Carbonara', 'Margherita Pizza', 'Burrata e Prosciutto'],
        'cta_title': 'Ready to Experience Authentic Italy?',
        'cta_text': 'Reserve your table today and let us take care of the rest. Walk-ins welcome, but reservations recommended for dinner.',
        'show_order_online': True,
        'order_online_title': 'Order Online',
        'order_online_text': 'Enjoy our authentic Italian cuisine from the comfort of your home. Available for pickup and delivery.'
    },
    'about': {
        'hero_image': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&h=600&fit=crop',
        'subtitle': 'Since 2010',
        'heading': 'A Taste of Tuscany in Every Bite',
        'story': 'Founded in 2010 by Chef Marco Rossi, La Bella Cucina brings the heart of Tuscany to your table. Every dish is crafted with imported Italian ingredients and generations-old family recipes.',
        'extra_paragraph': 'Our wood-fired oven was imported directly from Naples and bakes pizzas at 900°F for that perfect charred crust. Every morning, our kitchen team prepares fresh pasta dough, sauces, and desserts from scratch — just as Nonna taught us.',
        'food_image': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&h=600&fit=crop',
        'values': [
            {'title': 'Fresh Ingredients', 'description': 'We source locally and import directly from Italy every week. Our tomatoes come from San Marzano, our flour from Naples, and our olive oil from a family grove in Tuscany.'},
            {'title': 'Family Recipes', 'description': 'Every sauce and dough is made from scratch using time-honored techniques passed down through three generations of the Rossi family.'},
            {'title': 'Warm Hospitality', 'description': 'We treat every guest like family from the moment you walk through our doors. Your table is waiting.'}
        ],
        'chef_name': 'Chef Marco Rossi',
        'chef_bio': 'With over 20 years of experience in Michelin-starred kitchens across Rome and Florence, Chef Marco brings authentic Italian flavors with a modern twist. He trained under Maestro Gualtiero Marchesi and has been featured in Bon Appétit and Food & Wine.',
        'chef_image': 'https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=400&h=400&fit=crop',
        'chef_stats': [
            {'number': '20+', 'label': 'Years Experience'},
            {'number': '3', 'label': 'Michelin Stars'},
            {'number': '150+', 'label': 'Signature Dishes'}
        ],
        'cta_title': 'Come Dine With Us',
        'cta_text': 'Experience the warmth of Italian hospitality and the flavors of Tuscany. Your table is waiting.'
    },
    'testimonials': [
        {'name': 'Sarah M.', 'text': 'The best carbonara I have had outside of Rome. The ambiance is perfect for date night!', 'rating': 5},
        {'name': 'James & Linda K.', 'text': 'We celebrated our anniversary here and the staff made us feel so special. Highly recommend the tiramisu.', 'rating': 5},
        {'name': 'David R.', 'text': 'Authentic flavors, generous portions, and the wine selection is incredible. Our new favorite spot.', 'rating': 5},
        {'name': 'Maria G.', 'text': 'As an Italian expat, I can confirm this is the real deal. The burrata tastes like it came straight from Puglia.', 'rating': 5}
    ],
    'menu': {
        'appetizers': [
            {'name': 'Bruschetta al Pomodoro', 'description': 'Grilled sourdough topped with fresh tomatoes, basil, garlic, and extra virgin olive oil', 'price': 12.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1572695157369-7b5e6e5a04c5?w=500&h=350&fit=crop', 'dietary': ['vegetarian']},
            {'name': 'Calamari Fritti', 'description': 'Tender calamari lightly fried and served with lemon aioli and house marinara', 'price': 14.99, 'popular': False, 'image': 'https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6?w=500&h=350&fit=crop', 'dietary': []},
            {'name': 'Burrata e Prosciutto', 'description': 'Creamy burrata cheese with aged prosciutto di Parma, arugula, and balsamic glaze', 'price': 16.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1529312266912-b33cf6227e24?w=500&h=350&fit=crop', 'dietary': []}
        ],
        'mains': [
            {'name': 'Spaghetti alla Carbonara', 'description': 'Classic Roman pasta with guanciale, pecorino romano, farm eggs, and cracked black pepper', 'price': 22.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1612874742237-6526221588e3?w=500&h=350&fit=crop', 'dietary': []},
            {'name': 'Chicken Parmigiana', 'description': 'Hand-breaded chicken breast with San Marzano marinara, fresh mozzarella, and parmesan over spaghetti', 'price': 24.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1632778149955-e80f8ceca2e8?w=500&h=350&fit=crop', 'dietary': []},
            {'name': 'Margherita Pizza', 'description': 'San Marzano tomato sauce, fresh fior di latte mozzarella, basil, and EVOO on wood-fired Neapolitan crust', 'price': 18.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=500&h=350&fit=crop', 'dietary': ['vegetarian']},
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
        'time_slots': ['17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00']
    },
    'contact': {
        'page_title': 'Get in Touch',
        'page_subtitle': 'Have a question, feedback, or want to book a private event? We would love to hear from you.',
        'subjects': [
            {'value': 'general', 'label': 'General Inquiry'},
            {'value': 'reservation', 'label': 'Reservation Question'},
            {'value': 'private-event', 'label': 'Private Event / Catering'},
            {'value': 'feedback', 'label': 'Feedback'},
            {'value': 'other', 'label': 'Other'}
        ],
        'show_map': True
    },
    'footer': {
        'description': 'Authentic Italian dining at La Bella Cucina. Serving fresh, handcrafted dishes with passion since 2010. Every dish tells a story.',
        'show_legal': True
    },
    'online_ordering': {
        'enabled': True,
        'page_title': 'Order Online',
        'page_subtitle': 'Enjoy our authentic Italian cuisine from the comfort of your home. Available for pickup and delivery.',
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
        'cta_text': 'Let us help you plan the perfect occasion. Contact us to discuss custom menus, seating arrangements, and special requests.',
        'services': [
            {'title': 'Private Dining Room', 'description': 'An intimate space for up to 24 guests, perfect for family celebrations, rehearsal dinners, and business meetings. Complete with dedicated service staff.', 'icon': 'fa-utensils'},
            {'title': 'Full Restaurant Buyout', 'description': 'Host up to 80 guests for a truly exclusive experience. Ideal for weddings, corporate events, and milestone celebrations.', 'icon': 'fa-building'},
            {'title': 'Catering & Off-Site', 'description': 'Bring the flavors of La Bella Cucina to your venue. We offer full-service catering with customizable menus for events of any size.', 'icon': 'fa-truck'},
            {'title': 'Wine Pairing Dinners', 'description': 'Elevate your event with a curated wine pairing experience. Our sommelier selects the perfect wines to complement each course.', 'icon': 'fa-wine-glass'}
        ],
        'upcoming_events': [
            {'title': 'Wine & Dine Wednesday', 'description': 'Every Wednesday, enjoy a 3-course prix fixe menu paired with sommelier-selected wines. $65 per person.', 'date': 'Every Wednesday', 'image': 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600&h=400&fit=crop'},
            {'title': 'Sunday Family Feast', 'description': 'A rotating family-style menu featuring classic Italian dishes served at communal tables. Perfect for groups of 4-12.', 'date': 'Every Sunday', 'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=400&fit=crop'},
            {'title': 'Pasta Making Class', 'description': 'Learn the art of fresh pasta from Chef Marco. Includes hands-on instruction, dinner, and a recipe booklet to take home.', 'date': 'First Saturday of the month', 'image': 'https://images.unsplash.com/photo-1551183053-bf91b1dca034?w=600&h=400&fit=crop'}
        ]
    },
    'analytics': {
        'daily_sales': [1250, 1420, 1380, 1680, 2100, 2450, 1800],
        'monthly_revenue': [45000, 52000, 49000, 58000, 62000, 68000],
        'popular_items': ['Spaghetti Carbonara', 'Chicken Parmigiana', 'Margherita Pizza'],
        'customer_satisfaction': 4.8,
        'total_reservations': 156
    },
    'reservation_list': [],
    'contact_messages': []
}


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


# -- DATABASE --
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            guests TEXT NOT NULL,
            special_requests TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    ''')
    cur = conn.execute("SELECT COUNT(*) as count FROM users")
    if cur.fetchone()['count'] == 0:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ('admin', generate_password_hash('admin'))
        )
    defaults = [
        ('smtp_server', 'smtp.gmail.com'),
        ('smtp_port', '587'),
        ('smtp_username', ''),
        ('smtp_password', ''),
        ('smtp_use_tls', 'true'),
        ('notification_email', 'owner@restaurant.com')
    ]
    for key, value in defaults:
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
    conn.commit()
    conn.close()


def get_setting(key, default=''):
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row['value'] if row else default


def set_setting(key, value):
    conn = get_db()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value)
    )
    conn.commit()
    conn.close()


# -- AUTH --
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# -- EMAIL --
def send_notification(subject, body):
    try:
        smtp_server = get_setting('smtp_server')
        smtp_port = int(get_setting('smtp_port', '587'))
        smtp_username = get_setting('smtp_username')
        smtp_password = get_setting('smtp_password')
        use_tls = get_setting('smtp_use_tls', 'true').lower() == 'true'
        to_email = get_setting('notification_email')
        if not smtp_username or not to_email:
            return False
        msg = f"Subject: {subject}\n\n{body}"
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if use_tls:
                server.starttls(context=context)
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, to_email, msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


# -- IMAGE UPLOADS --
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}


# -- INIT --
data = load_data()
init_db()


def get_featured_items():
    featured_names = data['home'].get('featured_items', [])
    featured = []
    for name in featured_names:
        for category, items in data['menu'].items():
            for item in items:
                if item['name'] == name:
                    featured.append(item)
                    break
    while len(featured) < 3:
        for category, items in data['menu'].items():
            if items and len(featured) < 3:
                if items[0] not in featured:
                    featured.append(items[0])
            if len(featured) >= 3:
                break
        if len(featured) >= 3:
            break
    return featured[:3]


@app.context_processor
def inject_globals():
    return {
        'restaurant': data['restaurant'],
        'theme': data['theme'],
        'order_online': data['online_ordering'],
        'gallery': data['gallery'],
        'events': data['events'],
        'footer': data['footer'],
        'current_year': datetime.now().year
    }


# ========================================
# PUBLIC ROUTES
# ========================================

@app.route('/')
def home():
    return render_template('home.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         reservations=data['reservations'],
                         home=data['home'],
                         menu=data['menu'],
                         testimonials=data['testimonials'],
                         online_ordering=data['online_ordering'],
                         featured=get_featured_items())


@app.route('/menu')
def menu_page():
    return render_template('menu.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         menu=data['menu'])


@app.route('/reservations', methods=['GET', 'POST'])
def reservations():
    if request.method == 'POST':
        reservation = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'date': request.form.get('date'),
            'time': request.form.get('time'),
            'guests': request.form.get('guests'),
            'special_requests': request.form.get('special_requests')
        }
        conn = get_db()
        conn.execute('''
            INSERT INTO reservations (name, email, phone, date, time, guests, special_requests)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (reservation['name'], reservation['email'], reservation['phone'],
              reservation['date'], reservation['time'], reservation['guests'],
              reservation['special_requests']))
        conn.commit()
        conn.close()
        send_notification(
            f"New Reservation: {reservation['name']}",
            f'''A new reservation has been made:

Name: {reservation['name']}
Email: {reservation['email']}
Phone: {reservation['phone']}
Date: {reservation['date']}
Time: {reservation['time']}
Guests: {reservation['guests']}
Special Requests: {reservation['special_requests'] or 'None'}
'''
        )
        data['analytics']['total_reservations'] = data['analytics'].get('total_reservations', 0) + 1
        save_data(data)
        return render_template('reservations.html',
                             theme=data['theme'],
                             restaurant=data['restaurant'],
                             reservations=data['reservations'],
                             success=True)
    return render_template('reservations.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         reservations=data['reservations'],
                         success=False)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        message = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'subject': request.form.get('subject'),
            'message': request.form.get('message')
        }
        conn = get_db()
        conn.execute('''
            INSERT INTO contact_messages (name, email, subject, message)
            VALUES (?, ?, ?, ?)
        ''', (message['name'], message['email'], message['subject'], message['message']))
        conn.commit()
        conn.close()
        send_notification(
            f"New Contact Message: {message['subject']}",
            f'''New message from {message['name']} ({message['email']}):

Subject: {message['subject']}
Message:
{message['message']}
'''
        )
        return render_template('contact.html',
                             theme=data['theme'],
                             restaurant=data['restaurant'],
                             contact=data['contact'],
                             success=True)
    return render_template('contact.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         contact=data['contact'],
                         success=False)


@app.route('/about')
def about():
    return render_template('about.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         about=data['about'])


@app.route('/order')
def order_online():
    return render_template('order.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         online_ordering=data['online_ordering'])


@app.route('/gallery')
def gallery():
    return render_template('gallery.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         gallery=data['gallery'])


@app.route('/events')
def events():
    return render_template('events.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         events=data['events'])


# ========================================
# AUTH & ADMIN ROUTES
# ========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('editor'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', theme=data['theme'], restaurant=data['restaurant'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/dashboard')
@admin_required
def dashboard():
    conn = get_db()
    rows = conn.execute("SELECT * FROM reservations ORDER BY created_at DESC LIMIT 10").fetchall()
    total_reservations = conn.execute("SELECT COUNT(*) as count FROM reservations").fetchone()['count']
    conn.close()
    analytics = data['analytics'].copy()
    analytics['total_reservations'] = total_reservations
    return render_template('dashboard.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         analytics=analytics,
                         reservations=[dict(r) for r in rows])


@app.route('/editor')
@admin_required
def editor():
    return render_template('editor.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         home=data['home'],
                         about=data['about'],
                         contact=data['contact'],
                         footer=data['footer'],
                         menu=data['menu'],
                         testimonials=data['testimonials'],
                         online_ordering=data['online_ordering'],
                         gallery=data['gallery'],
                         events=data['events'],
                         analytics=data['analytics'])


@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    if request.method == 'POST':
        set_setting('smtp_server', request.form.get('smtp_server', ''))
        set_setting('smtp_port', request.form.get('smtp_port', '587'))
        set_setting('smtp_username', request.form.get('smtp_username', ''))
        set_setting('smtp_password', request.form.get('smtp_password', ''))
        set_setting('smtp_use_tls', 'true' if request.form.get('smtp_use_tls') else 'false')
        set_setting('notification_email', request.form.get('notification_email', ''))
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if new_password:
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
            else:
                conn = get_db()
                user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
                if not check_password_hash(user['password_hash'], current_password):
                    flash('Current password is incorrect', 'error')
                else:
                    conn.execute(
                        "UPDATE users SET password_hash = ? WHERE id = ?",
                        (generate_password_hash(new_password), session['user_id'])
                    )
                    conn.commit()
                    flash('Password updated successfully')
                conn.close()
        return redirect(url_for('admin_settings'))
    settings = {
        'smtp_server': get_setting('smtp_server'),
        'smtp_port': get_setting('smtp_port'),
        'smtp_username': get_setting('smtp_username'),
        'smtp_password': get_setting('smtp_password'),
        'smtp_use_tls': get_setting('smtp_use_tls', 'true') == 'true',
        'notification_email': get_setting('notification_email')
    }
    return render_template('admin_settings.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         settings=settings)


@app.route('/api/upload_image', methods=['POST'])
@admin_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        url = url_for('static', filename=f'uploads/{filename}')
        return jsonify({'success': True, 'url': url})
    return jsonify({'success': False, 'error': 'Invalid file type'})


@app.route('/api/export/reservations')
@admin_required
def export_reservations():
    conn = get_db()
    rows = conn.execute("SELECT * FROM reservations ORDER BY created_at DESC").fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Date', 'Time', 'Guests', 'Special Requests', 'Created At'])
    for r in rows:
        writer.writerow([r['id'], r['name'], r['email'], r['phone'], r['date'], r['time'], r['guests'], r['special_requests'], r['created_at']])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'reservations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
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


@app.route('/api/update_hours', methods=['POST'])
@admin_required
def update_hours():
    hours = request.json
    data['restaurant']['hours'] = hours
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_social', methods=['POST'])
@admin_required
def update_social():
    social = request.json
    data['restaurant']['social'] = social
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_home', methods=['POST'])
@admin_required
def update_home():
    updates = request.json
    for key, value in updates.items():
        if key in data['home'] and key != 'featured_items':
            data['home'][key] = value
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_home_featured', methods=['POST'])
@admin_required
def update_home_featured():
    featured = request.json.get('featured_items', [])
    data['home']['featured_items'] = featured
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


@app.route('/api/update_about_values', methods=['POST'])
@admin_required
def update_about_values():
    values = request.json.get('values', [])
    data['about']['values'] = values
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_about_stats', methods=['POST'])
@admin_required
def update_about_stats():
    stats = request.json.get('chef_stats', [])
    data['about']['chef_stats'] = stats
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_contact', methods=['POST'])
@admin_required
def update_contact():
    updates = request.json
    for key, value in updates.items():
        if key in data['contact']:
            data['contact'][key] = value
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_footer', methods=['POST'])
@admin_required
def update_footer():
    updates = request.json
    for key, value in updates.items():
        if key in data['footer']:
            data['footer'][key] = value
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_reservations', methods=['POST'])
@admin_required
def update_reservations():
    updates = request.json
    for key, value in updates.items():
        if key in data['reservations']:
            data['reservations'][key] = value
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_testimonials', methods=['POST'])
@admin_required
def update_testimonials():
    testimonials = request.json.get('testimonials', [])
    data['testimonials'] = testimonials
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_online_ordering', methods=['POST'])
@admin_required
def update_online_ordering():
    updates = request.json
    for key, value in updates.items():
        if key in data['online_ordering'] and key != 'platforms':
            data['online_ordering'][key] = value
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_ordering_platforms', methods=['POST'])
@admin_required
def update_ordering_platforms():
    platforms = request.json.get('platforms', [])
    data['online_ordering']['platforms'] = platforms
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_gallery', methods=['POST'])
@admin_required
def update_gallery():
    updates = request.json
    for key, value in updates.items():
        if key in data['gallery'] and key != 'photos':
            data['gallery'][key] = value
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_gallery_photos', methods=['POST'])
@admin_required
def update_gallery_photos():
    photos = request.json.get('photos', [])
    data['gallery']['photos'] = photos
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_events', methods=['POST'])
@admin_required
def update_events():
    updates = request.json
    for key, value in updates.items():
        if key in data['events'] and key not in ['services', 'upcoming_events']:
            data['events'][key] = value
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_event_services', methods=['POST'])
@admin_required
def update_event_services():
    services = request.json.get('services', [])
    data['events']['services'] = services
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/update_upcoming_events', methods=['POST'])
@admin_required
def update_upcoming_events():
    events = request.json.get('upcoming_events', [])
    data['events']['upcoming_events'] = events
    save_data(data)
    return jsonify({'success': True})


@app.route('/api/menu/add', methods=['POST'])
@admin_required
def add_menu_item():
    item_data = request.json
    category = item_data.get('category')
    item = {
        'name': item_data.get('name'),
        'description': item_data.get('description'),
        'price': float(item_data.get('price')),
        'popular': item_data.get('popular', False),
        'image': item_data.get('image', ''),
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
    index = int(item_data.get('index'))
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
    index = int(item_data.get('index'))
    if category in data['menu'] and 0 <= index < len(data['menu'][category]):
        data['menu'][category][index] = {
            'name': item_data.get('name'),
            'description': item_data.get('description'),
            'price': float(item_data.get('price')),
            'popular': item_data.get('popular', False),
            'image': item_data.get('image', ''),
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


if __name__ == '__main__':
    print("=" * 60)
    print("  RESTAURANT WEBSITE - PREMIUM EDITION")
    print("=" * 60)
    print("  Public Site:  http://127.0.0.1:5000")
    print("  Admin Login:  http://127.0.0.1:5000/login")
    print("  Editor:       http://127.0.0.1:5000/editor")
    print("  Dashboard:    http://127.0.0.1:5000/dashboard")
    print("  Settings:     http://127.0.0.1:5000/admin/settings")
    print("=" * 60)
    print("  Default login: admin / admin")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
