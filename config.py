import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ticketbroker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = None  # Will be set from database settings
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = None  # Will be set from database settings
    
    # Admin configuration
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    
    # App configuration
    MAX_TICKETS_PER_BOOKING = 4
    ADULT_TICKET_PRICE = 200
    STUDENT_TICKET_PRICE = 100
    SWISH_NUMBER = '012 345 67 89'
    SWISH_RECIPIENT_NAME = 'Event Organizer'
    CONTACT_EMAIL = 'admin@example.com'
    CONCERT_DATE = '29/1 2026'
    CONCERT_VENUE = 'Aulan på Rytmus Stockholm'
