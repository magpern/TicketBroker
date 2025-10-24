from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from app.models import Show, Booking, Settings, Ticket
from app import db
from app.utils.audit import log_booking_created, log_payment_initiated, log_buyer_confirmed_payment
from datetime import datetime
import re
import qrcode
import io
import base64

public_bp = Blueprint('public', __name__)

def generate_swish_url(phone, amount, booking_ref):
    """Generate Swish deep link URL"""
    # Remove spaces and format phone number
    clean_phone = phone.replace(' ', '').replace('-', '')
    
    # Format: https://app.swish.nu/1/p/sw/?sw=PHONE&amt=AMOUNT&cur=SEK&msg=REF&src=qr
    url = f"https://app.swish.nu/1/p/sw/?sw={clean_phone}&amt={amount}&cur=SEK&msg={booking_ref}&src=qr"
    return url

def is_mobile_device(user_agent):
    """Detect if the user is on a mobile device"""
    mobile_indicators = [
        'Mobile', 'Android', 'iPhone', 'iPad', 'iPod', 
        'BlackBerry', 'Windows Phone', 'Opera Mini'
    ]
    user_agent_lower = user_agent.lower()
    return any(indicator.lower() in user_agent_lower for indicator in mobile_indicators)

def generate_swish_qr_code(phone, amount, booking_ref):
    """Generate QR code for Swish payment"""
    # Create Swish payment URL
    swish_url = generate_swish_url(phone, amount, booking_ref)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(swish_url)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 string
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"

@public_bp.route('/class-photo')
def class_photo():
    """Serve class photo from database"""
    from flask import Response
    
    # Get class photo data from database
    class_photo_data = Settings.get_value('class_photo_data')
    class_photo_content_type = Settings.get_value('class_photo_content_type', 'image/jpeg')
    
    if class_photo_data:
        import base64
        try:
            # Decode base64 data
            photo_bytes = base64.b64decode(class_photo_data)
            return Response(photo_bytes, mimetype=class_photo_content_type)
        except Exception as e:
            print(f"Error decoding class photo data: {e}")
    
    # Fallback to static file if no database image
    from flask import send_from_directory
    return send_from_directory('static/images', 'class-photo.jpg')

@public_bp.route('/')
def index():
    """Landing page with class photo and welcome message"""
    # Get settings
    swish_recipient_name = Settings.get_value('swish_recipient_name', 'Donald Duch')
    adult_price = Settings.get_value('adult_price', '200')
    student_price = Settings.get_value('student_price', '100')
    concert_date = Settings.get_value('concert_date', '29/1 2026')
    concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
    welcome_message = Settings.get_value('welcome_message', 'Välkommen till 24c:s klasspelning!')
    
    # Get shows to display times dynamically
    shows = Show.query.order_by(Show.start_time).all()
    
    # Format show times for display
    show_times = []
    if shows:
        for show in shows:
            show_times.append(f"{show.start_time}-{show.end_time}")
        times_display = " eller ".join(show_times)
    else:
        times_display = "17:45-18:45 eller 19:00-20:00"  # fallback

    return render_template('index.html', 
                         swish_recipient_name=swish_recipient_name,
                         adult_price=adult_price,
                         student_price=student_price,
                         concert_date=concert_date,
                         concert_name=concert_name,
                         welcome_message=welcome_message,
                         times_display=times_display)

@public_bp.route('/booking')
def booking():
    """Step 1: Time slot selection"""
    shows = Show.query.order_by(Show.start_time).all()  # Order chronologically
    if not shows:
        # Create default shows if none exist
        show1 = Show(date='29/1 2026', start_time='17:45', end_time='18:45', total_tickets=100, available_tickets=100)
        show2 = Show(date='29/1 2026', start_time='19:00', end_time='20:00', total_tickets=100, available_tickets=100)
        db.session.add(show1)
        db.session.add(show2)
        db.session.commit()
        shows = [show1, show2]
    
    # Get settings
    swish_recipient_name = Settings.get_value('swish_recipient_name', 'Oliver Ahlstrand')
    concert_date = Settings.get_value('concert_date', '29/1 2026')
    
    return render_template('booking.html', step=1, shows=shows, 
                         swish_recipient_name=swish_recipient_name, concert_date=concert_date)

