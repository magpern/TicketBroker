from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models import Show, Booking, Settings
from app import db
from datetime import datetime
import re

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Landing page with class photo and welcome message"""
    return render_template('index.html')

@public_bp.route('/booking')
def booking():
    """Step 1: Time slot selection"""
    shows = Show.query.all()
    if not shows:
        # Create default shows if none exist
        show1 = Show(date='29/1 2026', start_time='17:45', end_time='18:45', total_tickets=100, available_tickets=100)
        show2 = Show(date='29/1 2026', start_time='19:00', end_time='20:00', total_tickets=100, available_tickets=100)
        db.session.add(show1)
        db.session.add(show2)
        db.session.commit()
        shows = [show1, show2]
    
    return render_template('booking.html', step=1, shows=shows)

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
        
        return render_template('booking.html', step=2, show=show)
    
    # GET request - redirect to step 1 if no show selected
    if 'show_id' not in session:
        return redirect(url_for('public.booking'))
    
    show = Show.query.get_or_404(session['show_id'])
    return render_template('booking.html', step=2, show=show)

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
        total_amount = (adult_tickets * adult_price) + (student_tickets * student_price)
        session['total_amount'] = total_amount
        
        return render_template('booking.html', step=3, 
                             adult_tickets=adult_tickets, 
                             student_tickets=student_tickets,
                             total_amount=total_amount)
    
    # GET request - redirect to step 2 if no tickets selected
    if 'adult_tickets' not in session or 'student_tickets' not in session:
        return redirect(url_for('public.booking_tickets'))
    
    return render_template('booking.html', step=3,
                         adult_tickets=session['adult_tickets'],
                         student_tickets=session['student_tickets'],
                         total_amount=session['total_amount'])

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
    
    # Create booking
    booking = Booking(
        show_id=session['show_id'],
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
        
        # Clear session data
        session.pop('show_id', None)
        session.pop('adult_tickets', None)
        session.pop('student_tickets', None)
        session.pop('total_amount', None)
        
        # Send confirmation email
        from app.utils.email import send_booking_confirmation
        send_booking_confirmation(booking)
        
        flash('Tack! Du har reserverat dina biljetter. Glöm inte att swisha summan till 070 123 45 67 för att bekräfta din plats.', 'success')
        return redirect(url_for('public.booking_success', booking_id=booking.id))
        
    except Exception as e:
        db.session.rollback()
        flash('Ett fel uppstod. Försök igen.', 'error')
        return redirect(url_for('public.booking_contact'))

@public_bp.route('/booking/success/<int:booking_id>')
def booking_success(booking_id):
    """Success page with payment confirmation option"""
    booking = Booking.query.get_or_404(booking_id)
    return render_template('booking_success.html', booking=booking)

@public_bp.route('/booking/confirm-payment/<int:booking_id>', methods=['POST'])
def confirm_payment(booking_id):
    """Buyer confirms they have paid via Swish"""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status == 'confirmed':
        flash('Betalningen är redan bekräftad.', 'info')
        return redirect(url_for('public.booking_success', booking_id=booking_id))
    
    booking.buyer_confirmed_payment = True
    db.session.commit()
    
    # Send notification to admin
    from app.utils.email import send_admin_notification
    send_admin_notification(booking)
    
    flash('Tack! Vi har fått din bekräftelse. Administratören kommer att kontrollera betalningen.', 'success')
    return redirect(url_for('public.booking_success', booking_id=booking_id))

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
