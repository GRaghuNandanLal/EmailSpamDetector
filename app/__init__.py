from flask import Flask
from config import Config
from app.models.detection_history import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()  # Create database tables

    from app.models.spam_detector import SpamDetector
    app.spam_detector = SpamDetector()

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app 