# Restaurant CMS Pro v2.0 — Production Edition

A complete, white-label restaurant management platform with online ordering, kitchen display, table management, CRM, loyalty, gift cards, reservations, and an admin dashboard.

## What's Included

### Customer-Facing
- **Beautiful responsive website** — Mobile-first, PWA-ready, dark mode support
- **Online menu** with dietary filters and direct ordering
- **Reservations** with real-time capacity management
- **Gift cards** — Digital, email-delivered, balance tracking
- **Loyalty program** — Points, enrollment, profile lookup
- **Waitlist** with SMS notifications
- **QR table ordering** — Guests order from their phones
- **Gallery, Events, About, Contact** pages
- **Embeddable reservation widget**

### Admin & Operations
- **Real-time kitchen display** — Auto-refreshing order feed
- **Table management** — Drag-and-drop floor plan
- **Order management** — Status workflow, CSV export
- **Reservation management** — Status updates, capacity guard
- **Customer CRM** — Lifetime spend, visits, orders, preferences
- **Message inbox** — Reply, archive, export
- **Staff management** — Role-based access (admin/manager/staff)
- **Analytics dashboard** — Chart.js visualizations
- **Visual editor** — Real-time theme, menu, content editing
- **Audit logging** — Every action tracked
- **Webhook system** — Integrate with external tools
- **Data backup/restore** — JSON export/import

### Security & DevOps
- XSS sanitization, input validation, bcrypt hashing
- Rate limiting with Redis fallback
- Docker + Docker Compose + Nginx ready
- Health check endpoint
- pytest test suite

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python restaurant_website_pro.py

# 3. Open browser
# http://localhost:5000
# Admin: admin / admin123
```

## Docker Deployment

```bash
# Build and run with full stack (app + postgres + redis + nginx)
docker-compose up --build

# Or run just the app
docker build -t restaurant-cms .
docker run -p 5000:5000 restaurant-cms
```

## Environment Variables

```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/restaurant
REDIS_URL=redis://localhost:6379
SENDGRID_API_KEY=SG.xxxxx
FROM_EMAIL=noreply@yourdomain.com
NOTIFICATION_EMAIL=owner@restaurant.com
TWILIO_SID=ACxxxxx
TWILIO_TOKEN=xxxxx
TWILIO_PHONE=+15551234567
CLOUDINARY_CLOUD_NAME=yourcloud
CLOUDINARY_API_KEY=xxxxx
CLOUDINARY_API_SECRET=xxxxx
SESSION_COOKIE_SECURE=true
```

## File Structure

```
├── restaurant_website_pro.py   # Main Flask app
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container build
├── docker-compose.yml          # Full stack orchestration
├── nginx.conf                  # Reverse proxy config
├── static/
│   ├── sw.js                   # Service worker for PWA
│   └── icon.svg                # App icon
├── templates/
│   ├── base.html               # Layout + navigation
│   ├── home.html               # Landing page
│   ├── menu.html               # Menu page
│   ├── order.html              # Online ordering landing
│   ├── orders.html             # Menu ordering interface
│   ├── cart.html               # Shopping cart
│   ├── checkout.html           # Checkout
│   ├── gift_cards.html         # Gift card purchase
│   ├── loyalty.html            # Rewards enrollment
│   ├── reservations.html       # Book a table
│   ├── waitlist.html           # Join waitlist
│   ├── table_order.html        # QR table ordering
│   ├── about.html              # About / story
│   ├── contact.html            # Contact form
│   ├── gallery.html            # Photo gallery
│   ├── events.html             # Events & private dining
│   ├── widget_reservation.html # Embeddable widget
│   ├── login.html              # Admin login
│   ├── dashboard.html          # Analytics dashboard
│   ├── editor.html             # Visual editor
│   ├── admin_settings.html     # Settings + exports
│   ├── kitchen.html            # Kitchen display
│   ├── orders_admin.html       # Manage orders
│   ├── reservations_admin.html # Manage reservations
│   ├── tables_admin.html       # Table floor plan
│   ├── waitlist_admin.html     # Waitlist queue
│   ├── customers_admin.html    # Customer CRM
│   ├── customer_detail.html    # Customer profile
│   ├── staff.html              # Team management
│   ├── messages.html           # Message inbox
│   └── change_password.html    # Password change
├── test_app_fixed.py           # pytest suite
└── PITCH_DECK.md               # Sales deck
```

## Tests

```bash
pytest test_app_fixed.py -v
```

## License

This is your product. Sell it, white-label it, deploy it. Built to be sold.
