from flask_mail import Message
from app import mail
from app.models import Settings
from flask import current_app

def _get_admin_email():
    """Get admin email from settings"""
    return Settings.get_value('admin_email', 'klasskonsertgruppen@gmail.com')

def send_booking_confirmation(booking):
    """Send confirmation email to buyer"""
    try:
        admin_email = _get_admin_email()
        swish_number = Settings.get_value('swish_number', '070 123 45 67')
        concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
        
        # Generate payment link
        from flask import url_for
        payment_url = url_for('public.booking_success', booking_reference=booking.booking_reference, email=booking.email, _external=True)
        
        msg = Message(
            subject=f'Biljettreservation bekräftad - {booking.booking_reference}',
            recipients=[booking.email],
            sender=admin_email
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
        
        <div style="background-color: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 0; font-weight: 500; color: #1e40af;"><strong>OBS:</strong> Om du redan betalat så behöver du inte betala igen, utan avvakta bekräftelse från arrangören.</p>
        </div>
        
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
        admin_email = _get_admin_email()
        admin_email = Settings.get_value('admin_email', 'oliver.ahlstrand@icloud.com')
        
        msg = Message(
            subject=f'Ny biljettreservation - {booking.booking_reference}',
            recipients=[admin_email],
            sender=admin_email
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
    """Send payment confirmed email with PDF tickets attached"""
    try:
        from flask_mail import Message
        from app import mail
        from app.models import Settings
        from app.utils.pdf_tickets import generate_tickets_pdf
        
        # Get concert information
        concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
        concert_date = Settings.get_value('concert_date', '29/1 2026')
        concert_venue = Settings.get_value('concert_venue', 'Aulan på Rytmus Stockholm')
        
        # Generate PDF with all tickets
        pdf_data = generate_tickets_pdf(booking)
        
        # Create email message
        msg = Message(
            subject=f'Ticket Confirmation - {concert_name} ({booking.booking_reference})',
            recipients=[booking.email],
            sender=Settings.get_value('admin_email', 'klasskonsertgruppen@gmail.com')
        )
        
        # Email body - Professional design
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ticket Confirmation - {concert_name}</title>
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                     line-height: 1.6; color: #333333; background: #f8f9fa; margin: 0; padding: 0;">
            
            <div style="max-width: 600px; margin: 0 auto; background: white; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Professional Header -->
                <div style="background: #2c3e50; color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px; font-weight: 300; letter-spacing: 1px;">
                        TICKET CONFIRMATION
                    </h1>
                    <p style="margin: 8px 0 0 0; font-size: 14px; opacity: 0.9; font-weight: 300;">
                        {concert_name} • {concert_date}
                    </p>
                </div>
                
                <!-- Main Content -->
                <div style="padding: 40px 30px;">
                    
                    <!-- Confirmation Message -->
                    <div style="text-align: center; margin-bottom: 40px;">
                        <h2 style="margin: 0 0 15px 0; font-size: 20px; color: #27ae60; font-weight: 400;">
                            Payment Confirmed
                        </h2>
                        <p style="margin: 0; font-size: 16px; color: #666; font-weight: 300;">
                            Your tickets have been successfully processed and are ready for the event.
                        </p>
                    </div>
                    
                    <!-- Booking Details -->
                    <div style="background: #f8f9fa; border-left: 4px solid #3498db; padding: 25px; margin-bottom: 30px;">
                        <h3 style="margin: 0 0 20px 0; font-size: 16px; color: #2c3e50; font-weight: 500;">
                            BOOKING DETAILS
                        </h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #555; width: 140px;">Booking Reference:</td>
                                <td style="padding: 8px 0; color: #333; font-family: monospace; font-size: 14px;">{booking.booking_reference}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #555;">Name:</td>
                                <td style="padding: 8px 0; color: #333;">{booking.full_name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #555;">Email:</td>
                                <td style="padding: 8px 0; color: #333;">{booking.email}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #555;">Phone:</td>
                                <td style="padding: 8px 0; color: #333;">{booking.phone}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #555;">Tickets:</td>
                                <td style="padding: 8px 0; color: #333;">{len(booking.tickets)} tickets</td>
                            </tr>
                        </table>
                    </div>
                    
                    <!-- Ticket Information -->
                    <div style="background: #e8f5e8; border: 1px solid #27ae60; padding: 25px; margin-bottom: 30px;">
                        <h3 style="margin: 0 0 15px 0; font-size: 16px; color: #27ae60; font-weight: 500;">
                            YOUR TICKETS
                        </h3>
                        <p style="margin: 0; font-size: 14px; color: #555;">
                            Your tickets are attached to this email as a PDF document. Each ticket contains a unique QR code for entry.
                        </p>
                    </div>
                    
                    <!-- Event Information -->
                    <div style="background: #f8f9fa; padding: 25px; margin-bottom: 30px;">
                        <h3 style="margin: 0 0 20px 0; font-size: 16px; color: #2c3e50; font-weight: 500;">
                            EVENT INFORMATION
                        </h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #555; width: 80px;">Date:</td>
                                <td style="padding: 8px 0; color: #333;">{concert_date}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #555;">Time:</td>
                                <td style="padding: 8px 0; color: #333;">{booking.show.start_time} - {booking.show.end_time}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #555;">Venue:</td>
                                <td style="padding: 8px 0; color: #333;">{concert_venue}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <!-- Instructions -->
                    <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 25px; margin-bottom: 30px;">
                        <h3 style="margin: 0 0 15px 0; font-size: 16px; color: #856404; font-weight: 500;">
                            IMPORTANT INSTRUCTIONS
                        </h3>
                        <ul style="margin: 0; padding-left: 20px; color: #856404;">
                            <li style="margin-bottom: 8px; font-size: 14px;">Present your QR code at the entrance for scanning</li>
                            <li style="margin-bottom: 8px; font-size: 14px;">Bring valid photo identification for verification</li>
                            <li style="margin-bottom: 8px; font-size: 14px;">Arrive 15 minutes before the event start time</li>
                            <li style="margin-bottom: 8px; font-size: 14px;">Each ticket is valid for one person only</li>
                        </ul>
                    </div>
                    
                </div>
                
                <!-- Professional Footer -->
                <div style="background: #34495e; color: white; padding: 25px; text-align: center;">
                    <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: 300;">
                        Questions? Contact us at {Settings.get_value('contact_email', 'oliver.ahlstrand@icloud.com')}
                    </p>
                    <p style="margin: 0; font-size: 12px; opacity: 0.8; font-weight: 300;">
                        This is an automated message. Please do not reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach PDF
        msg.attach(
            filename=f"biljetter_{booking.booking_reference}.pdf",
            content_type="application/pdf",
            data=pdf_data
        )
        
        # Send email
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending payment confirmed email: {str(e)}")
        return False

def send_ticket_resend(booking):
    """Resend tickets to user (for lost tickets functionality)"""
    try:
        admin_email = _get_admin_email()
        concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
        
        msg = Message(
            subject=f'Dina biljetter - {booking.booking_reference}',
            recipients=[booking.email],
            sender=admin_email
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
        admin_email = _get_admin_email()
        concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
        
        if not bookings:
            return False

        # Use the first booking for recipient info
        first_booking = bookings[0]
        
        msg = Message(
            subject=f'Dina biljetter - {len(bookings)} bokningar',
            recipients=[first_booking.email],
            sender=admin_email
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

def send_contact_message(name, email, phone, subject, message):
    """Send contact form message to admin"""
    try:
        admin_email = _get_admin_email()
        concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
        
        msg = Message(
            subject=f'Kontaktformulär: {subject} - {concert_name}',
            recipients=[admin_email],
            sender=admin_email
        )
        
        phone_info = f"<li><strong>Telefon:</strong> {phone}</li>" if phone else ""
        
        msg.html = f"""
        <h2>Nytt meddelande från kontaktformuläret</h2>
        <p>Du har fått ett nytt meddelande från {concert_name} kontaktformulär.</p>
        
        <h3>Avsändaruppgifter:</h3>
        <ul>
            <li><strong>Namn:</strong> {name}</li>
            <li><strong>E-post:</strong> {email}</li>
            {phone_info}
            <li><strong>Ämne:</strong> {subject}</li>
        </ul>
        
        <h3>Meddelande:</h3>
        <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; border-left: 4px solid #dc2626;">
            {message.replace(chr(10), '<br>')}
        </div>
        
        <hr style="margin: 30px 0;">
        
        <p><strong>Svara direkt på detta e-postmeddelande för att svara till {name}.</strong></p>
        
        <p>Meddelandet skickades från: {concert_name} kontaktformulär</p>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send contact message: {e}")
        return False