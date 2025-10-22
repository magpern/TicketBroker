from flask_mail import Message
from app import mail
from app.models import Settings
from flask import current_app

def send_booking_confirmation(booking):
    """Send confirmation email to buyer"""
    try:
        swish_number = Settings.get_value('swish_number', '070 123 45 67')
        
        msg = Message(
            subject=f'Biljettreservation bekräftad - {booking.booking_reference}',
            recipients=[booking.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.html = f"""
        <h2>Tack för din reservation!</h2>
        <p>Hej {booking.first_name},</p>
        <p>Din biljettreservation för Klasskonsert 24C har bekräftats.</p>
        
        <h3>Din bokningsreferens: <strong>{booking.booking_reference}</strong></h3>
        
        <h3>Reservationsdetaljer:</h3>
        <ul>
            <li><strong>Namn:</strong> {booking.full_name}</li>
            <li><strong>E-post:</strong> {booking.email}</li>
            <li><strong>Telefon:</strong> {booking.phone}</li>
            <li><strong>Tid:</strong> {booking.show.start_time}-{booking.show.end_time}</li>
            <li><strong>Ordinarie biljetter:</strong> {booking.adult_tickets} st</li>
            <li><strong>Studentbiljetter:</strong> {booking.student_tickets} st</li>
            <li><strong>Totalt att betala:</strong> {booking.total_amount} kr</li>
        </ul>
        
        <h3>Viktigt - Betalning krävs!</h3>
        <p>Du har reserverat en plats först när du BÅDE har reserverat en biljett här på hemsidan - och du har swishat summan till <strong>{swish_number}</strong>.</p>
        
        <p>Glöm inte att bekräfta din betalning på hemsidan efter att du har swishat!</p>
        
        <p>Med vänliga hälsningar,<br>Klasskonsertgruppen</p>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send booking confirmation email: {e}")
        return False

def send_admin_notification(booking):
    """Send notification to admin about new booking"""
    try:
        admin_email = Settings.get_value('admin_email', 'oliver.ahlstrand@icloud.com')
        
        msg = Message(
            subject=f'Ny biljettreservation - {booking.booking_reference}',
            recipients=[admin_email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.html = f"""
        <h2>Ny biljettreservation</h2>
        <p>En ny biljettreservation har gjorts:</p>
        
        <h3>Bokningsreferens: <strong>{booking.booking_reference}</strong></h3>
        
        <h3>Reservationsdetaljer:</h3>
        <ul>
            <li><strong>Namn:</strong> {booking.full_name}</li>
            <li><strong>E-post:</strong> {booking.email}</li>
            <li><strong>Telefon:</strong> {booking.phone}</li>
            <li><strong>Tid:</strong> {booking.show.start_time}-{booking.show.end_time}</li>
            <li><strong>Ordinarie biljetter:</strong> {booking.adult_tickets} st</li>
            <li><strong>Studentbiljetter:</strong> {booking.student_tickets} st</li>
            <li><strong>Totalt att betala:</strong> {booking.total_amount} kr</li>
            <li><strong>Status:</strong> {'Betalning bekräftad av köpare' if booking.buyer_confirmed_payment else 'Väntar på betalning'}</li>
            {f'<li><strong>Swish initierad:</strong> {booking.swish_payment_initiated_at.strftime("%Y-%m-%d %H:%M")}</li>' if booking.swish_payment_initiated and booking.swish_payment_initiated_at else ''}
        </ul>
        
        <p>Logga in på adminpanelen för att hantera reservationen.</p>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send admin notification email: {e}")
        return False

def send_payment_confirmed(booking):
    """Send confirmation email when payment is confirmed by admin"""
    try:
        msg = Message(
            subject=f'Betalning bekräftad - {booking.booking_reference}',
            recipients=[booking.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Generate ticket list HTML
        ticket_list_html = ""
        if booking.tickets:
            ticket_list_html = "<h3>Dina biljettreferenser:</h3><ul>"
            for ticket in booking.tickets:
                ticket_type_text = "Ordinarie" if ticket.ticket_type == "normal" else "Student"
                ticket_list_html += f"<li><strong>{ticket.ticket_reference}</strong> - {ticket_type_text}</li>"
            ticket_list_html += "</ul>"
        
        msg.html = f"""
        <h2>Betalning bekräftad!</h2>
        <p>Hej {booking.first_name},</p>
        <p>Din betalning har bekräftats och dina biljetter är nu säkra!</p>
        
        <h3>Bokningsreferens: <strong>{booking.booking_reference}</strong></h3>
        
        <h3>Biljettdetaljer:</h3>
        <ul>
            <li><strong>Namn:</strong> {booking.full_name}</li>
            <li><strong>Tid:</strong> {booking.show.start_time}-{booking.show.end_time}</li>
            <li><strong>Ordinarie biljetter:</strong> {booking.adult_tickets} st</li>
            <li><strong>Studentbiljetter:</strong> {booking.student_tickets} st</li>
        </ul>
        
        {ticket_list_html}
        
        <h3>Viktigt för konserten:</h3>
        <p>Ta med dig dina biljettreferenser till konserten. De kommer att kontrolleras vid ingången.</p>
        
        <p>Vi ses på konserten!</p>
        
        <p>Med vänliga hälsningar,<br>Klasskonsertgruppen</p>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send payment confirmation email: {e}")
        return False
