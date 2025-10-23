from app.models import Ticket, Buyer, Booking, db
from app.utils.audit import log_ticket_generated
from datetime import datetime

def create_or_update_buyer(booking):
    """Create or update buyer record from booking"""
    buyer = Buyer.query.filter_by(phone=booking.phone).first()
    
    if buyer:
        # Update existing buyer
        buyer.first_name = booking.first_name
        buyer.last_name = booking.last_name
        buyer.email = booking.email
        buyer.updated_at = datetime.utcnow()
    else:
        # Create new buyer
        buyer = Buyer(
            phone=booking.phone,
            first_name=booking.first_name,
            last_name=booking.last_name,
            email=booking.email
        )
        db.session.add(buyer)
    
    db.session.commit()
    return buyer

def generate_tickets_for_booking(booking):
    """Generate individual tickets for a confirmed booking"""
    if booking.status != 'confirmed':
        raise ValueError("Can only generate tickets for confirmed bookings")
    
    # Create or update buyer
    buyer = create_or_update_buyer(booking)
    
    tickets = []
    ticket_number = 1
    
    # Generate normal tickets
    for i in range(booking.adult_tickets):
        ticket_ref = Ticket.generate_ticket_reference(
            booking.booking_reference, 
            "normal", 
            ticket_number
        )
        
        ticket = Ticket(
            ticket_reference=ticket_ref,
            booking_id=booking.id,
            show_id=booking.show_id,
            buyer_id=buyer.id,
            ticket_type="normal",
            ticket_number=ticket_number
        )
        
        db.session.add(ticket)
        tickets.append(ticket)
        
        ticket_number += 1
    
    # Generate student tickets
    for i in range(booking.student_tickets):
        ticket_ref = Ticket.generate_ticket_reference(
            booking.booking_reference, 
            "student", 
            ticket_number
        )
        
        ticket = Ticket(
            ticket_reference=ticket_ref,
            booking_id=booking.id,
            show_id=booking.show_id,
            buyer_id=buyer.id,
            ticket_type="student",
            ticket_number=ticket_number
        )
        
        db.session.add(ticket)
        tickets.append(ticket)
        
        ticket_number += 1
    
    db.session.commit()
    
    # Log ticket generation after commit (when tickets have IDs)
    for ticket in tickets:
        log_ticket_generated(ticket, booking)
    
    return tickets

def delete_ticket(ticket, admin_user, reason=None):
    """Delete a ticket and update counts"""
    if ticket.is_used:
        raise ValueError("Cannot delete used tickets")
    
    # Log the deletion before removing
    log_ticket_deleted(ticket, admin_user, reason)
    
    # Update booking counts
    booking = ticket.booking
    if ticket.ticket_type == "normal":
        booking.adult_tickets -= 1
    else:
        booking.student_tickets -= 1
    
    booking.total_amount = (booking.adult_tickets * 200) + (booking.student_tickets * 100)
    
    # Update show availability
    booking.show.update_availability()
    
    # Remove the ticket
    db.session.delete(ticket)
    db.session.commit()
    
    return True

def get_tickets_for_booking(booking):
    """Get all tickets for a booking"""
    return Ticket.query.filter_by(booking_id=booking.id).all()

def get_tickets_for_show(show):
    """Get all tickets for a show"""
    return Ticket.query.filter_by(show_id=show.id).all()

def mark_ticket_as_used(ticket, checker_user):
    """Mark a ticket as used"""
    if ticket.is_used:
        raise ValueError("Ticket is already used")
    
    ticket.is_used = True
    ticket.used_at = datetime.utcnow()
    ticket.checked_by = checker_user
    
    db.session.commit()
    
    # Log the usage
    log_ticket_used(ticket, checker_user)
    
    return True