@public_bp.route('/booking/tickets', methods=['GET', 'POST'])
def booking_tickets():
    """Step 2: Ticket quantity selection"""
    if request.method == 'POST':
        show_id = request.form.get('show_id')
        if not show_id:
            flash('Välj en tid först.', 'error')
            return redirect(url_for('public.booking'))
        
        session['show_id'] = show_id
        show = Show.query.get_or_404(show_id)
        
        if show.is_sold_out:
            flash('Tyvärr är biljetterna slut till den här spelningen.', 'error')
            return redirect(url_for('public.booking'))
        
        # Get dynamic prices and labels from settings
        adult_price = int(Settings.get_value('adult_price', '200'))
        student_price = int(Settings.get_value('student_price', '100'))
        adult_label = Settings.get_value('adult_ticket_label', 'Ordinarie biljett')
        student_label = Settings.get_value('student_ticket_label', 'Studentbiljett')
        
        return render_template('booking.html', step=2, show=show, 
                             adult_price=adult_price,
                             student_price=student_price,
                             adult_label=adult_label,
                             student_label=student_label,
                             swish_recipient_name=Settings.get_value('swish_recipient_name', 'Oliver Ahlstrand'),
                             concert_date=Settings.get_value('concert_date', '29/1 2026'))
    
    # GET request - redirect to step 1 if no show selected
    if 'show_id' not in session:
        return redirect(url_for('public.booking'))
    
    show = Show.query.get_or_404(session['show_id'])
    
    # Get dynamic prices and labels from settings
    adult_price = int(Settings.get_value('adult_price', '200'))
    student_price = int(Settings.get_value('student_price', '100'))
    adult_label = Settings.get_value('adult_ticket_label', 'Ordinarie biljett')
    student_label = Settings.get_value('student_ticket_label', 'Studentbiljett')
    
    return render_template('booking.html', step=2, show=show, 
                         adult_price=adult_price,
                         student_price=student_price,
                         adult_label=adult_label,
                         student_label=student_label,
                         swish_recipient_name=Settings.get_value('swish_recipient_name', 'Oliver Ahlstrand'),
                         concert_date=Settings.get_value('concert_date', '29/1 2026'))

@public_bp.route('/booking/contact', methods=['GET', 'POST'])
def booking_contact():
    """Step 3: Contact information"""
    if request.method == 'POST':
        adult_tickets = int(request.form.get('adult_tickets', 0))
        student_tickets = int(request.form.get('student_tickets', 0))
        
        if adult_tickets + student_tickets == 0:
            flash('Välj minst en biljett.', 'error')
            return redirect(url_for('public.booking_tickets'))
        
        if adult_tickets + student_tickets > 4:
            flash('Du kan bara boka upp till 4 biljetter åt gången.', 'error')
            return redirect(url_for('public.booking_tickets'))
        
        session['adult_tickets'] = adult_tickets
        session['student_tickets'] = student_tickets
        
        # Calculate total amount
        adult_price = int(Settings.get_value('adult_price', '200'))
        student_price = int(Settings.get_value('student_price', '100'))
        adult_label = Settings.get_value('adult_ticket_label', 'Ordinarie biljett')
        student_label = Settings.get_value('student_ticket_label', 'Studentbiljett')
        total_amount = (adult_tickets * adult_price) + (student_tickets * student_price)
        session['total_amount'] = total_amount
        
        return render_template('booking.html', step=3, 
                             adult_tickets=adult_tickets, 
                             student_tickets=student_tickets,
                             adult_label=adult_label,
                             student_label=student_label,
                             total_amount=total_amount,
                             swish_recipient_name=Settings.get_value('swish_recipient_name', 'Oliver Ahlstrand'),
                             concert_date=Settings.get_value('concert_date', '29/1 2026'))
    
    # GET request - redirect to step 2 if no tickets selected
    if 'adult_tickets' not in session or 'student_tickets' not in session:
        return redirect(url_for('public.booking_tickets'))
    
    return render_template('booking.html', step=3,
                         adult_tickets=session['adult_tickets'],
                         student_tickets=session['student_tickets'],
                         total_amount=session['total_amount'],
                         swish_recipient_name=Settings.get_value('swish_recipient_name', 'Oliver Ahlstrand'),
                         concert_date=Settings.get_value('concert_date', '29/1 2026'))

