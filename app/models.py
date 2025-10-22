from datetime import datetime
from app import db

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    total_tickets = db.Column(db.Integer, default=100)
    available_tickets = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    bookings = db.relationship('Booking', backref='show', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Show {self.start_time}-{self.end_time}>'
    
    @property
    def is_sold_out(self):
        return self.available_tickets <= 0
    
    def update_availability(self):
        """Update available tickets count based on confirmed bookings"""
        confirmed_bookings = Booking.query.filter_by(show_id=self.id, status='confirmed').all()
        total_booked = sum(booking.adult_tickets + booking.student_tickets for booking in confirmed_bookings)
        self.available_tickets = max(0, self.total_tickets - total_booked)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    adult_tickets = db.Column(db.Integer, default=0)
    student_tickets = db.Column(db.Integer, default=0)
    total_amount = db.Column(db.Integer, nullable=False)  # Amount in SEK
    status = db.Column(db.String(20), default='reserved')  # 'reserved' or 'confirmed'
    buyer_confirmed_payment = db.Column(db.Boolean, default=False)
    gdpr_consent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Booking {self.first_name} {self.last_name} - {self.show.start_time}>'
    
    @property
    def total_tickets(self):
        return self.adult_tickets + self.student_tickets
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Setting {self.key}: {self.value}>'
    
    @staticmethod
    def get_value(key, default=None):
        setting = Settings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set_value(key, value):
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Settings(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
        return setting
