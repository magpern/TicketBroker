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
    
    try:
        print(f"Starting PDF generation for booking {booking.booking_reference}")
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles inspired by Rytmus aesthetic
        title_style = ParagraphStyle(
            'ConcertTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1e40af'),  # Rytmus blue
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'ConcertSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#374151'),  # Dark gray
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica'
        )
        
        # Color scheme inspired by Rytmus
        primary_blue = colors.HexColor('#1e40af')  # Rytmus blue
        secondary_gray = colors.HexColor('#374151')  # Dark gray
        accent_green = colors.HexColor('#059669')  # Success green
        light_gray = colors.HexColor('#f3f4f6')  # Light background
        
        # Get concert information
        from app.models import Settings
        import os
        concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
        concert_date = Settings.get_value('concert_date', '29/1 2026')
        concert_venue = Settings.get_value('concert_venue', 'Aulan på Rytmus Stockholm')
        
        print(f"Concert info: {concert_name}, {concert_date}, {concert_venue}")
        
        # Get logo data from database if available
        logo_data = None
        qr_logo_data = Settings.get_value('qr_logo_data')
        qr_logo_content_type = Settings.get_value('qr_logo_content_type', 'image/jpeg')
        
        if qr_logo_data:
            import base64
            from PIL import Image as PILImage
            
            try:
                # Decode base64 data
                logo_bytes = base64.b64decode(qr_logo_data)
                logo_data = io.BytesIO(logo_bytes)
                print("Logo data loaded successfully")
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
            ('BACKGROUND', (0, 0), (0, -1), light_gray),
            ('TEXTCOLOR', (0, 0), (0, -1), secondary_gray),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, primary_blue),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, light_gray])
        ]))
        
        story.append(booking_table)
        story.append(Spacer(1, 30))
        
        print(f"Generating {len(booking.tickets)} tickets")
        
        # Generate tickets
        for i, ticket in enumerate(booking.tickets):
            # Page break for each ticket (except first)
            if i > 0:
                story.append(Spacer(1, 0.5*inch))
            
            print(f"Creating ticket {i+1}/{len(booking.tickets)}: {ticket.ticket_reference}")
            
            # Create ticket-like design
            ticket_data = create_ticket_design(ticket, booking, concert_name, concert_date, concert_venue, logo_data, i+1, len(booking.tickets))
            story.extend(ticket_data)
            
            # Page break after each ticket (except last)
            if i < len(booking.tickets) - 1:
                story.append(Spacer(1, 0.5*inch))
        
        print("Building PDF document")
        doc.build(story)
        buffer.seek(0)
        
        pdf_data = buffer.getvalue()
        print(f"PDF generated successfully, size: {len(pdf_data)} bytes")
        
        return pdf_data
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e

def create_ticket_design(ticket, booking, concert_name, concert_date, concert_venue, logo_data, ticket_num, total_tickets):
    """Create a single ticket design"""
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle, Spacer
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph, Image
    import io
    import base64
    
    # Generate QR code with logo
    qr_code_data = generate_ticket_qr_code(ticket, logo_data)
    qr_buffer = io.BytesIO(base64.b64decode(qr_code_data))
    
    # Ticket dimensions
    ticket_width = 6*inch
    ticket_height = 3*inch
    
    # Create ticket table structure
    ticket_type = 'Ordinarie' if ticket.ticket_type == 'normal' else 'Student'
    
    # Main ticket content
    ticket_content = [
        # Header row
        [
            Paragraph(f"<b><font color='#1e40af'>{concert_name}</font></b>", 
                     ParagraphStyle('TicketTitle', fontSize=16, alignment=TA_CENTER, fontName='Helvetica-Bold')),
            "",
            Paragraph(f"<b><font color='#1e40af'>BILJETT {ticket_num}/{total_tickets}</font></b>", 
                     ParagraphStyle('TicketNumber', fontSize=12, alignment=TA_CENTER, fontName='Helvetica-Bold'))
        ],
        # Date and venue row
        [
            Paragraph(f"<font color='#374151'>{concert_date}</font>", 
                     ParagraphStyle('TicketDate', fontSize=12, alignment=TA_LEFT, fontName='Helvetica')),
            "",
            Paragraph(f"<font color='#374151'>{concert_venue}</font>", 
                     ParagraphStyle('TicketVenue', fontSize=10, alignment=TA_CENTER, fontName='Helvetica'))
        ],
        # Time and type row
        [
            Paragraph(f"<b><font color='#059669'>{booking.show.start_time}-{booking.show.end_time}</font></b>", 
                     ParagraphStyle('TicketTime', fontSize=14, alignment=TA_LEFT, fontName='Helvetica-Bold')),
            "",
            Paragraph(f"<b><font color='#1e40af'>{ticket_type}</font></b>", 
                     ParagraphStyle('TicketType', fontSize=12, alignment=TA_CENTER, fontName='Helvetica-Bold'))
        ],
        # QR code and reference row
        [
            Image(qr_buffer, width=1.5*inch, height=1.5*inch),
            "",
            Paragraph(f"<font color='#6b7280' size='8'>{ticket.ticket_reference}</font>", 
                     ParagraphStyle('TicketRef', fontSize=8, alignment=TA_CENTER, fontName='Helvetica'))
        ]
    ]
    
    # Create ticket table
    ticket_table = Table(ticket_content, colWidths=[3*inch, 0.5*inch, 2.5*inch], rowHeights=[0.4*inch, 0.3*inch, 0.4*inch, 1.5*inch])
    
    # Style the ticket table
    ticket_table.setStyle(TableStyle([
        # Borders
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e40af')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#1e40af')),
        ('LINEBELOW', (0, 2), (-1, 2), 1, colors.HexColor('#1e40af')),
        
        # Background colors
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),  # Header background
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#f0f9ff')),  # Time row background
        ('BACKGROUND', (0, 3), (-1, 3), colors.white),
        
        # Padding
        ('PADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Perforated line effect (dashed border)
        ('LINEBELOW', (0, 3), (-1, 3), 1, colors.HexColor('#d1d5db')),
    ]))
    
    # Add perforated edge effect
    perforated_style = TableStyle([
        ('LINEABOVE', (0, 3), (-1, 3), 1, colors.HexColor('#d1d5db')),
        ('LINEBELOW', (0, 3), (-1, 3), 1, colors.HexColor('#d1d5db')),
    ])
    
    # Create ticket stub
    stub_content = [
        [
            Paragraph(f"<font color='#6b7280' size='8'>KEEP THIS TICKET</font>", 
                     ParagraphStyle('StubText', fontSize=8, alignment=TA_CENTER, fontName='Helvetica')),
            "",
            Paragraph(f"<font color='#6b7280' size='8'>{ticket.ticket_reference}</font>", 
                     ParagraphStyle('StubRef', fontSize=8, alignment=TA_CENTER, fontName='Helvetica'))
        ]
    ]
    
    stub_table = Table(stub_content, colWidths=[3*inch, 0.5*inch, 2.5*inch], rowHeights=[0.3*inch])
    stub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f9fafb')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    return [ticket_table, Spacer(1, 10), stub_table]

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