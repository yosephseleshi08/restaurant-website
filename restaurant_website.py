# restaurant_website.py - Clean Version

from flask import Flask, render_template, request, jsonify
import plotly.graph_objs as go
import plotly.utils
import json
import os
from datetime import datetime
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

DATA_FILE = 'restaurant_data.json'

DEFAULT_DATA = {
    'theme': {
        'primary_color': '#E85D3A',
        'secondary_color': '#F4A261',
        'background_color': '#FFF8F0',
        'text_color': '#2D1B12',
        'card_bg': '#FFFFFF',
        'accent_color': '#2A9D8F',
        'font_family': "'Georgia', serif"
    },
    'restaurant': {
        'name': 'La Bella Cucina',
        'tagline': 'Authentic Italian Dining Experience',
        'address': '123 Main Street, Foodville, FD 12345',
        'phone': '(555) 123-4567',
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
            'instagram': '@labellacucina',
            'facebook': 'LaBellaCucina',
            'twitter': '@LaBellaCucina'
        }
    },
    'menu': {
        'appetizers': [
            {'name': 'Bruschetta', 'description': 'Toasted bread with tomatoes', 'price': 12.99, 'popular': True},
            {'name': 'Calamari', 'description': 'Crispy fried calamari', 'price': 14.99, 'popular': False}
        ],
        'mains': [
            {'name': 'Spaghetti Carbonara', 'description': 'Classic pasta', 'price': 18.99, 'popular': True},
            {'name': 'Chicken Parmigiana', 'description': 'Breaded chicken', 'price': 22.99, 'popular': True}
        ],
        'desserts': [
            {'name': 'Tiramisu', 'description': 'Coffee-flavored dessert', 'price': 8.99, 'popular': True}
        ],
        'beverages': [
            {'name': 'Espresso', 'description': 'Rich Italian coffee', 'price': 4.99, 'popular': True}
        ]
    },
    'analytics': {
        'daily_sales': [1250, 1420, 1380, 1680, 2100, 2450, 1800],
        'monthly_revenue': [45000, 52000, 49000, 58000, 62000, 68000],
        'popular_items': ['Spaghetti Carbonara', 'Chicken Parmigiana', 'Margherita Pizza'],
        'customer_satisfaction': 4.8,
        'total_reservations': 156
    },
    'reservations': []
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

