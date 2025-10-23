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
    """Send confirmation email with professional ticket-style QR codes when payment is confirmed by admin"""
    try:
        admin_email = _get_admin_email()
        concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
        concert_date = Settings.get_value('concert_date', '29/1 2026')
        concert_venue = Settings.get_value('concert_venue', 'Aulan på Rytmus Stockholm')
        
        msg = Message(
            subject=f'🎫 Dina biljetter är klara! - {booking.booking_reference}',
            recipients=[booking.email],
            sender=admin_email
        )
        
        # Generate professional ticket cards
        tickets_html = ""
        if booking.tickets:
            tickets_html = f"""
            <div style="margin: 30px 0;">
                <h2 style="color: #dc2626; text-align: center; margin-bottom: 30px;">🎫 Dina biljetter för {concert_name}</h2>
            """
            
            for ticket in booking.tickets:
                ticket_type_text = "Ordinarie" if ticket.ticket_type == "normal" else "Student"
                ticket_type_color = "#dc2626" if ticket.ticket_type == "normal" else "#059669"
                
                # Generate QR code for ticket
                import qrcode
                import io
                import base64
                
                qr = qrcode.QRCode(version=1, box_size=8, border=4)
                qr.add_data(ticket.ticket_reference)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                tickets_html += f"""
                <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); 
                            border: 3px solid {ticket_type_color}; 
                            border-radius: 20px; 
                            padding: 25px; 
                            margin: 20px 0; 
                            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                            position: relative;
                            overflow: hidden;">
                    
                    <!-- Ticket Header -->
                    <div style="background: {ticket_type_color}; 
                                color: white; 
                                padding: 15px; 
                                margin: -25px -25px 20px -25px; 
                                border-radius: 17px 17px 0 0;
                                text-align: center;">
                        <h3 style="margin: 0; font-size: 18px; font-weight: bold;">{concert_name}</h3>
                        <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">{concert_date}</p>
                    </div>
                    
                    <!-- Ticket Content -->
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <!-- QR Code -->
                        <div style="flex-shrink: 0;">
                            <img src="data:image/png;base64,{img_base64}" 
                                 alt="QR Code for {ticket.ticket_reference}" 
                                 style="width: 120px; height: 120px; border: 2px solid #e5e7eb; border-radius: 10px;">
                        </div>
                        
                        <!-- Ticket Details -->
                        <div style="flex: 1;">
                            <div style="margin-bottom: 15px;">
                                <h4 style="color: {ticket_type_color}; margin: 0 0 10px 0; font-size: 16px;">
                                    {ticket_type_text} Biljett
                                </h4>
                                <p style="margin: 0; font-size: 14px; color: #6b7280;">
                                    <strong>Referens:</strong> {ticket.ticket_reference}
                                </p>
                            </div>
                            
                            <div style="background: #f3f4f6; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                                <p style="margin: 0; font-size: 13px; color: #374151;">
                                    <strong>📍 Plats:</strong> {concert_venue}<br>
                                    <strong>🕐 Tid:</strong> {booking.show.start_time}-{booking.show.end_time}
                                </p>
                            </div>
                            
                            <div style="text-align: center; padding: 10px; background: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                                <p style="margin: 0; font-size: 12px; color: #92400e; font-weight: bold;">
                                    📱 Visa denna QR-kod vid ingången
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Ticket Footer -->
                    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e5e7eb; text-align: center;">
                        <p style="margin: 0; font-size: 11px; color: #9ca3af;">
                            Denna biljett är personlig och kan inte överlämnas till andra
                        </p>
                    </div>
                </div>
                """
            
            tickets_html += "</div>"
        
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dina biljetter - {concert_name}</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                     line-height: 1.6; color: #374151; background: #f9fafb; margin: 0; padding: 20px;">
            
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); 
                            color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px; font-weight: bold;">🎉 Betalning bekräftad!</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">
                        Dina biljetter är nu säkra och klara för konserten
                    </p>
                </div>
                
                <!-- Main Content -->
                <div style="padding: 30px;">
                    <div style="background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 10px; 
                                padding: 20px; margin-bottom: 30px;">
                        <h3 style="margin: 0 0 10px 0; color: #0369a1;">📋 Bokningsinformation</h3>
                        <p style="margin: 0; font-size: 14px;">
                            <strong>Bokningsreferens:</strong> {booking.booking_reference}<br>
                            <strong>Namn:</strong> {booking.full_name}<br>
                            <strong>E-post:</strong> {booking.email}<br>
                            <strong>Telefon:</strong> {booking.phone}
                        </p>
                    </div>
                    
                    {tickets_html}
                    
                    <!-- Important Instructions -->
                    <div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 10px; 
                                padding: 20px; margin-top: 30px;">
                        <h3 style="margin: 0 0 15px 0; color: #dc2626;">⚠️ Viktigt för konserten</h3>
                        <ul style="margin: 0; padding-left: 20px; font-size: 14px;">
                            <li>Ta med dig alla dina biljetter (QR-koder) till konserten</li>
                            <li>Biljetterna kommer att skannas vid ingången</li>
                            <li>Du kan visa biljetterna på din telefon från detta e-postmeddelande</li>
                            <li>Varje biljett är personlig och kan inte överlämnas till andra</li>
                            <li>Kom i tid - ingången stänger 15 minuter efter konsertens start</li>
                        </ul>
                    </div>
                    
                    <!-- Contact Info -->
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; 
                                border-top: 1px solid #e5e7eb;">
                        <p style="margin: 0; font-size: 14px; color: #6b7280;">
                            Har du frågor? Kontakta oss på <a href="mailto:{admin_email}" 
                            style="color: #dc2626; text-decoration: none;">{admin_email}</a>
                        </p>
                        <p style="margin: 10px 0 0 0; font-size: 12px; color: #9ca3af;">
                            Vi ses på konserten! 🎵
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send payment confirmation email: {e}")
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