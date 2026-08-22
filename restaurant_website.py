from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
import json
import os
import secrets
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

DATA_FILE = 'restaurant_data.json'

# Default data
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
        'google_maps_embed': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3022.1!2d-74.006!3d40.7128!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zNDDCsDQyJzQ2LjEiTiA3NMKwMDAnMjEuNiJX!5e0!3m2!1sen!2us!4v1'
    },
    'about': {
        'story': 'Founded in 2010 by Chef Marco Rossi, La Bella Cucina brings the heart of Tuscany to your table.',
        'chef_name': 'Chef Marco Rossi',
        'chef_bio': 'With over 20 years of experience in Michelin-starred kitchens.',
        'chef_image': 'https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=400&h=400&fit=crop',
        'interior_image': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&h=600&fit=crop',
        'food_image': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&h=600&fit=crop',
        'values': [
            {'title': 'Fresh Ingredients', 'description': 'We source locally and import directly from Italy.'},
            {'title': 'Family Recipes', 'description': 'Every sauce and dough is made from scratch.'},
            {'title': 'Warm Hospitality', 'description': 'We treat every guest like family.'}
        ]
    },
    'testimonials': [
        {'name': 'Sarah M.', 'text': 'The best carbonara I have had outside of Rome!', 'rating': 5},
        {'name': 'James & Linda K.', 'text': 'We celebrated our anniversary here and the staff made us feel so special.', 'rating': 5},
        {'name': 'David R.', 'text': 'Authentic flavors, generous portions, and the wine selection is incredible.', 'rating': 5}
    ],
    'menu': {
        'appetizers': [
            {'name': 'Bruschetta', 'description': 'Toasted bread with tomatoes and basil', 'price': 12.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1572695157369-7b5e6e5a04c5?w=500&h=350&fit=crop', 'dietary': ['vegetarian']},
            {'name': 'Calamari', 'description': 'Crispy fried calamari with marinara', 'price': 14.99, 'popular': False, 'image': 'https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6?w=500&h=350&fit=crop', 'dietary': []}
        ],
        'mains': [
            {'name': 'Spaghetti Carbonara', 'description': 'Classic pasta with guanciale and pecorino', 'price': 22.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1612874742237-6526221588e3?w=500&h=350&fit=crop', 'dietary': []},
            {'name': 'Chicken Parmigiana', 'description': 'Breaded chicken with marinara and mozzarella', 'price': 24.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1632778149955-e80f8ceca2e8?w=500&h=350&fit=crop', 'dietary': []}
        ],
        'desserts': [
            {'name': 'Tiramisu', 'description': 'Classic Italian coffee-flavored dessert', 'price': 10.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=500&h=350&fit=crop', 'dietary': ['vegetarian']}
        ],
        'beverages': [
            {'name': 'Espresso', 'description': 'Rich Italian coffee', 'price': 4.99, 'popular': True, 'image': 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500&h=350&fit=crop', 'dietary': ['vegetarian', 'gluten-free']}
        ]
    },
    'reservations': {
        'hold_time': '15 minutes',
        'large_party_note': 'Parties of 8+ please call directly',
        'time_slots': ['17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00']
    },
    'online_ordering': {
        'enabled': True,
        'page_title': 'Order Online',
        'page_subtitle': 'Enjoy our cuisine from the comfort of your home.',
        'platforms': [
            {'name': 'DoorDash', 'url': 'https://doordash.com', 'icon': 'fa-motorcycle', 'active': True, 'color': '#FF3008'},
            {'name': 'UberEats', 'url': 'https://ubereats.com', 'icon': 'fa-utensils', 'active': True, 'color': '#06C167'}
        ]
    },
    'gallery': {
        'enabled': True,
        'page_title': 'Gallery',
        'page_subtitle': 'A glimpse into our kitchen and dishes.',
        'photos': [
            {'url': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&h=600&fit=crop', 'caption': 'Our dining room', 'category': 'interior'},
            {'url': 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800&h=600&fit=crop', 'caption': 'Margherita Pizza', 'category': 'food'}
        ]
    },
    'events': {
        'enabled': True,
        'page_title': 'Events & Private Dining',
        'page_subtitle': 'Host your next celebration with us.',
        'hero_image': 'https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=1920&h=800&fit=crop',
        'cta_title': 'Book Your Private Event',
        'cta_text': 'Contact us to discuss custom menus and special requests.',
        'services': [
            {'title': 'Private Dining Room', 'description': 'Intimate space for up to 24 guests.', 'icon': 'fa-utensils'},
            {'title': 'Full Restaurant Buyout', 'description': 'Host up to 80 guests for an exclusive experience.', 'icon': 'fa-building'}
        ],
        'upcoming_events': [
            {'title': 'Wine & Dine Wednesday', 'description': '3-course prix fixe menu with wine pairings.', 'date': 'Every Wednesday', 'image': 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600&h=400&fit=crop'}
        ]
    },
    'analytics': {
        'daily_sales': [1250, 1420, 1380, 1680, 2100, 2450, 1800],
        'monthly_revenue': [45000, 52000, 49000, 58000, 62000, 68000],
        'popular_items': ['Spaghetti Carbonara', 'Chicken Parmigiana'],
        'customer_satisfaction': 4.8,
        'total_reservations': 156
    }
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_DATA.copy()

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

data = load_data()

# Admin credentials (for testing)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_featured_items():
    featured = []
    for category, items in data['menu'].items():
        for item in items:
            if item.get('popular') and len(featured) < 3:
                featured.append(item)
    return featured[:3]

@app.context_processor
def inject_globals():
    return {
        'restaurant': data['restaurant'],
        'theme': data['theme'],
        'current_year': datetime.now().year
    }

@app.route('/')
def home():
    return render_template('home.html',
        theme=data['theme'],
        restaurant=data['restaurant'],
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

@app.route('/about')
def about():
    return render_template('about.html',
        theme=data['theme'],
        restaurant=data['restaurant'],
        about=data['about'])

@app.route('/contact')
def contact():
    return render_template('contact.html',
        theme=data['theme'],
        restaurant=data['restaurant'])

@app.route('/reservations')
def reservations():
    return render_template('reservations.html',
        theme=data['theme'],
        restaurant=data['restaurant'],
        reservations=data['reservations'])

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

@app.route('/order')
def order():
    return render_template('order.html',
        theme=data['theme'],
        restaurant=data['restaurant'],
        online_ordering=data['online_ordering'])

@app.route('/dashboard')
@admin_required
def dashboard():
    return render_template('dashboard.html',
        theme=data['theme'],
        restaurant=data['restaurant'],
        analytics=data['analytics'])

@app.route('/editor')
@admin_required
def editor():
    return render_template('editor.html',
        theme=data['theme'],
        restaurant=data['restaurant'],
        menu=data['menu'],
        about=data['about'],
        testimonials=data['testimonials'],
        analytics=data['analytics'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html',
        theme=data['theme'],
        restaurant=data['restaurant'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

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
    item_data = request.json
    category = item_data.get('category')
    index = int(item_data.get('index', -1))
    if category in data['menu'] and 0 <= index < len(data['menu'][category]):
        data['menu'][category][index] = {
            'name': item_data.get('name'),
            'description': item_data.get('description'),
            'price': float(item_data.get('price', 0)),
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
    print("  RESTAURANT WEBSITE")
    print("=" * 60)
    print("  Website:  http://127.0.0.1:5000")
    print("  Admin:    admin / admin123")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=5000)
