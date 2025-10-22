import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ticketbroker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    # Admin configuration
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'klasskonsert26'
    
    # App configuration
    MAX_TICKETS_PER_BOOKING = 4
    ADULT_TICKET_PRICE = 200
    STUDENT_TICKET_PRICE = 100
    SWISH_NUMBER = '070 123 45 67'
    CONCERT_DATE = '29/1 2026'
    CONCERT_VENUE = 'Aulan på Rytmus Stockholm'