@public_bp.route('/booking/confirm', methods=['POST'])
def booking_confirm():
    """Final step: Create booking"""
    # Validate required fields
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    gdpr_consent = request.form.get('gdpr_consent') == 'on'
    
    if not all([first_name, last_name, email, phone]):
        flash('Alla fält är obligatoriska.', 'error')
        return redirect(url_for('public.booking_contact'))
    
    if not gdpr_consent:
        flash('Du måste godkänna att informationen sparas.', 'error')
        return redirect(url_for('public.booking_contact'))
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        flash('Ange en giltig e-postadress.', 'error')
        return redirect(url_for('public.booking_contact'))
    
    # Validate phone format (Swedish phone numbers)
    phone_pattern = r'^(\+46|0)[0-9\s-]{8,12}$'
    if not re.match(phone_pattern, phone.replace(' ', '')):
        flash('Ange ett giltigt telefonnummer.', 'error')
        return redirect(url_for('public.booking_contact'))
    
    # Check if we have all required session data
    if not all(key in session for key in ['show_id', 'adult_tickets', 'student_tickets', 'total_amount']):
        flash('Sessionen har gått ut. Börja om bokningen.', 'error')
        return redirect(url_for('public.booking'))
    
    # Check if show is still available
    show = Show.query.get_or_404(session['show_id'])
    if show.is_sold_out:
        flash('Tyvärr är biljetterna slut till den här spelningen.', 'error')
        return redirect(url_for('public.booking'))
    
    # Generate unique booking reference
    booking_reference = Booking.generate_booking_reference()
    
    # Create booking
    booking = Booking(
        show_id=session['show_id'],
        booking_reference=booking_reference,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        adult_tickets=session['adult_tickets'],
        student_tickets=session['student_tickets'],
        total_amount=session['total_amount'],
        gdpr_consent=True
    )
    
    try:
        db.session.add(booking)
        db.session.commit()
        
        # Log booking creation
        log_booking_created(booking)
        
        # Clear session data
        session.pop('show_id', None)
        session.pop('adult_tickets', None)
        session.pop('student_tickets', None)
        session.pop('total_amount', None)
        
        # Send confirmation email
        from app.utils.email import send_booking_confirmation
        send_booking_confirmation(booking)
        
        flash('Tack! Du har reserverat dina biljetter. Glöm inte att swisha summan till 070 123 45 67 för att bekräfta din plats.', 'success')
        return redirect(url_for('public.booking_success', booking_reference=booking.booking_reference, email=booking.email))
        
    except Exception as e:
        db.session.rollback()
        flash('Ett fel uppstod. Försök igen.', 'error')
        return redirect(url_for('public.booking_contact'))