def generate_plotly_graph(graph_data, graph_type='bar', title=''):
    fig = go.Figure()
    theme = data['theme']
    
    if graph_type == 'bar':
        fig.add_trace(go.Bar(
            x=graph_data.get('x', []),
            y=graph_data.get('y', []),
            marker_color=theme['primary_color'],
            text=graph_data.get('y', []),
            textposition='auto',
        ))
    elif graph_type == 'line':
        fig.add_trace(go.Scatter(
            x=graph_data.get('x', []),
            y=graph_data.get('y', []),
            mode='lines+markers',
            line=dict(color=theme['primary_color'], width=3),
            marker=dict(size=10, color=theme['secondary_color'])
        ))
    elif graph_type == 'pie':
        fig.add_trace(go.Pie(
            labels=graph_data.get('labels', []),
            values=graph_data.get('values', []),
            hole=0.4,
            marker=dict(colors=[theme['primary_color'], theme['secondary_color'], theme['accent_color']])
        ))
    
    fig.update_layout(
        title=title,
        plot_bgcolor=theme['background_color'],
        paper_bgcolor=theme['card_bg'],
        font_color=theme['text_color'],
        font_family=theme['font_family']
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def home():
    return render_template('home.html', 
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         menu=data['menu'])

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
            'special_requests': request.form.get('special_requests'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        data['reservations'].append(reservation)
        data['analytics']['total_reservations'] += 1
        save_data(data)
        return render_template('reservations.html',
                             theme=data['theme'],
                             restaurant=data['restaurant'],
                             success=True)
    
    return render_template('reservations.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         success=False)

@app.route('/dashboard')
def dashboard():
    sales_data = {
        'x': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'y': data['analytics']['daily_sales']
    }
    sales_chart = generate_plotly_graph(sales_data, 'bar', 'Weekly Sales')
    
    revenue_data = {
        'x': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'y': data['analytics']['monthly_revenue']
    }
    revenue_chart = generate_plotly_graph(revenue_data, 'line', 'Monthly Revenue')
    
    popular_data = {
        'labels': data['analytics']['popular_items'],
        'values': [35, 28, 22]
    }
    popularity_chart = generate_plotly_graph(popular_data, 'pie', 'Popular Menu Items')
    
    return render_template('dashboard.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         sales_chart=sales_chart,
                         revenue_chart=revenue_chart,
                         popularity_chart=popularity_chart,
                         analytics=data['analytics'])

@app.route('/editor')
def editor():
    return render_template('editor.html',
                         theme=data['theme'],
                         restaurant=data['restaurant'],
                         menu=data['menu'],
                         analytics=data['analytics'])

@app.route('/api/update_theme', methods=['POST'])
def update_theme():
    theme_updates = request.json
    for key, value in theme_updates.items():
        if key in data['theme']:
            data['theme'][key] = value
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/update_restaurant', methods=['POST'])
def update_restaurant():
    updates = request.json
    for key, value in updates.items():
        if key in data['restaurant']:
            data['restaurant'][key] = value
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/update_hours', methods=['POST'])
def update_hours():
    hours = request.json
    data['restaurant']['hours'] = hours
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/update_social', methods=['POST'])
def update_social():
    social = request.json
    data['restaurant']['social'] = social
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/menu/add', methods=['POST'])
def add_menu_item():
    item_data = request.json
    category = item_data.get('category')
    item = {
        'name': item_data.get('name'),
        'description': item_data.get('description'),
        'price': float(item_data.get('price')),
        'popular': item_data.get('popular', False)
    }
    if category in data['menu']:
        data['menu'][category].append(item)
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Category not found'})

@app.route('/api/menu/delete', methods=['POST'])
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
def update_menu_item():
    item_data = request.json
    category = item_data.get('category')
    index = int(item_data.get('index'))
    if category in data['menu'] and 0 <= index < len(data['menu'][category]):
        data['menu'][category][index] = {
            'name': item_data.get('name'),
            'description': item_data.get('description'),
            'price': float(item_data.get('price')),
            'popular': item_data.get('popular', False)
        }
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/update_sales', methods=['POST'])
def update_sales():
    sales = request.json.get('sales', [])
    if len(sales) == 7:
        data['analytics']['daily_sales'] = sales
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/update_revenue', methods=['POST'])
def update_revenue():
    revenue = request.json.get('revenue', [])
    if len(revenue) == 6:
        data['analytics']['monthly_revenue'] = revenue
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/reset_data', methods=['POST'])
def reset_data():
    global data
    data = DEFAULT_DATA.copy()
    save_data(data)
    return jsonify({'success': True})

def create_templates():
    os.makedirs('templates', exist_ok=True)
    
    # Base template - completely clean
    base = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ restaurant.name }}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        :root {
            --primary: {{ theme.primary_color }};
            --secondary: {{ theme.secondary_color }};
            --background: {{ theme.background_color }};
            --text: {{ theme.text_color }};
            --card-bg: {{ theme.card_bg }};
            --accent: {{ theme.accent_color }};
            --font: {{ theme.font_family }};
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: var(--font);
            background: var(--background);
            color: var(--text);
            min-height: 100vh;
        }
        .navbar {
            background: var(--card-bg);
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .nav-brand {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary);
            text-decoration: none;
        }
        .nav-links {
            display: flex;
            gap: 1rem;
            list-style: none;
            flex-wrap: wrap;
        }
        .nav-links a {
            color: var(--text);
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 6px;
        }
        .nav-links a:hover {
            color: var(--primary);
            background: var(--background);
        }
        .nav-links a.editor-link {
            background: var(--primary);
            color: white;
        }
        .nav-links a.editor-link:hover {
            background: var(--secondary);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        .hero {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 4rem 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
        }
        .hero h1 { font-size: 3rem; margin-bottom: 1rem; }
        .hero p { font-size: 1.2rem; opacity: 0.9; }
        .card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 1.5rem;
        }
        .grid {
            display: grid;
            gap: 1.5rem;
        }
        .grid-2 { grid-template-columns: repeat(2, 1fr); }
        .grid-3 { grid-template-columns: repeat(3, 1fr); }
        .grid-4 { grid-template-columns: repeat(4, 1fr); }
        .grid-6 { grid-template-columns: repeat(6, 1fr); }
        .grid-7 { grid-template-columns: repeat(7, 1fr); }
        .btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            font-family: var(--font);
            display: inline-block;
            text-decoration: none;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(232, 93, 58, 0.4);
        }
        .btn-secondary { background: var(--secondary); }
        .menu-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            border-bottom: 1px solid #eee;
        }
        .menu-item:last-child { border-bottom: none; }
        .menu-item .price { color: var(--primary); font-weight: 700; font-size: 1.1rem; }
        .popular-badge {
            background: var(--secondary);
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            margin-left: 8px;
        }
        .form-group {
            margin-bottom: 1rem;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-family: var(--font);
        }
        .form-group input:focus {
            outline: none;
            border-color: var(--primary);
        }
        .form-group input[type="color"] {
            height: 50px;
            padding: 4px;
            cursor: pointer;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        .footer {
            background: var(--card-bg);
            padding: 2rem;
            text-align: center;
            margin-top: 2rem;
            border-top: 1px solid #eee;
        }
        @media (max-width: 768px) {
            .grid-2, .grid-3, .grid-4, .grid-6, .grid-7 {
                grid-template-columns: 1fr;
            }
            .hero h1 { font-size: 2rem; }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="/" class="nav-brand">{{ restaurant.name }}</a>
            <ul class="nav-links">
                <li><a href="/">Home</a></li>
                <li><a href="/menu">Menu</a></li>
                <li><a href="/reservations">Book</a></li>
                <li><a href="/dashboard">Stats</a></li>
                <li><a href="/editor" class="editor-link">Edit</a></li>
            </ul>
        </div>
    </nav>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    <footer class="footer">
        <p>&copy; 2024 {{ restaurant.name }}. All rights reserved.</p>
        <p>{{ restaurant.address }} | {{ restaurant.phone }}</p>
    </footer>
</body>
</html>"""

    # Home page
    home = """
{% extends "base.html" %}
{% block content %}
<div class="hero">
    <h1>Welcome to {{ restaurant.name }}</h1>
    <p>{{ restaurant.tagline }}</p>
    <br>
    <a href="/menu" class="btn">View Menu</a>
    <a href="/reservations" class="btn btn-secondary">Book a Table</a>
</div>
<div class="grid grid-2">
    <div class="card">
        <h2>Hours</h2>
        {% for day, hours in restaurant.hours.items() %}
        <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #eee;">
            <span>{{ day|capitalize }}</span>
            <span>{{ hours }}</span>
        </div>
        {% endfor %}
    </div>
    <div class="card">
        <h2>Featured</h2>
        {% for item in menu.appetizers[:2] %}
        <div class="menu-item">
            <div>
                <strong>{{ item.name }}</strong>
                {% if item.popular %}<span class="popular-badge">Popular</span>{% endif %}
                <p style="font-size: 0.9rem;">{{ item.description }}</p>
            </div>
            <span class="price">${{ "%.2f"|format(item.price) }}</span>
        </div>
        {% endfor %}
        <div style="text-align: center; margin-top: 1rem;">
            <a href="/menu" class="btn">Full Menu</a>
        </div>
    </div>
</div>
<div class="card" style="text-align: center;">
    <h2>Make a Reservation</h2>
    <p style="margin: 1rem 0;">Call: <strong>{{ restaurant.phone }}</strong></p>
    <a href="/reservations" class="btn">Book Online</a>
</div>
{% endblock %}"""

    # Menu page
    menu = """
{% extends "base.html" %}
{% block content %}
<h1 style="text-align: center; margin-bottom: 2rem;">Our Menu</h1>
<div class="grid grid-2">
    {% for category, items in menu.items() %}
    <div class="card">
        <h2>{{ category|capitalize }}</h2>
        {% for item in items %}
        <div class="menu-item">
            <div>
                <strong>{{ item.name }}</strong>
                {% if item.popular %}<span class="popular-badge">Popular</span>{% endif %}
                <p style="font-size: 0.9rem;">{{ item.description }}</p>
            </div>
            <span class="price">${{ "%.2f"|format(item.price) }}</span>
        </div>
        {% endfor %}
    </div>
    {% endfor %}
</div>
{% endblock %}"""

    # Reservations page
    reservations_page = """
{% extends "base.html" %}
{% block content %}
<h1 style="text-align: center; margin-bottom: 2rem;">Make a Reservation</h1>
{% if success %}
<div class="alert-success">Your reservation was successful!</div>
{% endif %}
<div class="grid grid-2">
    <div class="card">
        <h2>Information</h2>
        <ul style="list-style: none; padding: 0;">
            <li style="padding: 0.5rem 0;">We hold reservations for 15 minutes</li>
            <li style="padding: 0.5rem 0;">Parties of 8+ call directly</li>
            <li style="padding: 0.5rem 0;">Call: <strong>{{ restaurant.phone }}</strong></li>
        </ul>
    </div>
    <div class="card">
        <h2>Book Online</h2>
        <form method="POST">
            <div class="form-group">
                <label>Full Name *</label>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>Email *</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Phone *</label>
                <input type="tel" name="phone" required>
            </div>
            <div class="grid grid-2">
                <div class="form-group">
                    <label>Date *</label>
                    <input type="date" name="date" required>
                </div>
                <div class="form-group">
                    <label>Time *</label>
                    <select name="time" required>
                        <option value="17:00">5:00 PM</option>
                        <option value="18:00">6:00 PM</option>
                        <option value="19:00">7:00 PM</option>
                        <option value="20:00">8:00 PM</option>
                        <option value="21:00">9:00 PM</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label>Guests *</label>
                <select name="guests" required>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                    <option value="6">6</option>
                    <option value="7">7</option>
                    <option value="8">8+</option>
                </select>
            </div>
            <div class="form-group">
                <label>Special Requests</label>
                <textarea name="special_requests" rows="2"></textarea>
            </div>
            <button type="submit" class="btn" style="width:100%;">Make Reservation</button>
        </form>
    </div>
</div>
{% endblock %}"""

    # Dashboard page
    dashboard = """
{% extends "base.html" %}
{% block content %}
<h1 style="text-align: center; margin-bottom: 2rem;">Business Dashboard</h1>
<div class="grid grid-4">
    <div class="card" style="text-align: center;">
        <div style="font-size: 2.5rem; color: var(--primary); font-weight: 700;">${{ "{:,.0f}".format(analytics.monthly_revenue|sum) }}</div>
        <div>Total Revenue</div>
    </div>
    <div class="card" style="text-align: center;">
        <div style="font-size: 2.5rem; color: var(--secondary); font-weight: 700;">{{ analytics.total_reservations }}</div>
        <div>Reservations</div>
    </div>
    <div class="card" style="text-align: center;">
        <div style="font-size: 2.5rem; color: var(--accent); font-weight: 700;">{{ analytics.customer_satisfaction }}</div>
        <div>Customer Rating</div>
    </div>
    <div class="card" style="text-align: center;">
        <div style="font-size: 2.5rem; color: var(--primary); font-weight: 700;">{{ analytics.daily_sales|sum }}</div>
        <div>Weekly Sales</div>
    </div>
</div>
<div class="grid grid-2">
    <div class="card"><div id="salesChart" style="height: 400px;"></div></div>
    <div class="card"><div id="revenueChart" style="height: 400px;"></div></div>
</div>
<div class="card"><div id="popularityChart" style="height: 400px;"></div></div>
<script>
    const salesData = {{ sales_chart | safe }};
    Plotly.newPlot('salesChart', salesData.data, salesData.layout);
    const revenueData = {{ revenue_chart | safe }};
    Plotly.newPlot('revenueChart', revenueData.data, revenueData.layout);
    const popularityData = {{ popularity_chart | safe }};
    Plotly.newPlot('popularityChart', popularityData.data, popularityData.layout);
</script>
{% endblock %}"""

    # Editor page
    editor = """
{% extends "base.html" %}
{% block content %}
<h1 style="text-align: center; margin-bottom: 2rem;">Visual Editor</h1>

<div class="card">
    <h2>Theme Colors</h2>
    <div class="grid grid-4">
        <div class="form-group">
            <label>Primary</label>
            <input type="color" id="primaryColor" value="{{ theme.primary_color }}" onchange="updateTheme('primary_color', this.value)">
        </div>
        <div class="form-group">
            <label>Secondary</label>
            <input type="color" id="secondaryColor" value="{{ theme.secondary_color }}" onchange="updateTheme('secondary_color', this.value)">
        </div>
        <div class="form-group">
            <label>Background</label>
            <input type="color" id="bgColor" value="{{ theme.background_color }}" onchange="updateTheme('background_color', this.value)">
        </div>
        <div class="form-group">
            <label>Text</label>
            <input type="color" id="textColor" value="{{ theme.text_color }}" onchange="updateTheme('text_color', this.value)">
        </div>
        <div class="form-group">
            <label>Card BG</label>
            <input type="color" id="cardBg" value="{{ theme.card_bg }}" onchange="updateTheme('card_bg', this.value)">
        </div>
        <div class="form-group">
            <label>Accent</label>
            <input type="color" id="accentColor" value="{{ theme.accent_color }}" onchange="updateTheme('accent_color', this.value)">
        </div>
        <div class="form-group">
            <label>Font</label>
            <select id="fontFamily" onchange="updateTheme('font_family', this.value)">
                <option value="'Georgia', serif" {% if theme.font_family == "'Georgia', serif" %}selected{% endif %}>Georgia</option>
                <option value="Arial, sans-serif" {% if theme.font_family == "Arial, sans-serif" %}selected{% endif %}>Arial</option>
                <option value="'Times New Roman', serif" {% if theme.font_family == "'Times New Roman', serif" %}selected{% endif %}>Times New Roman</option>
                <option value="'Inter', sans-serif" {% if theme.font_family == "'Inter', sans-serif" %}selected{% endif %}>Inter</option>
            </select>
        </div>
        <div style="display: flex; align-items: flex-end;">
            <button class="btn" onclick="resetData()" style="background: #dc3545; width:100%;">Reset</button>
        </div>
    </div>
</div>

<div class="card">
    <h2>Restaurant Info</h2>
    <div class="grid grid-2">
        <div class="form-group">
            <label>Name</label>
            <input type="text" id="restaurantName" value="{{ restaurant.name }}" onchange="updateRestaurant('name', this.value)">
        </div>
        <div class="form-group">
            <label>Tagline</label>
            <input type="text" id="tagline" value="{{ restaurant.tagline }}" onchange="updateRestaurant('tagline', this.value)">
        </div>
        <div class="form-group">
            <label>Address</label>
            <input type="text" id="address" value="{{ restaurant.address }}" onchange="updateRestaurant('address', this.value)">
        </div>
        <div class="form-group">
            <label>Phone</label>
            <input type="text" id="phone" value="{{ restaurant.phone }}" onchange="updateRestaurant('phone', this.value)">
        </div>
        <div class="form-group">
            <label>Email</label>
            <input type="email" id="email" value="{{ restaurant.email }}" onchange="updateRestaurant('email', this.value)">
        </div>
        <div class="form-group">
            <label>Instagram</label>
            <input type="text" id="instagram" value="{{ restaurant.social.instagram }}" onchange="updateSocial('instagram', this.value)">
        </div>
        <div class="form-group">
            <label>Facebook</label>
            <input type="text" id="facebook" value="{{ restaurant.social.facebook }}" onchange="updateSocial('facebook', this.value)">
        </div>
        <div class="form-group">
            <label>Twitter</label>
            <input type="text" id="twitter" value="{{ restaurant.social.twitter }}" onchange="updateSocial('twitter', this.value)">
        </div>
    </div>
</div>

<div class="card">
    <h2>Hours</h2>
    <div class="grid grid-2">
        {% for day, hours in restaurant.hours.items() %}
        <div class="form-group">
            <label>{{ day|capitalize }}</label>
            <input type="text" value="{{ hours }}" onchange="updateHours('{{ day }}', this.value)">
        </div>
        {% endfor %}
    </div>
</div>

<div class="card">
    <h2>Menu</h2>
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <h4>Add Item</h4>
        <div class="grid grid-4">
            <input type="text" id="newItemName" placeholder="Name">
            <input type="text" id="newItemDesc" placeholder="Description">
            <input type="number" id="newItemPrice" placeholder="Price" step="0.01">
            <select id="newItemCategory">
                <option value="appetizers">Appetizers</option>
                <option value="mains">Mains</option>
                <option value="desserts">Desserts</option>
                <option value="beverages">Beverages</option>
            </select>
        </div>
        <button class="btn" onclick="addMenuItem()" style="margin-top:10px;">Add Item</button>
    </div>
    {% for category, items in menu.items() %}
    <div style="margin-top:1rem;">
        <h3>{{ category|capitalize }}</h3>
        {% for item in items %}
        <div class="menu-item" id="item-{{ category }}-{{ loop.index0 }}">
            <div style="flex:1;">
                <input type="text" value="{{ item.name }}" onchange="updateMenuItem('{{ category }}', {{ loop.index0 }}, 'name', this.value)" style="border:1px solid #ddd;padding:4px 8px;border-radius:4px;width:150px;">
                <input type="text" value="{{ item.description }}" onchange="updateMenuItem('{{ category }}', {{ loop.index0 }}, 'description', this.value)" style="border:1px solid #ddd;padding:4px 8px;border-radius:4px;width:250px;">
                <input type="number" value="{{ item.price }}" step="0.01" onchange="updateMenuItem('{{ category }}', {{ loop.index0 }}, 'price', this.value)" style="border:1px solid #ddd;padding:4px 8px;border-radius:4px;width:80px;">
                <label><input type="checkbox" {% if item.popular %}checked{% endif %} onchange="updateMenuItem('{{ category }}', {{ loop.index0 }}, 'popular', this.checked)"> Popular</label>
            </div>
            <button onclick="deleteMenuItem('{{ category }}', {{ loop.index0 }})" style="background:#dc3545;color:white;border:none;padding:4px 12px;border-radius:4px;cursor:pointer;">X</button>
        </div>
        {% endfor %}
    </div>
    {% endfor %}
</div>

<div class="card">
    <h2>Sales Data (7 Days)</h2>
    <div class="grid grid-7">
        {% for i in range(7) %}
        <div class="form-group">
            <label>{{ ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][i] }}</label>
            <input type="number" value="{{ analytics.daily_sales[i] }}" onchange="updateSales({{ i }}, this.value)">
        </div>
        {% endfor %}
    </div>
</div>

<div class="card">
    <h2>Revenue Data (6 Months)</h2>
    <div class="grid grid-6">
        {% for i in range(6) %}
        <div class="form-group">
            <label>{{ ['Jan','Feb','Mar','Apr','May','Jun'][i] }}</label>
            <input type="number" value="{{ analytics.monthly_revenue[i] }}" onchange="updateRevenue({{ i }}, this.value)">
        </div>
        {% endfor %}
    </div>
</div>

<div style="text-align:center;margin:2rem 0;">
    <a href="/" class="btn" style="font-size:1.2rem;padding:1rem 3rem;">View Website</a>
</div>

<script>
function updateTheme(key, value) {
    fetch('/api/update_theme', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({[key]: value})
    });
}

