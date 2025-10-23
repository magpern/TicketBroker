import json
from datetime import datetime
from app.models import AuditLog, db

def log_audit_event(action_type, entity_type, entity_id, user_type, user_identifier, 
                   details=None, old_value=None, new_value=None):
    """Log an audit event to the database"""
    try:
        audit_entry = AuditLog(
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_type=user_type,
            user_identifier=user_identifier,
            details=json.dumps(details) if details else None,
            old_value=json.dumps(old_value) if old_value else None,
            new_value=json.dumps(new_value) if new_value else None
        )
        db.session.add(audit_entry)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Failed to log audit event: {e}")
        return False

def log_booking_created(booking):
    """Log when a booking is created"""
    details = {
        'booking_reference': booking.booking_reference,
        'show_time': f"{booking.show.start_time}-{booking.show.end_time}",
        'adult_tickets': booking.adult_tickets,
        'student_tickets': booking.student_tickets,
        'total_amount': booking.total_amount
    }
    return log_audit_event(
        action_type='booking_created',
        entity_type='booking',
        entity_id=booking.id,
        user_type='buyer',
        user_identifier=booking.phone,
        details=details
    )

def log_payment_initiated(booking):
    """Log when buyer initiates Swish payment"""
    details = {
        'booking_reference': booking.booking_reference,
        'amount': booking.total_amount,
        'initiated_at': booking.swish_payment_initiated_at.isoformat() if booking.swish_payment_initiated_at else None
    }
    return log_audit_event(
        action_type='payment_initiated',
        entity_type='booking',
        entity_id=booking.id,
        user_type='buyer',
        user_identifier=booking.phone,
        details=details
    )

def log_payment_confirmed(booking, admin_user):
    """Log when admin confirms payment"""
    details = {
        'booking_reference': booking.booking_reference,
        'amount': booking.total_amount,
        'confirmed_at': booking.confirmed_at.isoformat() if booking.confirmed_at else None
    }
    return log_audit_event(
        action_type='payment_confirmed',
        entity_type='booking',
        entity_id=booking.id,
        user_type='admin',
        user_identifier=admin_user,
        details=details
    )

def log_ticket_generated(ticket, booking):
    """Log when a ticket is generated"""
    details = {
        'ticket_reference': ticket.ticket_reference,
        'ticket_type': ticket.ticket_type,
        'booking_reference': booking.booking_reference
    }
    return log_audit_event(
        action_type='ticket_generated',
        entity_type='ticket',
        entity_id=ticket.id,
        user_type='admin',
        user_identifier='system',
        details=details
    )

def log_ticket_deleted(ticket, admin_user, reason=None):
    """Log when a ticket is deleted"""
    details = {
        'ticket_reference': ticket.ticket_reference,
        'ticket_type': ticket.ticket_type,
        'reason': reason
    }
    return log_audit_event(
        action_type='ticket_deleted',
        entity_type='ticket',
        entity_id=ticket.id,
        user_type='admin',
        user_identifier=admin_user,
        details=details
    )

def log_ticket_used(ticket, checker_user):
    """Log when a ticket is used/checked"""
    details = {
        'ticket_reference': ticket.ticket_reference,
        'used_at': ticket.used_at.isoformat() if ticket.used_at else None
    }
    return log_audit_event(
        action_type='ticket_used',
        entity_type='ticket',
        entity_id=ticket.id,
        user_type='admin',
        user_identifier=checker_user,
        details=details
    )

def log_settings_changed(key, old_value, new_value, admin_user):
    """Log when settings are changed"""
    return log_audit_event(
        action_type='settings_changed',
        entity_type='settings',
        entity_id=0,  # Settings don't have individual IDs
        user_type='admin',
        user_identifier=admin_user,
        details={'setting_key': key},
        old_value={'value': old_value},
        new_value={'value': new_value}
    )

def log_buyer_confirmed_payment(booking):
    """Log when buyer confirms they made payment"""
    details = {
        'booking_reference': booking.booking_reference,
        'amount': booking.total_amount
    }
    return log_audit_event(
        action_type='buyer_payment_confirmed',
        entity_type='booking',
        entity_id=booking.id,
        user_type='buyer',
        user_identifier=booking.phone,
        details=details
    )

def log_ticket_state_change(ticket, checker_user, action):
    """Log when a ticket state is changed (used/unused)"""
    details = {
        'ticket_reference': ticket.ticket_reference,
        'action': action,
        'new_state': 'used' if ticket.is_used else 'unused',
        'changed_at': ticket.used_at.isoformat() if ticket.used_at else None
    }
    return log_audit_event(
        action_type='ticket_state_changed',
        entity_type='ticket',
        entity_id=ticket.id,
        user_type='admin',
        user_identifier=checker_user,
        details=details
    )