@public_bp.route('/ticket/<ticket_reference>')
def mobile_ticket(ticket_reference):
    """Mobile-friendly ticket display with QR code"""
    ticket = Ticket.query.filter_by(ticket_reference=ticket_reference).first_or_404()
    
    # Get logo data from database if available
    logo_data = None
    qr_logo_data = Settings.get_value('qr_logo_data')
    
    if qr_logo_data:
        import base64
        import io
        
        try:
            # Decode base64 data
            logo_bytes = base64.b64decode(qr_logo_data)
            logo_data = io.BytesIO(logo_bytes)
        except Exception as e:
            print(f"Error decoding logo data: {e}")
            logo_data = None
    
    # Generate QR code for this specific ticket with logo
    qr_code_data = generate_ticket_qr_code(ticket, logo_data)
    
    # Get concert information from settings
    concert_name = Settings.get_value('concert_name', 'Klasskonsert 24C')
    concert_date = Settings.get_value('concert_date', '29/1 2026')
    concert_venue = Settings.get_value('concert_venue', 'Aulan på Rytmus Stockholm')
    
    return render_template('mobile_ticket.html', 
                         ticket=ticket,
                         qr_code_data=qr_code_data,
                         concert_name=concert_name,
                         concert_date=concert_date,
                         concert_venue=concert_venue)

@public_bp.route('/validate-ticket')
@public_bp.route('/validate-ticket/<int:show_id>')
def validate_ticket_page(show_id=None):
    """Mobile-friendly ticket validation page for door staff"""
    from app.models import Show
    
    # Get all shows for selection
    shows = Show.query.order_by(Show.start_time).all()
    
    # If show_id is provided, get that specific show
    selected_show = None
    if show_id:
        selected_show = Show.query.get(show_id)
    
    return render_template('validate_ticket.html', 
                         shows=shows, 
                         selected_show=selected_show)

@public_bp.route('/api/validate-ticket', methods=['POST'])
def validate_ticket_api():
    """API endpoint to validate a ticket by QR code"""
    try:
        data = request.get_json()
        ticket_reference = data.get('ticket_reference', '').strip()
        show_id = data.get('show_id')
        
        print(f"🔍 Validating ticket: {ticket_reference} for show: {show_id}")
        
        if not ticket_reference:
            print("❌ No ticket reference provided")
            return jsonify({
                'valid': False,
                'message': 'Ingen biljettreferens angiven',
                'status': 'error'
            }), 400
        
        if not show_id:
            print("❌ No show ID provided")
            return jsonify({
                'valid': False,
                'message': 'Ingen föreställning vald',
                'status': 'error'
            }), 400
        
        # Find the ticket
        ticket = Ticket.query.filter_by(ticket_reference=ticket_reference).first()
        
        if not ticket:
            print(f"❌ Ticket not found: {ticket_reference}")
            return jsonify({
                'valid': False,
                'message': 'Biljett hittades inte',
                'status': 'error',
                'ticket_reference': ticket_reference
            })
        
        print(f"🎫 Found ticket: {ticket.ticket_reference}, is_used: {ticket.is_used}, booking_status: {ticket.booking.status}")
        
        # Check if ticket is for the correct show
        if ticket.booking.show_id != int(show_id):
            print(f"⚠️ Ticket for wrong show: {ticket_reference}, ticket show: {ticket.booking.show_id}, validation show: {show_id}")
            return jsonify({
                'valid': False,
                'message': 'Biljett för fel föreställning',
                'status': 'wrong_show',
                'ticket_reference': ticket_reference,
                'ticket_show_id': ticket.booking.show_id,
                'validation_show_id': int(show_id)
            })
        
        # Check if ticket is already used
        if ticket.is_used:
            print(f"⚠️ Ticket already used: {ticket_reference}")
            return jsonify({
                'valid': False,
                'message': 'Biljett redan använd',
                'status': 'used',
                'ticket_reference': ticket_reference,
                'used_at': ticket.used_at.isoformat() if ticket.used_at else None
            })
        
        # Check if booking is confirmed
        if ticket.booking.status != 'confirmed':
            print(f"⚠️ Booking not confirmed: {ticket_reference}, status: {ticket.booking.status}")
            return jsonify({
                'valid': False,
                'message': 'Biljett inte bekräftad',
                'status': 'unconfirmed',
                'ticket_reference': ticket_reference,
                'booking_status': ticket.booking.status
            })
        
        # Mark ticket as used
        ticket.is_used = True
        ticket.used_at = datetime.now()
        
        # Log the ticket usage
        from app.utils.audit import log_ticket_used
        log_ticket_used(ticket, 'Door validation')
        
        db.session.commit()
        
        print(f"✅ Ticket validated successfully: {ticket_reference}")
        
        return jsonify({
            'valid': True,
            'message': 'Biljett godkänd - välkommen in!',
            'status': 'success',
            'ticket_reference': ticket_reference,
            'ticket_type': 'Ordinarie' if ticket.ticket_type == 'normal' else 'Student',
            'booking_reference': ticket.booking.booking_reference,
            'used_at': ticket.used_at.isoformat()
        })
        
    except Exception as e:
        print(f"💥 Error validating ticket: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'valid': False,
            'message': 'Ett internt fel uppstod. Försök igen senare.',
            'status': 'error'
        }), 500

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

