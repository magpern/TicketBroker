from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize mail with default config first
    mail.init_app(app)
    
    # Configure mail settings from database after db is initialized
    with app.app_context():
        try:
            from app.models import Settings
            admin_email = Settings.get_value('admin_email', 'klasskonsertgruppen@gmail.com')
            app.config['MAIL_USERNAME'] = admin_email
            app.config['MAIL_DEFAULT_SENDER'] = admin_email
            # Reinitialize mail with database settings
            mail.init_app(app)
        except Exception as e:
            # If database is not ready, use default email
            app.config['MAIL_USERNAME'] = 'klasskonsertgruppen@gmail.com'
            app.config['MAIL_DEFAULT_SENDER'] = 'klasskonsertgruppen@gmail.com'
            mail.init_app(app)
    
    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Add template context processor for global variables
    @app.context_processor
    def inject_global_vars():
        from app.models import Settings
        contact_email = Settings.get_value('contact_email', 'oliver.ahlstrand@icloud.com')
        return dict(contact_email=contact_email)
    
    # Note: Database tables are now managed by Flask-Migrate
    # Run 'flask db upgrade' to apply migrations
    
    return app
