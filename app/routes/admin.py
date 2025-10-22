from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import Show, Booking, Settings
from app import db
from app.utils.email import send_payment_confirmed
from datetime import datetime
import io
import csv
from openpyxl import Workbook

admin_bp = Blueprint('admin', __name__)

def login_required(f):
    """Decorator to require admin login"""
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('password')
        admin_password = 'klasskonsert26'  # In production, this should be hashed
        
        if password == admin_password:
            session['admin_logged_in'] = True
            flash('Inloggning lyckades!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Felaktigt lösenord.', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('Du har loggats ut.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@login_required
def dashboard():
    """Admin dashboard with all bookings"""
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    
    # Group bookings by show
    bookings_by_show = {}
    for booking in bookings:
        show_key = f"{booking.show.start_time}-{booking.show.end_time}"
        if show_key not in bookings_by_show:
            bookings_by_show[show_key] = []
        bookings_by_show[show_key].append(booking)
    
    return render_template('admin/dashboard.html', bookings_by_show=bookings_by_show)

@admin_bp.route('/settings')
@login_required
def settings():
    """Admin settings page"""
    settings_data = {}
    for setting in Settings.query.all():
        settings_data[setting.key] = setting.value
    
    return render_template('admin/settings.html', settings=settings_data)

@admin_bp.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    """Update settings"""
    try:
        # Update each setting
        for key in request.form:
            if key != 'csrf_token':
                Settings.set_value(key, request.form[key])
        
        flash('Inställningar sparade!', 'success')
    except Exception as e:
        flash('Ett fel uppstod vid sparande av inställningar.', 'error')
    
    return redirect(url_for('admin.settings'))

@admin_bp.route('/booking/<int:booking_id>/confirm-payment', methods=['POST'])
@login_required
def confirm_payment(booking_id):
    """Admin confirms payment"""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status == 'confirmed':
        flash('Betalningen är redan bekräftad.', 'info')
        return redirect(url_for('admin.dashboard'))
    
    booking.status = 'confirmed'
    booking.confirmed_at = datetime.utcnow()
    
    # Update show availability
    booking.show.update_availability()
    
    db.session.commit()
    
    # Send confirmation email to buyer
    send_payment_confirmed(booking)
    
    flash(f'Betalning bekräftad för {booking.full_name}!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/booking/<int:booking_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_booking(booking_id):
    """Edit booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    if request.method == 'POST':
        try:
            booking.first_name = request.form.get('first_name')
            booking.last_name = request.form.get('last_name')
            booking.email = request.form.get('email')
            booking.phone = request.form.get('phone')
            booking.adult_tickets = int(request.form.get('adult_tickets', 0))
            booking.student_tickets = int(request.form.get('student_tickets', 0))
            
            # Recalculate total amount
            adult_price = int(Settings.get_value('adult_price', '200'))
            student_price = int(Settings.get_value('student_price', '100'))
            booking.total_amount = (booking.adult_tickets * adult_price) + (booking.student_tickets * student_price)
            
            db.session.commit()
            flash('Bokning uppdaterad!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash('Ett fel uppstod vid uppdatering.', 'error')
    
    return render_template('admin/edit_booking.html', booking=booking)

@admin_bp.route('/booking/<int:booking_id>/delete', methods=['POST'])
@login_required
def delete_booking(booking_id):
    """Delete booking with confirmation"""
    booking = Booking.query.get_or_404(booking_id)
    
    try:
        # Update show availability before deleting
        booking.show.update_availability()
        
        db.session.delete(booking)
        db.session.commit()
        flash(f'Bokning för {booking.full_name} har raderats.', 'success')
    except Exception as e:
        flash('Ett fel uppstod vid radering.', 'error')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/export/excel')
@login_required
def export_excel():
    """Export all bookings to Excel"""
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Biljettbokningar"
    
    # Headers
    headers = ['ID', 'Namn', 'E-post', 'Telefon', 'Tid', 'Ordinarie biljetter', 'Studentbiljetter', 'Totalt', 'Status', 'Betalning bekräftad', 'Datum']
    for col, header in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=header)
    
    # Data
    for row, booking in enumerate(bookings, 2):
        ws.cell(row=row, column=1, value=booking.id)
        ws.cell(row=row, column=2, value=booking.full_name)
        ws.cell(row=row, column=3, value=booking.email)
        ws.cell(row=row, column=4, value=booking.phone)
        ws.cell(row=row, column=5, value=f"{booking.show.start_time}-{booking.show.end_time}")
        ws.cell(row=row, column=6, value=booking.adult_tickets)
        ws.cell(row=row, column=7, value=booking.student_tickets)
        ws.cell(row=row, column=8, value=booking.total_amount)
        ws.cell(row=row, column=9, value=booking.status)
        ws.cell(row=row, column=10, value='Ja' if booking.buyer_confirmed_payment else 'Nej')
        ws.cell(row=row, column=11, value=booking.created_at.strftime('%Y-%m-%d %H:%M'))
    
    # Save to BytesIO
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename=biljettbokningar_{datetime.now().strftime("%Y%m%d")}.xlsx'
    
    return response

@admin_bp.route('/shows')
@login_required
def manage_shows():
    """Manage shows/times"""
    shows = Show.query.all()
    return render_template('admin/shows.html', shows=shows)

@admin_bp.route('/shows/create', methods=['POST'])
@login_required
def create_show():
    """Create new show"""
    try:
        show = Show(
            date=request.form.get('date'),
            start_time=request.form.get('start_time'),
            end_time=request.form.get('end_time'),
            total_tickets=int(request.form.get('total_tickets', 100)),
            available_tickets=int(request.form.get('total_tickets', 100))
        )
        db.session.add(show)
        db.session.commit()
        flash('Ny föreställning skapad!', 'success')
    except Exception as e:
        flash('Ett fel uppstod vid skapande av föreställning.', 'error')
    
    return redirect(url_for('admin.manage_shows'))

@admin_bp.route('/shows/<int:show_id>/delete', methods=['POST'])
@login_required
def delete_show(show_id):
    """Delete show"""
    show = Show.query.get_or_404(show_id)
    
    if show.bookings:
        flash('Kan inte radera föreställning med befintliga bokningar.', 'error')
        return redirect(url_for('admin.manage_shows'))
    
    try:
        db.session.delete(show)
        db.session.commit()
        flash('Föreställning raderad!', 'success')
    except Exception as e:
        flash('Ett fel uppstod vid radering.', 'error')
    
    return redirect(url_for('admin.manage_shows'))
