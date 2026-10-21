import logging
from flask import Blueprint, jsonify, request
from app.models import db, Reservation, ContactMessage

# Initialize a structured logger for cleaner system outputs
logger = logging.getLogger(__name__)

# Create the core application blueprint layer
core_bp = Blueprint('core', __name__)

@core_bp.route('/health', methods=['GET'])
def systems_health_heartbeat():
    """Provides a structural runtime verification endpoint for the system."""
    try:
        # Run a low-overhead query statement to verify live database connectivity
        db.session.execute(db.text('SELECT 1'))
        return jsonify({"status": "ok", "database_connectivity": True}), 200
    except Exception as err:
        logger.error(f"Systems check failed to reach database infrastructure: {str(err)}")
        return jsonify({"status": "unhealthy", "error_payload": str(err)}), 500

@core_bp.route('/api/book', methods=['POST'])
def handle_booking():
    """Processes online table reservations securely into the database."""
    data = request.json or {}
    try:
        new_booking = Reservation(
            customer_name=data.get('name'),
            customer_email=data.get('email'),
            party_size=int(data.get('size', 1)),
            booking_time=db.text(data.get('time'))  # Temporary wrapper for serialization compatibility
        )
        db.session.add(new_booking)
        db.session.commit()
        logger.info(f"Successfully processed new reservation for: {data.get('name')}")
        return jsonify({"status": "success", "message": "Reservation confirmed"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed processing booking transaction pipeline: {str(e)}")
        return jsonify({"status": "error", "message": "Internal processing failure"}), 500

