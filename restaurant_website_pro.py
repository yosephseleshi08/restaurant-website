"""
La Bella Cucina — Restaurant CMS Pro Edition v2.0
"""
from flask import (
    Flask, render_template, request, jsonify, redirect, url_for,
    session, flash, send_file, Response, abort, g
)
from flask_wtf.csrf import CSRFProtect  # ✅ FIX 1: Added CSRF Protect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json, os, csv, io, secrets, re, requests, cloudinary, cloudinary.uploader, threading

def create_app(config_name="production"):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)
    
    # ✅ FIX 1: Initialize CSRF Protection
    csrf = CSRFProtect(app)
    
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
        key_func=get_remote_address, app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.environ.get('REDIS_URL', 'memory://'), strategy="fixed-window"
    )

    db = SQLAlchemy(app)
    DATA_FILE = 'restaurant_data.json'
    _data_lock = threading.Lock()

    DEFAULT_DATA = {
        'theme': {'primary_color': '#0B0F19', 'secondary_color': '#C9A96E', 'background_color': '#FAF7F2', 'text_color': '#1A1A1A', 'card_bg': '#FFFFFF', 'accent_color': '#8B7355', 'font_family': "'Playfair Display', 'Georgia', serif", 'dark_mode': False, 'custom_css': ''},
        'seo': {'meta_title': 'Aurelia — Modern Coastal Mediterranean Dining', 'meta_description': 'Experience award-winning coastal Mediterranean cuisine at Aurelia.', 'meta_keywords': 'mediterranean restaurant, fine dining, seafood, reservations', 'og_image': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&h=630&fit=crop', 'google_analytics_id': '', 'facebook_pixel': ''},
        'restaurant': {'name': "Aurelia", 'tagline': "Modern Coastal Mediterranean Dining", 'address': "47 Harbor View Boulevard, Marina District, CA 94123", 'phone': "(415) 555-0199", 'phone_link': "+14155550199", 'email': "reservations@aurelia.co", 'hours': {'monday': '5:00 PM - 10:00 PM', 'tuesday': '5:00 PM - 10:00 PM', 'wednesday': '5:00 PM - 10:00 PM', 'thursday': '5:00 PM - 10:00 PM', 'friday': '5:00 PM - 11:00 PM', 'saturday': '4:30 PM - 11:00 PM', 'sunday': '4:00 PM - 9:30 PM'}, 'social': {'instagram': 'aurelia.dining', 'facebook': 'AureliaDining', 'twitter': 'AureliaDining', 'yelp': 'aurelia-marina-district'}},
        'about': {'story': "Founded in 2019 by Chef Elena Marchetti, Aurelia was born from a simple belief: the Mediterranean diet is not just healthy — it is the purest expression of joy on a plate. Every evening, as the sun dips below the Golden Gate, our kitchen comes alive with the aromas of charcoal-grilled branzino, hand-rolled paccheri, and citrus-kissed olive oil cakes.", 'chef_name': "Chef Elena Marchetti", 'chef_bio': "A James Beard Award semifinalist, Chef Elena trained at El Celler de Can Roca and Lycabettus Restaurant in Athens. Her philosophy is simple: let the ingredient speak.", 'chef_image': "https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=600&h=600&fit=crop&crop=faces", 'interior_image': "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1600&h=900&fit=crop", 'food_image': "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1600&h=900&fit=crop", 'values': [{'title': 'Ocean to Table', 'description': 'We source seafood daily from Monterey Bay, ensuring the freshest catch reaches your plate within hours.'}, {'title': 'Zero Waste Kitchen', 'description': 'Every herb stem becomes a sauce. Every bone becomes a stock. Sustainability is not a trend — it is our foundation.'}, {'title': 'Wine as Philosophy', 'description': 'Our sommelier curates 200+ labels from coastal vineyards, pairing each course with intention and care.'}]},
        'testimonials': [{'name': 'Marcus T.', 'text': 'The grilled octopus transported me straight to a taverna in Santorini. Simply extraordinary.', 'rating': 5}, {'name': 'Priya & James K.', 'text': 'We hosted our rehearsal dinner here — every detail was perfection. The staff anticipated needs we did not know we had.', 'rating': 5}, {'name': 'David R., SF Chronicle', 'text': 'Aurelia is doing what few restaurants dare: making fine dining feel like coming home.', 'rating': 5}, {'name': 'Isabella M.', 'text': 'The olive oil cake alone is worth the flight to San Francisco. A revelation.', 'rating': 5}],
        'menu': {
            'raw bar': [{'name': 'Oysters on the Half Shell', 'description': 'Kumamoto & Miyagi selection, mignonette granita, lemon verbena', 'price': 24.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600&h=400&fit=crop', 'dietary': ['gluten-free']}, {'name': 'Tuna Crudo', 'description': 'Bigeye tuna, Sicilian olive oil, Calabrian chili, preserved lemon', 'price': 28.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1534604973900-c43ab4c2e0ab?w=600&h=400&fit=crop', 'dietary': ['gluten-free', 'dairy-free']}, {'name': 'Caviar Service', 'description': 'Osetra caviar, blinis, crème fraîche, chive, shallot', 'price': 85.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=600&h=400&fit=crop', 'dietary': ['vegetarian']}],
            'small plates': [{'name': 'Charred Eggplant Dip', 'description': 'Smoky baba ganoush, pomegranate molasses, toasted pine nuts, warm pita', 'price': 16.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?w=600&h=400&fit=crop', 'dietary': ['vegetarian']}, {'name': 'Whipped Feta', 'description': "Whipped sheep's milk feta, honeycomb, toasted walnuts, warm sourdough", 'price': 18.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1626200419199-391ae4be7a41?w=600&h=400&fit=crop', 'dietary': ['vegetarian']}, {'name': 'Grilled Spanish Octopus', 'description': 'Charred octopus, fingerling potatoes, smoked paprika, salsa verde', 'price': 26.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=400&fit=crop', 'dietary': ['gluten-free', 'dairy-free']}, {'name': 'Burrata & Heirloom Tomatoes', 'description': 'Pugliese burrata, San Marzano tomatoes, basil oil, aged balsamic', 'price': 22.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1608897013039-887f21d8c804?w=600&h=400&fit=crop', 'dietary': ['vegetarian', 'gluten-free']}, {'name': 'Crispy Calamari', 'description': 'Lightly fried squid, lemon aioli, marinara, fresh herbs', 'price': 19.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1599487488170-d11ec45f5650?w=600&h=400&fit=crop', 'dietary': []}, {'name': 'Mezze Platter', 'description': 'Hummus, baba ganoush, tzatziki, warm pita, marinated olives', 'price': 24.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=600&h=400&fit=crop', 'dietary': ['vegetarian']}],
            'mains': [{'name': 'Whole Roasted Branzino', 'description': 'Mediterranean sea bass, herb-stuffed, lemon, extra virgin olive oil', 'price': 42.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=600&h=400&fit=crop', 'dietary': ['gluten-free', 'dairy-free']}, {'name': 'Truffle Paccheri', 'description': 'Hand-rolled paccheri, black truffle cream, aged Parmigiano-Reggiano', 'price': 38.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600&h=400&fit=crop', 'dietary': ['vegetarian']}, {'name': 'Dry-Aged Ribeye', 'description': '45-day dry-aged ribeye, bone marrow butter, charred spring onion', 'price': 65.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1600891964092-4316c288032e?w=600&h=400&fit=crop', 'dietary': ['gluten-free']}, {'name': 'Lamb Osso Buco', 'description': 'Braised lamb shank, saffron risotto, gremolata, natural jus', 'price': 48.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=400&fit=crop', 'dietary': ['gluten-free']}, {'name': 'Lobster Linguine', 'description': 'Fresh Maine lobster, cherry tomatoes, white wine, garlic, basil', 'price': 52.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1563379926898-05f4575a45d7?w=600&h=400&fit=crop', 'dietary': []}, {'name': 'Grilled Swordfish', 'description': 'Caper berry relish, roasted fennel, citrus vinaigrette', 'price': 44.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1580476262798-bddd9f4b7369?w=600&h=400&fit=crop', 'dietary': ['gluten-free', 'dairy-free']}],
            'desserts': [{'name': 'Olive Oil Cake', 'description': 'Citrus-scented olive oil sponge, blood orange curd, mascarpone chantilly', 'price': 14.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=600&h=400&fit=crop', 'dietary': ['vegetarian']}, {'name': 'Dark Chocolate Fondant', 'description': 'Valrhona dark chocolate, sea salt caramel core, vanilla bean ice cream', 'price': 16.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1624353365286-3f8d62daad51?w=600&h=400&fit=crop', 'dietary': ['vegetarian']}, {'name': 'Baklava Ice Cream', 'description': 'Pistachio ice cream, honey-soaked phyllo, rose water syrup', 'price': 13.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=600&h=400&fit=crop', 'dietary': ['vegetarian']}, {'name': 'Tiramisu', 'description': 'Classic Italian tiramisu, espresso-soaked ladyfingers, cocoa', 'price': 14.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=600&h=400&fit=crop', 'dietary': ['vegetarian']}, {'name': 'Panna Cotta', 'description': 'Vanilla bean panna cotta, seasonal berry compote, mint', 'price': 12.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=600&h=400&fit=crop', 'dietary': ['vegetarian', 'gluten-free']}],
            'drinks': [{'name': 'The Aegean', 'description': 'Mastiha liqueur, cucumber, fresh lime, Mediterranean tonic', 'price': 18.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']}, {'name': 'Santorini Sunset', 'description': 'Aperol, prosecco, blood orange, thyme, edible flower', 'price': 19.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']}, {'name': 'Olive Branch', 'description': 'Gin, olive brine, dry vermouth, castelvetrano olive', 'price': 17.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1575023782549-62ca0d244b39?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']}, {'name': 'Negroni Bianco', 'description': 'Suze, Lillet Blanc, dry gin, grapefruit twist', 'price': 18.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']}, {'name': 'Mediterranean Mule', 'description': 'Vodka, fig syrup, fresh lime, ginger beer, rosemary', 'price': 16.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1536935338788-846bb9981813?w=600&h=400&fit=crop', 'dietary': ['vegan']}, {'name': 'Espresso Martini', 'description': 'Vodka, fresh espresso, coffee liqueur, vanilla', 'price': 17.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=600&h=400&fit=crop', 'dietary': ['vegan']}],
            'wine selection': [{'name': 'Santorini Assyrtiko', 'description': 'Gaia Wines, 2022 — Crisp minerality, citrus, saline finish', 'price': 16.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']}, {'name': 'Barolo DOCG', 'description': 'Pio Cesare, 2018 — Nebbiolo, tar and roses, firm tannins', 'price': 28.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']}, {'name': 'Châteauneuf-du-Pape', 'description': 'Domaine du Pegau, 2019 — Grenache blend, dark fruit, spice', 'price': 24.00, 'popular': False, 'image': 'https://images.unsplash.com/photo-1553361371-9b22f78e8b1d?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']}, {'name': 'Provence Rosé', 'description': 'Miraval, 2023 — Fresh strawberry, white peach, mineral', 'price': 18.00, 'popular': True, 'image': 'https://images.unsplash.com/photo-1558001373-7b93ee48ffa0?w=600&h=400&fit=crop', 'dietary': ['vegan', 'gluten-free']}]
        },
        'reservations': {'hold_time': '15 minutes', 'large_party_note': 'Parties of 8+ please contact our events team directly', 'time_slots': ['17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30'], 'max_guests_per_slot': 24},
        'online_ordering': {'enabled': True, 'page_title': 'Order Online', 'page_subtitle': "Enjoy Aurelia's coastal Mediterranean cuisine at home.", 'platforms': [{'name': 'DoorDash', 'url': 'https://doordash.com', 'icon': 'fa-motorcycle', 'active': True, 'color': '#FF3008'}, {'name': 'UberEats', 'url': 'https://ubereats.com', 'icon': 'fa-utensils', 'active': True, 'color': '#06C167'}]},
        'gallery': {'enabled': True, 'page_title': 'Gallery', 'page_subtitle': 'A glimpse into our kitchen, our craft, and the warm, sun-drenched atmosphere.', 'photos': [{'url': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&h=600&fit=crop', 'caption': 'The main dining room at golden hour', 'category': 'interior'}, {'url': 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&h=600&fit=crop', 'caption': 'Fresh oysters from Monterey Bay', 'category': 'food'}, {'url': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=800&h=600&fit=crop', 'caption': 'Whole roasted branzino, Ligurian style', 'category': 'food'}, {'url': 'https://images.unsplash.com/photo-1592861956120-e524fc739696?w=800&h=600&fit=crop', 'caption': 'Private dining room', 'category': 'interior'}, {'url': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&h=600&fit=crop', 'caption': 'Chef Elena plating the signature dish', 'category': 'food'}, {'url': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=800&h=600&fit=crop', 'caption': 'Grilled Spanish octopus', 'category': 'food'}, {'url': 'https://images.unsplash.com/photo-1563379926898-05f4575a45d7?w=800&h=600&fit=crop', 'caption': 'Fresh lobster linguine', 'category': 'food'}, {'url': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800&h=600&fit=crop', 'caption': 'Truffle paccheri pasta', 'category': 'food'}, {'url': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=800&h=600&fit=crop', 'caption': 'Our signature olive oil cake', 'category': 'food'}, {'url': 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=800&h=600&fit=crop', 'caption': 'The Aegean cocktail', 'category': 'drinks'}, {'url': 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=800&h=600&fit=crop', 'caption': 'Santorini Sunset aperitif', 'category': 'drinks'}, {'url': 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=800&h=600&fit=crop', 'caption': 'Santorini Assyrtiko wine', 'category': 'drinks'}, {'url': 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=800&h=600&fit=crop', 'caption': 'Negroni Bianco', 'category': 'drinks'}, {'url': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=800&h=600&fit=crop', 'caption': 'Espresso Martini', 'category': 'drinks'}, {'url': 'https://images.unsplash.com/photo-1558001373-7b93ee48ffa0?w=800&h=600&fit=crop', 'caption': 'Provence Rosé selection', 'category': 'drinks'}, {'url': 'https://images.unsplash.com/photo-1536935338788-846bb9981813?w=800&h=600&fit=crop', 'caption': 'Mediterranean Mule', 'category': 'drinks'}, {'url': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&h=600&fit=crop', 'caption': 'The bar at Aurelia', 'category': 'interior'}, {'url': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&h=600&fit=crop', 'caption': 'Candlelit dinner setting', 'category': 'interior'}]},
        'events': {'enabled': True, 'page_title': 'Events & Private Dining', 'page_subtitle': 'Host your next celebration at Aurelia.', 'hero_image': 'https://images.unsplash.com/photo-1519167758481-83f55049b3b3?w=1920&h=800&fit=crop', 'cta_title': 'Plan Your Private Event', 'cta_text': 'Let our events team design a bespoke experience.', 'services': [{'title': 'The Terrace', 'description': 'Intimate space for up to 32 guests.', 'icon': 'fa-utensils'}, {'title': 'The Cellar', 'description': 'Underground wine cellar for up to 16 guests.', 'icon': 'fa-wine-glass'}], 'upcoming_events': [{'title': "Chef Elena's Sunday Supper", 'description': 'A rotating family-style menu. $85 per person.', 'date': 'Every Sunday, 6:00 PM', 'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=400&fit=crop'}, {'title': 'Wine & Waves', 'description': 'Monthly tasting series exploring coastal wine regions.', 'date': 'Last Thursday of each month', 'image': 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600&h=400&fit=crop'}, {'title': 'Pasta Masterclass', 'description': 'Learn to make paccheri, pappardelle, and squid ink fettuccine.', 'date': 'First Saturday of each month', 'image': 'https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=600&h=400&fit=crop'}]},
        'analytics': {'daily_sales': [2850, 3200, 2950, 4100, 5200, 6800, 5900], 'monthly_revenue': [98000, 112000, 105000, 128000, 135000, 148000], 'popular_items': ['Whole Roasted Branzino', 'Grilled Spanish Octopus', 'Truffle Paccheri'], 'customer_satisfaction': 4.9, 'total_reservations': 342},
        'settings': {'currency': '$', 'tax_rate': 8.75, 'delivery_fee': 6.0, 'min_order': 25.0, 'cookie_consent': True, 'enable_online_ordering': True, 'enable_reservations': True, 'enable_events': True, 'enable_gallery': True, 'enable_loyalty': True, 'enable_gift_cards': True, 'enable_waitlist': True, 'enable_table_management': True, 'enable_kitchen_display': True}
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
                if key not in result: result[key] = value
                else: result[key] = deep_merge(value, result[key])
            return result
        return current

    def load_data():
        with _data_lock:
            if os.path.exists(DATA_FILE):
                try:
                    with open(DATA_FILE, 'r', encoding='utf-8') as f: return deep_merge(DEFAULT_DATA, json.load(f))
                except: return DEFAULT_DATA.copy()
            return DEFAULT_DATA.copy()

    def save_data(data_obj):
        with _data_lock:
            try:
                with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data_obj, f, indent=2, ensure_ascii=False)
            except IOError as e: app.logger.error(f"Failed to save data: {e}")

    def init_db():
        with app.app_context():
            db.create_all()
            if User.query.count() == 0:
                initial_password = os.environ.get('ADMIN_INITIAL_PASSWORD') or 'admin123'
                db.session.add(User(username='admin', password_hash=generate_password_hash(initial_password), role='admin'))
                db.session.commit()
                print("\n" + "=" * 60 + "\n  ADMIN CREDENTIALS: admin / " + initial_password + "\n" + "=" * 60 + "\n")

    def track_page_view(page):
        try:
            db.session.add(PageView(page=page))
            db.session.commit()
        except: db.session.rollback()

    def get_featured_items(data):
        featured = []
        for category in ['small plates', 'mains', 'desserts']:
            for item in data['menu'].get(category, []):
                if item.get('popular'): featured.append({**item, 'category': category.title()})
        return featured[:6]

    @app.before_request
    def before_request():
        g.user = None; g.user_role = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user: g.user, g.user_role = user, user.role

    @app.context_processor
    def inject_globals():
        data = load_data()
        return {'theme': data['theme'], 'restaurant': data['restaurant'], 'settings': data['settings'], 'seo': data['seo'], 'user_role': g.user_role, 'current_year': datetime.utcnow().year}

    @app.route('/health')
    def health(): return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

    @app.route('/')
    def home():
        track_page_view('home')
        data = load_data()
        return render_template('home.html', theme=data['theme'], restaurant=data['restaurant'], menu=data['menu'], testimonials=data['testimonials'], online_ordering=data['online_ordering'], featured=get_featured_items(data), seo=data['seo'], settings=data['settings'])

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
            name, email, subject, message = request.form.get('name','').strip(), request.form.get('email','').strip(), request.form.get('subject','').strip(), request.form.get('message','').strip()
            if all([name, email, subject, message]):
                db.session.add(ContactMessage(name=name[:100], email=email[:120], subject=subject[:100], message=message[:5000]))
                db.session.commit()
                flash("Message sent! We'll get back to you soon.", 'success')
                return redirect(url_for('contact'))
            flash('Please fill in all fields', 'error')
        track_page_view('contact')
        return render_template('contact.html', theme=data['theme'], restaurant=data['restaurant'], seo=data['seo'], settings=data['settings'])

    @app.route('/reservations', methods=['GET', 'POST'])
    def reservations():
        data = load_data()
        if request.method == 'POST':
            name, email, phone, date, time, guests, special_requests = request.form.get('name','').strip(), request.form.get('email','').strip(), request.form.get('phone','').strip(), request.form.get('date','').strip(), request.form.get('time','').strip(), request.form.get('guests','').strip(), request.form.get('special_requests','').strip()
            if all([name, email, phone, date, time, guests]):
                db.session.add(Reservation(name=name[:100], email=email[:120], phone=phone[:50], date=date, time=time, guests=guests, special_requests=special_requests[:1000]))
                db.session.commit()
                flash("Reservation request received! We'll confirm shortly.", 'success')
                return redirect(url_for('reservations'))
            flash('Please fill in all required fields', 'error')
        track_page_view('reservations')
        return render_template('reservations.html', theme=data['theme'], restaurant=data['restaurant'], reservations=data['reservations'], seo=data['seo'], settings=data['settings'])

    @app.route('/order')
    @app.route('/order/menu')
    def order_menu():
        track_page_view('order')
        data = load_data()
        return render_template('order.html', theme=data['theme'], restaurant=data['restaurant'], menu=data['menu'], online_ordering=data['online_ordering'], settings=data['settings'], seo=data['seo'])

    # ✅ FIX 2: Cart route now calculates math and passes it to the template
    @app.route('/cart')
    def cart():
        track_page_view('cart')
        data = load_data()
        cart_items = session.get('cart', [])
        subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
        tax_rate = data['settings'].get('tax_rate', 8.75) / 100
        tax = subtotal * tax_rate
        delivery_fee = data['settings'].get('delivery_fee', 0.0)
        grand_total = subtotal + tax + delivery_fee
        return render_template('cart.html', theme=data['theme'], restaurant=data['restaurant'], settings=data['settings'], seo=data['seo'], 
                               cart=cart_items, total=subtotal, tax=tax, delivery_fee=delivery_fee, grand_total=grand_total)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username, password = request.form.get('username', '').strip(), request.form.get('password', '').strip()
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['username'] = user.username
                return redirect(url_for('dashboard'))
            flash('Invalid username or password', 'error')
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            flash("Please log in to view the dashboard. (Demo: admin / admin123)", "info")
            return redirect(url_for('login'))
        data = load_data()
        return render_template('dashboard.html', theme=data['theme'], restaurant=data['restaurant'], analytics=data['analytics'], settings=data['settings'])

    @app.route('/editor')
    def editor():
        if 'user_id' not in session:
            flash("Please log in to view the editor.", "info")
            return redirect(url_for('login'))
        data = load_data()
        return render_template('editor.html', theme=data['theme'], restaurant=data['restaurant'], settings=data['settings'], data=data)

    @app.route('/kitchen')
    def kitchen():
        if 'user_id' not in session:
            flash("Please log in to view the kitchen display.", "info")
            return redirect(url_for('login'))
        data = load_data()
        orders = Order.query.filter(Order.status.in_(['pending', 'preparing', 'ready'])).order_by(Order.created_at.asc()).all()
        return render_template('kitchen.html', theme=data['theme'], restaurant=data['restaurant'], orders=orders, settings=data['settings'])

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('home'))

    # ✅ FIX 3: Added Cart API endpoints (EXACTLY ONCE)
    @app.route('/api/cart/add', methods=['POST'])
    def add_to_cart():
        item = request.json
        cart = session.get('cart', [])
        for c in cart:
            if c['name'] == item['name']:
                c['quantity'] += item.get('quantity', 1)
                break
        else:
            cart.append(item)
        session['cart'] = cart
        return jsonify({'success': True, 'count': len(cart)})

    @app.route('/api/cart/clear', methods=['POST'])
    def clear_cart():
        session['cart'] = []
        return jsonify({'success': True})

        # ─── STRIPE CHECKOUT ROUTE ────────────────────────────────────────
    @app.route('/api/create-checkout-session', methods=['POST'])
    @csrf.exempt 
    def create_checkout_session():
        import stripe
        # PASTE YOUR sk_test_... KEY INSIDE THE QUOTES BELOW
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')  # ← KEEP THIS
        
        try:
            req_data = request.json
            cart_items = req_data.get('items', [])
            
            line_items = []
            for item in cart_items:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': item['name']},
                        'unit_amount': int(item['price'] * 100), # Stripe requires cents
                    },
                    'quantity': item['quantity'],
                })

            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode='payment',
                success_url=request.host_url + 'cart?success=true',
                cancel_url=request.host_url + 'cart?canceled=true',
            )
            return jsonify({'url': checkout_session.url})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    # ─── EDITOR API ENDPOINTS ──────────────────────────────────────────
    @app.route('/api/update_theme', methods=['POST'])
    def update_theme():
        if 'user_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        data = load_data()
        data['theme'].update(request.json)
        save_data(data)
        return jsonify({'success': True})

    @app.route('/api/update_restaurant', methods=['POST'])
    def update_restaurant():
        if 'user_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        data = load_data()
        data['restaurant'].update(request.json)
        save_data(data)
        return jsonify({'success': True})

    @app.route('/api/update_hours', methods=['POST'])
    def update_hours():
        if 'user_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        data = load_data()
        data['restaurant']['hours'] = request.json
        save_data(data)
        return jsonify({'success': True})

    @app.route('/api/update_about', methods=['POST'])
    def update_about():
        if 'user_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        data = load_data()
        data['about'].update(request.json)
        save_data(data)
        return jsonify({'success': True})

    @app.route('/api/update_seo', methods=['POST'])
    def update_seo():
        if 'user_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        data = load_data()
        data['seo'].update(request.json)
        save_data(data)
        return jsonify({'success': True})

    @app.route('/api/menu/add', methods=['POST'])
    def add_menu_item():
        if 'user_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        data = load_data()
        category = request.json.get('category')
        if category not in data['menu']: data['menu'][category] = []
        data['menu'][category].append(request.json.get('item'))
        save_data(data)
        return jsonify({'success': True})

    @app.route('/api/menu/update', methods=['POST'])
    def update_menu_item():
        if 'user_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        data = load_data()
        category = request.json.get('category')
        index = int(request.json.get('index', -1))
        if category in data['menu'] and 0 <= index < len(data['menu'][category]):
            data['menu'][category][index] = request.json.get('item')
            save_data(data)
            return jsonify({'success': True})
        return jsonify({'success': False})

    @app.route('/api/menu/delete', methods=['POST'])
    def delete_menu_item():
        if 'user_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        data = load_data()
        category = request.json.get('category')
        index = int(request.json.get('index', -1))
        if category in data['menu'] and 0 <= index < len(data['menu'][category]):
            data['menu'][category].pop(index)
            save_data(data)
            return jsonify({'success': True})
        return jsonify({'success': False})

    @app.route('/api/testimonials/update', methods=['POST'])
    def update_testimonials():
        if 'user_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        data = load_data()
        data['testimonials'] = request.json.get('testimonials', [])
        save_data(data)
        return jsonify({'success': True})

    @app.route('/api/gallery/update', methods=['POST'])
    def update_gallery():
        if 'user_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        data = load_data()
        data['gallery']['photos'] = request.json.get('photos', [])
        save_data(data)
        return jsonify({'success': True})

    @app.route('/api/events/update', methods=['POST'])
    def update_events():
        if 'user_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        data = load_data()
        data['events'].update(request.json)
        save_data(data)
        return jsonify({'success': True})

    @app.route('/api/upload_image', methods=['POST'])
    def upload_image():
        if 'user_id' not in session: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        if 'image' not in request.files: return jsonify({'success': False, 'message': 'No image provided'})
        file = request.files['image']
        if file.filename == '': return jsonify({'success': False, 'message': 'No image selected'})
        try:
            upload_result = cloudinary.uploader.upload(file, folder="restaurant")
            return jsonify({'success': True, 'url': upload_result['secure_url']})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    with app.app_context(): init_db()
    return app

# ✅ FIX 4: Fixed the fatal syntax error at the bottom
if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
