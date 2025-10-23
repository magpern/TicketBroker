from flask_mail import Message
from app import mail
from app.models import Settings
from flask import current_app

def send_booking_confirmation(booking):
    """Send confirmation email to buyer"""
    try:
        swish_number = Settings.get_value('swish_number', '070 123 45 67')
        concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
        
        # Generate payment link
        from flask import url_for
        payment_url = url_for('public.booking_success', booking_id=booking.id, _external=True)
        
        msg = Message(
            subject=f'Biljettreservation bekräftad - {booking.booking_reference}',
            recipients=[booking.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.html = f"""
        <h2>Tack för din reservation!</h2>
        <p>Hej {booking.first_name},</p>
        <p>Din biljettreservation för {concert_name} har bekräftats.</p>
        
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
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{payment_url}" style="background-color: #dc2626; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Betala nu</a>
        </div>
        
        <p>Eller klicka på denna länk för att komma till betalningssidan: <a href="{payment_url}">{payment_url}</a></p>
        
        <p>Glöm inte att bekräfta din betalning på hemsidan efter att du har swishat!</p>
        
        <p>Med vänliga hälsningar,<br>{concert_name}-gruppen</p>
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
    """Send confirmation email with QR codes when payment is confirmed by admin"""
    try:
        concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
        
        msg = Message(
            subject=f'Betalning bekräftad - {booking.booking_reference}',
            recipients=[booking.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Generate QR codes for each ticket
        qr_codes_html = ""
        if booking.tickets:
            qr_codes_html = "<h3>Dina biljetter med QR-koder:</h3>"
            for ticket in booking.tickets:
                ticket_type_text = "Ordinarie" if ticket.ticket_type == "normal" else "Student"
                
                # Generate QR code for ticket
                import qrcode
                import io
                import base64
                
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(ticket.ticket_reference)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                qr_codes_html += f"""
                <div style="border: 2px solid #dc2626; padding: 15px; margin: 10px 0; border-radius: 8px; text-align: center;">
                    <h4>{ticket.ticket_reference} - {ticket_type_text}</h4>
                    <img src="data:image/png;base64,{img_base64}" alt="QR Code for {ticket.ticket_reference}" style="max-width: 200px;">
                    <p><strong>Referens:</strong> {ticket.ticket_reference}</p>
                </div>
                """
        
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
        
        {qr_codes_html}
        
        <h3>Viktigt för konserten:</h3>
        <p>Ta med dig dina biljetter (QR-koder) till konserten. De kommer att skannas vid ingången.</p>
        <p>Du kan också visa biljetterna på din telefon från detta e-postmeddelande.</p>
        
        <p>Vi ses på konserten!</p>
        
        <p>Med vänliga hälsningar,<br>{concert_name}-gruppen</p>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send payment confirmation email: {e}")
        return False

def send_ticket_resend(booking):
    """Resend tickets to user (for lost tickets functionality)"""
    try:
        concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
        
        msg = Message(
            subject=f'Dina biljetter - {booking.booking_reference}',
            recipients=[booking.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Generate QR codes for each ticket
        qr_codes_html = ""
        if booking.tickets:
            qr_codes_html = "<h3>Dina biljetter med QR-koder:</h3>"
            for ticket in booking.tickets:
                ticket_type_text = "Ordinarie" if ticket.ticket_type == "normal" else "Student"
                
                # Generate QR code for ticket
                import qrcode
                import io
                import base64
                
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(ticket.ticket_reference)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                qr_codes_html += f"""
                <div style="border: 2px solid #dc2626; padding: 15px; margin: 10px 0; border-radius: 8px; text-align: center;">
                    <h4>{ticket.ticket_reference} - {ticket_type_text}</h4>
                    <img src="data:image/png;base64,{img_base64}" alt="QR Code for {ticket.ticket_reference}" style="max-width: 200px;">
                    <p><strong>Referens:</strong> {ticket.ticket_reference}</p>
                </div>
                """
        
        msg.html = f"""
        <h2>Dina biljetter</h2>
        <p>Hej {booking.first_name},</p>
        <p>Här är dina biljetter för {concert_name}.</p>
        
        <h3>Bokningsreferens: <strong>{booking.booking_reference}</strong></h3>
        
        <h3>Biljettdetaljer:</h3>
        <ul>
            <li><strong>Namn:</strong> {booking.full_name}</li>
            <li><strong>Tid:</strong> {booking.show.start_time}-{booking.show.end_time}</li>
            <li><strong>Ordinarie biljetter:</strong> {booking.adult_tickets} st</li>
            <li><strong>Studentbiljetter:</strong> {booking.student_tickets} st</li>
        </ul>
        
        {qr_codes_html}
        
        <h3>Viktigt för konserten:</h3>
        <p>Ta med dig dina biljetter (QR-koder) till konserten. De kommer att skannas vid ingången.</p>
        <p>Du kan också visa biljetterna på din telefon från detta e-postmeddelande.</p>
        
        <p>Vi ses på konserten!</p>
        
        <p>Med vänliga hälsningar,<br>{concert_name}-gruppen</p>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to resend tickets email: {e}")
        return False

def send_multiple_tickets_resend(bookings):
    """Resend tickets for multiple bookings in one email"""
    try:
        concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
        
        if not bookings:
            return False
            
        # Use the first booking for recipient info
        first_booking = bookings[0]
        
        msg = Message(
            subject=f'Dina biljetter - {len(bookings)} bokningar',
            recipients=[first_booking.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Generate QR codes for all tickets from all bookings
        all_tickets_html = ""
        total_tickets = 0
        
        for booking in bookings:
            if booking.tickets:
                booking_header = f"<h3>Bokning {booking.booking_reference} - {booking.show.start_time}-{booking.show.end_time}</h3>"
                all_tickets_html += booking_header
                
                for ticket in booking.tickets:
                    ticket_type_text = "Ordinarie" if ticket.ticket_type == "normal" else "Student"
                    total_tickets += 1
                    
                    # Generate QR code for ticket
                    import qrcode
                    import io
                    import base64
                    
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(ticket.ticket_reference)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)
                    img_base64 = base64.b64encode(buffer.getvalue()).decode()
                    
                    all_tickets_html += f"""
                    <div style="border: 2px solid #dc2626; padding: 15px; margin: 10px 0; border-radius: 8px; text-align: center;">
                        <h4>{ticket.ticket_reference} - {ticket_type_text}</h4>
                        <img src="data:image/png;base64,{img_base64}" alt="QR Code for {ticket.ticket_reference}" style="max-width: 200px;">
                        <p><strong>Referens:</strong> {ticket.ticket_reference}</p>
                    </div>
                    """
        
        msg.html = f"""
        <h2>Dina biljetter</h2>
        <p>Hej {first_booking.first_name},</p>
        <p>Här är alla dina biljetter för {concert_name} ({len(bookings)} bokningar, {total_tickets} biljetter totalt).</p>
        
        <h3>Bokningsöversikt:</h3>
        <ul>
        """
        
        for booking in bookings:
            msg.html += f"<li><strong>{booking.booking_reference}:</strong> {booking.show.start_time}-{booking.show.end_time} ({booking.total_tickets} biljetter)</li>"
        
        msg.html += f"""
        </ul>
        
        {all_tickets_html}
        
        <h3>Viktigt för konserten:</h3>
        <p>Ta med dig alla dina biljetter (QR-koder) till konserten. De kommer att skannas vid ingången.</p>
        <p>Du kan också visa biljetterna på din telefon från detta e-postmeddelande.</p>
        
        <p>Vi ses på konserten!</p>
        
        <p>Med vänliga hälsningar,<br>{concert_name}-gruppen</p>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to resend multiple tickets email: {e}")
        return False