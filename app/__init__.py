from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    mail.init_app(app)
    
    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Initialize default settings if they don't exist
        from app.models import Settings
        default_settings = [
            ('adult_price', '200'),
            ('student_price', '100'),
            ('swish_number', '070 123 45 67'),
            ('admin_email', 'oliver.ahlstrand@icloud.com'),
            ('concert_date', '29/1 2026'),
            ('concert_venue', 'Aulan på Rytmus Stockholm'),
            ('max_tickets_per_booking', '4')
        ]
        
        for key, value in default_settings:
            if not Settings.query.filter_by(key=key).first():
                setting = Settings(key=key, value=value)
                db.session.add(setting)
        
        db.session.commit()
    
    return app
