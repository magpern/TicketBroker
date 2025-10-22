from datetime import datetime
import random
import string
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
    booking_reference = db.Column(db.String(10), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    adult_tickets = db.Column(db.Integer, default=0)
    student_tickets = db.Column(db.Integer, default=0)
    total_amount = db.Column(db.Integer, nullable=False)  # Amount in SEK
    status = db.Column(db.String(20), default='reserved')  # 'reserved' or 'confirmed'
    buyer_confirmed_payment = db.Column(db.Boolean, default=False)
    swish_payment_initiated = db.Column(db.Boolean, default=False)
    swish_payment_initiated_at = db.Column(db.DateTime)
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
    
    @staticmethod
    def generate_booking_reference():
        """Generate a unique 5-character booking reference"""
        while True:
            # Generate 5-character alphanumeric string
            ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            # Check if it's already used
            if not Booking.query.filter_by(booking_reference=ref).first():
                return ref

class Buyer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='buyer', lazy=True)
    
    def __repr__(self):
        return f'<Buyer {self.first_name} {self.last_name} - {self.phone}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_reference = db.Column(db.String(20), unique=True, nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyer.id'), nullable=False)
    ticket_type = db.Column(db.String(10), nullable=False)  # 'normal' or 'student'
    ticket_number = db.Column(db.Integer, nullable=False)  # Sequential within booking (01, 02, etc.)
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime, nullable=True)
    checked_by = db.Column(db.String(50), nullable=True)  # Admin username who checked the ticket
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    booking = db.relationship('Booking', backref='tickets', lazy=True)
    show = db.relationship('Show', backref='tickets', lazy=True)
    
    def __repr__(self):
        return f'<Ticket {self.ticket_reference} - {self.ticket_type}>'
    
    @staticmethod
    def generate_ticket_reference(booking_ref, ticket_type, ticket_number):
        """Generate ticket reference like BOOKING_REF-N01 or BOOKING_REF-D01"""
        prefix = "N" if ticket_type == "normal" else "D"
        return f"{booking_ref}-{prefix}{ticket_number:02d}"

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    action_type = db.Column(db.String(50), nullable=False)  # booking_created, payment_initiated, etc.
    entity_type = db.Column(db.String(20), nullable=False)  # booking, ticket, payment
    entity_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # buyer, admin
    user_identifier = db.Column(db.String(50), nullable=False)  # Phone number or admin username
    details = db.Column(db.Text, nullable=True)  # JSON string for additional context
    old_value = db.Column(db.Text, nullable=True)  # JSON string for before state
    new_value = db.Column(db.Text, nullable=True)  # JSON string for after state
    
    def __repr__(self):
        return f'<AuditLog {self.action_type} - {self.entity_type}:{self.entity_id}>'

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