@public_bp.route('/booking/success/<booking_reference>/<email>')
def booking_success(booking_reference, email):
    """Success page with payment confirmation option"""
    booking = Booking.query.filter_by(booking_reference=booking_reference, email=email.lower()).first_or_404()
    
    # Get Swish settings
    swish_number = Settings.get_value('swish_number', '070 123 45 67')
    swish_recipient_name = Settings.get_value('swish_recipient_name', 'Oliver Ahlstrand')
    
    # Detect if user is on mobile device
    user_agent = request.headers.get('User-Agent', '')
    is_mobile = is_mobile_device(user_agent)
    
    # Generate QR code for desktop users
    qr_code_data = None
    if not is_mobile:
        qr_code_data = generate_swish_qr_code(swish_number, booking.total_amount, booking.booking_reference)
    
    return render_template('booking_success.html', 
                         booking=booking,
                         swish_number=swish_number,
                         swish_recipient_name=swish_recipient_name,
                         is_mobile=is_mobile,
                         qr_code_data=qr_code_data)

@public_bp.route('/booking/initiate-payment/<booking_reference>/<email>', methods=['POST'])
def initiate_payment(booking_reference, email):
    """Initiate Swish payment and log the action"""
    booking = Booking.query.filter_by(booking_reference=booking_reference, email=email.lower()).first_or_404()
    
    if booking.status == 'confirmed':
        flash('Betalningen är redan bekräftad.', 'info')
        return redirect(url_for('public.booking_success', booking_reference=booking_reference, email=email))
    
    # Mark payment as initiated
    booking.swish_payment_initiated = True
    booking.swish_payment_initiated_at = datetime.utcnow()
    db.session.commit()
    
    # Log payment initiation
    log_payment_initiated(booking)
    
    # Generate Swish URL
    swish_number = Settings.get_value('swish_number', '070 123 45 67')
    swish_url = generate_swish_url(swish_number, booking.total_amount, booking.booking_reference)
    
    # Detect if user is on mobile device
    user_agent = request.headers.get('User-Agent', '')
    is_mobile = is_mobile_device(user_agent)
    
    return jsonify({
        'success': True,
        'swish_url': swish_url,
        'is_mobile': is_mobile,
        'message': 'Swish-betalning initierad'
    })

@public_bp.route('/booking/confirm-payment/<booking_reference>/<email>', methods=['POST'])
def confirm_payment(booking_reference, email):
    """Buyer confirms they have paid via Swish"""
    booking = Booking.query.filter_by(booking_reference=booking_reference, email=email.lower()).first_or_404()
    
    if booking.status == 'confirmed':
        flash('Betalningen är redan bekräftad.', 'info')
        return redirect(url_for('public.booking_success', booking_reference=booking_reference, email=email))
    
    booking.buyer_confirmed_payment = True
    db.session.commit()
    
    # Log buyer confirmation
    log_buyer_confirmed_payment(booking)
    
    # Send notification to admin
    from app.utils.email import send_admin_notification
    send_admin_notification(booking)
    
    flash('Tack! Vi har fått din bekräftelse. Administratören kommer att kontrollera betalningen.', 'success')
    return redirect(url_for('public.booking_success', booking_reference=booking_reference, email=email))