function updateRestaurant(key, value) {
    fetch('/api/update_restaurant', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({[key]: value})
    });
}

function updateHours(day, value) {
    fetch('/api/update_hours', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({[day]: value})
    });
}

function updateSocial(key, value) {
    fetch('/api/update_social', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({[key]: value})
    });
}

function addMenuItem() {
    const name = document.getElementById('newItemName').value;
    const description = document.getElementById('newItemDesc').value;
    const price = document.getElementById('newItemPrice').value;
    const category = document.getElementById('newItemCategory').value;
    if (!name || !price) { alert('Name and price required!'); return; }
    fetch('/api/menu/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({category, name, description, price, popular: false})
    }).then(() => location.reload());
}

function updateMenuItem(category, index, key, value) {
    const itemDiv = document.getElementById('item-' + category + '-' + index);
    const inputs = itemDiv.querySelectorAll('input');
    const item = {
        name: inputs[0].value,
        description: inputs[1].value,
        price: parseFloat(inputs[2].value),
        popular: inputs[3].checked
    };
    fetch('/api/menu/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({category, index, item})
    });
}

function deleteMenuItem(category, index) {
    if (!confirm('Delete?')) return;
    fetch('/api/menu/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({category, index})
    }).then(() => location.reload());
}

function updateSales(index, value) {
    const inputs = document.querySelectorAll('.grid-7 input');
    const sales = Array.from(inputs).map(i => parseInt(i.value) || 0);
    fetch('/api/update_sales', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({sales})
    });
}

function updateRevenue(index, value) {
    const inputs = document.querySelectorAll('.grid-6 input');
    const revenue = Array.from(inputs).map(i => parseInt(i.value) || 0);
    fetch('/api/update_revenue', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({revenue})
    });
}

function resetData() {
    if (!confirm('Reset all data?')) return;
    fetch('/api/reset_data', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    }).then(() => location.reload());
}
</script>
{% endblock %}"""

    # Write all templates
    templates = {
        'base.html': base,
        'home.html': home,
        'menu.html': menu,
        'reservations.html': reservations_page,
        'dashboard.html': dashboard,
        'editor.html': editor
    }
    
    for filename, content in templates.items():
        with open(os.path.join('templates', filename), 'w', encoding='utf-8') as f:
            f.write(content)

# Remove old templates folder if it exists
import shutil
if os.path.exists('templates'):
    shutil.rmtree('templates')

# Create fresh templates
create_templates()

if __name__ == '__main__':
    print("=" * 50)
    print("RESTAURANT WEBSITE BUILDER")
    print("=" * 50)
    print("Website: http://127.0.0.1:5000")
    print("Editor: http://127.0.0.1:5000/editor")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)