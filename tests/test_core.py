import pytest
from app import create_app
from app.models import db

@pytest.fixture
def app_context():
    """Instantiates an isolated sandbox application context for validation."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def api_client(app_context):
    """Generates a test client runner to dispatch mock requests."""
    return app_context.test_client()

def test_health_endpoint_returns_success(api_client):
    """Asserts that the system health heartbeat path functions cleanly."""
    response = api_client.get('/health')
    assert response.status_code == 200
    assert response.json['database_connectivity'] is True

def test_booking_endpoint_ingests_valid_payload(api_client):
    """Asserts that table reservation data maps smoothly into storage."""
    payload = {
        "name": "Yoseph", 
        "email": "yoseph@test.com", 
        "size": 4, 
        "time": "2026-10-22 19:30:00"
    }
    response = api_client.post('/api/book', json=payload)
    assert response.status_code == 201
    assert b"Reservation confirmed" in response.data