@public_bp.route('/api/check-availability')
def check_availability():
    """API endpoint to check ticket availability"""
    show_id = request.args.get('show_id')
    if not show_id:
        return jsonify({'error': 'Show ID required'}), 400
    
    show = Show.query.get_or_404(show_id)
    show.update_availability()
    db.session.commit()
    
    return jsonify({
        'available': show.available_tickets,
        'sold_out': show.is_sold_out
    })

@public_bp.route('/lost-tickets', methods=['GET', 'POST'])
def lost_tickets():
    """Lost tickets functionality - find booking by email and resend tickets"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Vänligen ange din e-postadress.', 'error')
            return render_template('lost_tickets.html')
        
        # Find ALL bookings by email that have confirmed tickets
        bookings = Booking.query.filter_by(email=email, status='confirmed').all()
        confirmed_bookings_with_tickets = [b for b in bookings if b.tickets]
        
        if confirmed_bookings_with_tickets:
            # Send ticket resend email for each confirmed booking with tickets
            from app.utils.email import send_multiple_tickets_resend
            if send_multiple_tickets_resend(confirmed_bookings_with_tickets):
                if len(confirmed_bookings_with_tickets) == 1:
                    flash('Om denna e-post har biljetter kommer dessa skickas dit.', 'success')
                else:
                    flash(f'Om denna e-post har biljetter kommer dessa skickas dit ({len(confirmed_bookings_with_tickets)} bokningar hittades).', 'success')
            else:
                flash('Ett fel uppstod vid skickande av e-post. Försök igen senare.', 'error')
        else:
            # Always show success message for security (don't reveal if email exists)
            flash('Om denna e-post har biljetter kommer dessa skickas dit.', 'success')
        
        return render_template('lost_tickets.html')
    
    return render_template('lost_tickets.html')

@public_bp.route('/find-booking', methods=['GET', 'POST'])
def find_booking():
    """Find booking by email and last name"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        last_name = request.form.get('last_name', '').strip()
        
        if not email or not last_name:
            flash('Vänligen fyll i både e-post och efternamn.', 'error')
            return render_template('find_booking.html')
        
        # Find ALL bookings by email and last name
        bookings = Booking.query.filter_by(email=email, last_name=last_name).all()
        
        if bookings:
            if len(bookings) == 1:
                # Single booking - redirect directly
                return redirect(url_for('public.booking_success', booking_reference=bookings[0].booking_reference, email=bookings[0].email))
            else:
                # Multiple bookings - show selection page
                return render_template('booking_selection.html', bookings=bookings)
        else:
            flash('Ingen bokning hittades med denna e-post och efternamn.', 'error')
            return render_template('find_booking.html')
    
    return render_template('find_booking.html')

@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form page"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        gdpr_consent = request.form.get('gdpr_consent') == 'on'
        
        # Validation
        if not all([name, email, subject, message]):
            flash('Alla obligatoriska fält måste fyllas i.', 'error')
            return render_template('contact.html')
        
        if not gdpr_consent:
            flash('Du måste godkänna att informationen sparas.', 'error')
            return render_template('contact.html')
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Ange en giltig e-postadress.', 'error')
            return render_template('contact.html')
        
        # Send contact email
        from app.utils.email import send_contact_message
        if send_contact_message(name, email, phone, subject, message):
            flash('Tack för ditt meddelande! Vi återkommer så snart som möjligt.', 'success')
            return redirect(url_for('public.contact'))
        else:
            flash('Ett fel uppstod vid skickande av meddelandet. Försök igen senare.', 'error')
            return render_template('contact.html')
    
    return render_template('contact.html')
