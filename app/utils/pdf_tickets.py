from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.textlabels import Label
import qrcode
import io
import base64
from datetime import datetime

def generate_tickets_pdf(booking):
    """Generate PDF with all tickets for a booking"""
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles with colors
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.red,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.darkred,
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=10,
        textColor=colors.darkblue
    )
    
    # Color scheme
    primary_color = colors.red
    secondary_color = colors.darkblue
    accent_color = colors.green
    
    # Get concert information
    from app.models import Settings
    import os
    concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
    concert_date = Settings.get_value('concert_date', '29/1 2026')
    concert_venue = Settings.get_value('concert_venue', 'Aulan på Rytmus Stockholm')
    
    # Get logo data from database if available
    logo_data = None
    qr_logo_data = Settings.get_value('qr_logo_data')
    qr_logo_content_type = Settings.get_value('qr_logo_content_type', 'image/jpeg')
    
    if qr_logo_data:
        import base64
        from PIL import Image as PILImage
        import io
        
        try:
            # Decode base64 data
            logo_bytes = base64.b64decode(qr_logo_data)
            logo_data = io.BytesIO(logo_bytes)
        except Exception as e:
            print(f"Error decoding logo data: {e}")
            logo_data = None
    
    # Build PDF content
    story = []
    
    # Header
    story.append(Paragraph(f"{concert_name}", title_style))
    story.append(Paragraph(f"{concert_date}", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Booking info
    booking_info = [
        ['Bokningsreferens:', booking.booking_reference],
        ['Namn:', booking.full_name],
        ['E-post:', booking.email],
        ['Telefon:', booking.phone],
        ['Föreställning:', f"{booking.show.start_time}-{booking.show.end_time}"],
        ['Plats:', concert_venue]
    ]
    
    booking_table = Table(booking_info, colWidths=[2*inch, 4*inch])
    booking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.darkblue),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(booking_table)
    story.append(Spacer(1, 30))
    
    # Generate tickets
    for i, ticket in enumerate(booking.tickets):
        # Page break for each ticket (except first)
        if i > 0:
            story.append(Spacer(1, 0.5*inch))
        
        # Ticket header with colors
        ticket_type = 'Ordinarie' if ticket.ticket_type == 'normal' else 'Student'
        story.append(Paragraph(f"<font color='{primary_color}'>Biljett {i+1} av {len(booking.tickets)}</font>", subtitle_style))
        story.append(Paragraph(f"<font color='{secondary_color}'>{ticket_type} Biljett - {ticket.ticket_reference}</font>", info_style))
        story.append(Spacer(1, 20))
        
        # Generate QR code with logo
        qr_code_data = generate_ticket_qr_code(ticket, logo_data)
        qr_buffer = io.BytesIO(base64.b64decode(qr_code_data))
        
        # Add QR code to PDF
        qr_image = Image(qr_buffer, width=2*inch, height=2*inch)
        story.append(qr_image)
        story.append(Spacer(1, 10))
        
        # Ticket details with colors
        story.append(Paragraph(f"<b><font color='{primary_color}'>Referens:</font></b> {ticket.ticket_reference}", info_style))
        story.append(Paragraph(f"<b><font color='{primary_color}'>Typ:</font></b> {ticket_type}", info_style))
        story.append(Paragraph(f"<b><font color='{primary_color}'>Datum:</font></b> {concert_date}", info_style))
        story.append(Paragraph(f"<b><font color='{primary_color}'>Tid:</font></b> {booking.show.start_time}-{booking.show.end_time}", info_style))
        story.append(Paragraph(f"<b><font color='{primary_color}'>Plats:</font></b> {concert_venue}", info_style))
        
        # Instructions with colors
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"<b><font color='{accent_color}'>Instruktioner:</font></b>", info_style))
        story.append(Paragraph(f"<font color='{secondary_color}'>• Visa denna QR-kod vid ingången</font>", info_style))
        story.append(Paragraph(f"<font color='{secondary_color}'>• Biljetten är personlig och kan inte överlämnas</font>", info_style))
        story.append(Paragraph(f"<font color='{secondary_color}'>• Ta med giltigt ID för verifiering</font>", info_style))
        
        # Page break after each ticket (except last)
        if i < len(booking.tickets) - 1:
            story.append(Spacer(1, 0.5*inch))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Genererat: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, 
                                       textColor=colors.grey, alignment=TA_CENTER)))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer.getvalue()

def generate_ticket_qr_code(ticket, logo_data=None):
    """Generate QR code for a specific ticket with optional logo"""
    import qrcode
    from PIL import Image as PILImage, ImageDraw
    import io
    import base64
    import os
    
    # Create QR code with higher error correction for logo embedding
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,
        border=4,
    )
    qr.add_data(ticket.ticket_reference)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Add logo if provided
    if logo_data:
        try:
            # Open logo from BytesIO
            logo = PILImage.open(logo_data)
            
            # Calculate logo size - smaller to avoid interfering with QR code
            qr_size = qr_img.size[0]
            logo_size = int(qr_size * 0.15)  # 15% of QR code size (smaller)
            
            # Resize logo maintaining aspect ratio
            logo.thumbnail((logo_size, logo_size), PILImage.Resampling.LANCZOS)
            
            # Convert logo to RGBA if it isn't already
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            
            # Create a semi-transparent white background for better visibility
            logo_bg_size = logo_size + 8  # Add small padding
            logo_bg = PILImage.new('RGBA', (logo_bg_size, logo_bg_size), (255, 255, 255, 200))  # Semi-transparent white
            
            # Create rounded rectangle mask for the background
            mask = PILImage.new('L', (logo_bg_size, logo_bg_size), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([0, 0, logo_bg_size, logo_bg_size], radius=4, fill=255)
            
            # Apply mask to create rounded background
            logo_bg.putalpha(mask)
            
            # Paste logo on semi-transparent background
            logo_x = (logo_bg_size - logo_size) // 2
            logo_y = (logo_bg_size - logo_size) // 2
            
            # Composite logo onto background preserving colors
            logo_bg.paste(logo, (logo_x, logo_y), logo)
            
            # Calculate position to center logo in QR code
            qr_width, qr_height = qr_img.size
            logo_width, logo_height = logo_bg.size
            
            x = (qr_width - logo_width) // 2
            y = (qr_height - logo_height) // 2
            
            # Convert QR code to RGBA for alpha blending
            qr_img = qr_img.convert('RGBA')
            
            # Paste logo onto QR code with alpha blending
            qr_img.paste(logo_bg, (x, y), logo_bg)
            
            # Convert back to RGB for final output
            qr_img = qr_img.convert('RGB')
            
        except Exception as e:
            print(f"Error adding logo to QR code: {e}")
            # Continue without logo if there's an error
    
    # Convert to base64
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return img_base64
