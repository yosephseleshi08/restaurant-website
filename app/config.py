import os
from dotenv import load_dotenv

# Load local .env configuration parameters safely without exposure
load_dotenv()

class Config:
    """Centralizes application layout parameters and environments."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-default-secure-string-key')
    
    # Configure production database pipeline paths
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///restaurant.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Third-party digital merchant credentials and messaging tokens
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    
    # Administrative isolation safeguards
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

    @classmethod
    def verify_security_posture(cls):
        """Enforces administrative environment definitions in production."""
        if os.environ.get('FLASK_ENV') == 'production' and not cls.ADMIN_PASSWORD:
            raise ValueError(
                "CRITICAL RUNTIME EXCEPTION: "
                "The ADMIN_PASSWORD environment variable must be explicitly defined in production!"
            )
. 
