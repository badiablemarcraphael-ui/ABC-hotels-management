from flask import Blueprint, request, jsonify, session, render_template, send_file, redirect, url_for
import sys
import os
from decimal import Decimal
from datetime import datetime
import json
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask_app.db_config import get_db_connection
from flask_app.utils.email_service import email_service
from flask_app.utils.pdf_generator import generate_booking_ticket
from flask_app.utils.paymongo_checkout import paymongo_checkout

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/checkout/<int:booking_id>', methods=['GET'])
def checkout_page(booking_id):
    """Show checkout/payment page"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.*, r.room_number, rt.type_name 
        FROM bookings b
        JOIN rooms r ON b.room_id = r.room_id
        JOIN room_types rt ON r.type_id = rt.type_id
        WHERE b.booking_id = %s
    """, (booking_id,))
    
    booking = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not booking:
        return "Booking not found", 404
    
    check_in = datetime.strptime(str(booking['check_in_date']), '%Y-%m-%d')
    check_out = datetime.strptime(str(booking['check_out_date']), '%Y-%m-%d')
    nights = (check_out - check_in).days
    
    total_amount = float(booking['total_amount'])
    vat = total_amount * 0.07
    service = total_amount * 0.05
    grand_total = total_amount + vat + service
    
    return render_template('checkout_payment.html', 
                          booking=booking, 
                          nights=nights,
                          total_amount=total_amount,
                          vat=vat,
                          service=service,
                          grand_total=grand_total)


@payment_bp.route('/initiate-gcash-payment', methods=['POST'])
def initiate_gcash_payment():
    """Step 1: Create PayMongo Checkout Session and redirect"""
    try:
        booking_id = request.form.get('booking_id')
        amount = float(request.form.get('amount', 0))
        
        # Store in session for callback
        session['pending_booking_id'] = booking_id
        
        # Get booking details
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bookings WHERE booking_id = %s", (booking_id,))
        booking = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not booking:
            return render_template('payment_error.html', 
                                  error="Booking not found",
                                  booking_id=booking_id)
        
        # Create PayMongo checkout session
        result = paymongo_checkout.create_checkout_session(
            booking_id=booking_id,
            amount=amount,
            guest_name=booking['guest_name'],
            guest_email=booking['guest_email'],
            description=f"Hotel Booking - Room {booking.get('room_number', 'N/A')}"
        )
        
        if result['success']:
            # Redirect to PayMongo checkout page
            return redirect(result['checkout_url'])
        else:
            return render_template('payment_error.html', 
                                  error=result['message'],
                                  booking_id=booking_id)
        
    except Exception as e:
        print(f"Initiate payment error: {e}")
        return render_template('payment_error.html', error=str(e), booking_id=booking_id)


@payment_bp.route('/paymongo-success', methods=['GET'])
def paymongo_success():
    """Step 2: Handle successful payment from PayMongo"""
    print("=" * 50)
    print("🔔 PayMongo SUCCESS Callback Received!")
    print(f"Full URL: {request.url}")
    print(f"Args: {request.args}")
    
    booking_id = request.args.get('booking_id')
    session_id = request.args.get('session_id')
    
    print(f"Booking ID from URL: {booking_id}")
    print(f"Session ID from URL: {session_id}")
    
    if not booking_id:
        # Try to get from session
        pending = session.get('pending_payment', {})
        booking_id = pending.get('booking_id')
        print(f"Booking ID from session: {booking_id}")
    
    if not booking_id:
        print("❌ No booking ID found!")
        return "No booking found", 404
    
    # Clear session
    session.pop('pending_booking_id', None)
    session.pop('pending_payment', None)
    
    print(f"✅ Redirecting to payment success page for booking {booking_id}")
    
    # Redirect to payment success page with modal
    return redirect(url_for('payment.payment_success_modal_page', booking_id=booking_id))


@payment_bp.route('/paymongo-failed', methods=['GET'])
def paymongo_failed():
    """Handle failed payment from PayMongo"""
    print("=" * 50)
    print("🔔 PayMongo FAILED Callback Received!")
    print(f"Full URL: {request.url}")
    
    booking_id = request.args.get('booking_id')
    error_message = request.args.get('error_message', 'Payment was not completed')
    
    print(f"Booking ID: {booking_id}")
    print(f"Error: {error_message}")
    
    # Check if it's an expired session error
    if "expired" in str(error_message).lower():
        error_message = "The payment session has expired. Please create a new booking and try again."
    
    return render_template('payment_failed.html', 
                          booking_id=booking_id,
                          error_message=error_message)


@payment_bp.route('/payment-success-modal/<int:booking_id>', methods=['GET'])
def payment_success_modal_page(booking_id):
    """Show payment success modal page for GCash payments"""
    return render_template('payment_success_modal.html', booking_id=booking_id)


@payment_bp.route('/process-payment-success-json/<int:booking_id>', methods=['GET'])
def process_payment_success_json(booking_id):
    """Process successful payment and return JSON with receipt data for modal"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT b.*, r.room_number, rt.type_name 
            FROM bookings b
            JOIN rooms r ON b.room_id = r.room_id
            JOIN room_types rt ON r.type_id = rt.type_id
            WHERE b.booking_id = %s
        """, (booking_id,))
        
        booking = cursor.fetchone()
        
        if not booking:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Booking not found'})
        
        total_amount = float(booking['total_amount'])
        
        nights = (datetime.strptime(str(booking['check_out_date']), '%Y-%m-%d') - 
                 datetime.strptime(str(booking['check_in_date']), '%Y-%m-%d')).days
        
        discount_amount = float(booking.get('discount_amount', 0)) if booking.get('discount_amount') else 0
        coupon_code = booking.get('coupon_code', '')
        
        # Update booking as paid
        cursor.execute("""
            UPDATE bookings 
            SET payment_status = 'paid', 
                status = 'confirmed'
            WHERE booking_id = %s
        """, (booking_id,))
        
        transaction_id = f"PAYMONGO_{booking_id}_{uuid.uuid4().hex[:6]}"
        cursor.execute("""
            INSERT INTO payments (booking_id, amount, payment_method, transaction_id, status)
            VALUES (%s, %s, %s, %s, 'completed')
        """, (booking_id, total_amount * 1.12, 'online', transaction_id))
        
        conn.commit()
        
        booking_data = {
            'booking_id': booking_id,
            'guest_name': booking['guest_name'],
            'guest_email': booking['guest_email'],
            'guest_phone': booking['guest_phone'],
            'room_number': booking['room_number'],
            'type_name': booking['type_name'],
            'check_in_date': str(booking['check_in_date']),
            'check_out_date': str(booking['check_out_date']),
            'nights': nights,
            'total_amount': total_amount,
            'payment_status': 'paid',
            'payment_method': 'GCash via PayMongo',
            'discount_amount': discount_amount,
            'coupon_code': coupon_code,
            'room_type': booking.get('type_name', 'Standard')
        }
        
        cursor.close()
        conn.close()
        
        # Send email
        email_service.send_payment_receipt(booking, transaction_id, 'GCash via PayMongo')
        
        return jsonify({
            'success': True,
            'receipt_data': booking_data
        })
        
    except Exception as e:
        print(f"Payment success error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)})


@payment_bp.route('/process-counter-payment', methods=['POST'])
def process_counter_payment():
    """Process pay at counter with PDF download"""
    try:
        booking_id = request.form.get('booking_id')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT b.*, r.room_number, rt.type_name 
            FROM bookings b
            JOIN rooms r ON b.room_id = r.room_id
            JOIN room_types rt ON r.type_id = rt.type_id
            WHERE b.booking_id = %s
        """, (booking_id,))
        
        booking = cursor.fetchone()
        
        if not booking:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Booking not found'})
        
        ticket_number = f"HTL{datetime.now().strftime('%Y%m%d%H%M%S')}{booking_id}"
        
        cursor.execute("""
            UPDATE bookings 
            SET payment_status = 'pending', 
                status = 'confirmed'
            WHERE booking_id = %s
        """, (booking_id,))
        
        conn.commit()
        
        nights = (datetime.strptime(str(booking['check_out_date']), '%Y-%m-%d') - 
                 datetime.strptime(str(booking['check_in_date']), '%Y-%m-%d')).days
        
        # Get discount amount and coupon code
        discount_amount = float(booking.get('discount_amount', 0)) if booking.get('discount_amount') else 0
        coupon_code = booking.get('coupon_code', '')
        
        booking_data = {
            'booking_id': booking_id,
            'guest_name': booking['guest_name'],
            'guest_email': booking['guest_email'],
            'guest_phone': booking['guest_phone'],
            'room_number': booking['room_number'],
            'type_name': booking['type_name'],
            'check_in_date': booking['check_in_date'],
            'check_out_date': booking['check_out_date'],
            'nights': nights,
            'total_amount': float(booking['total_amount']),
            'payment_status': 'pending',
            'discount_amount': discount_amount,
            'coupon_code': coupon_code
        }
        
        print(f"📊 Counter PDF Data - Discount: ${discount_amount}, Coupon: {coupon_code}")
        
        pdf_path = generate_booking_ticket(booking_data, ticket_number)
        
        cursor.close()
        conn.close()
        
        email_service.send_booking_confirmation(booking, 'Pay at Counter', ticket_number)
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"hotel_ticket_{ticket_number}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"Counter payment error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@payment_bp.route('/ticket/<int:booking_id>')
def view_ticket(booking_id):
    """View booking ticket HTML version"""
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        if not conn:
            return "Database connection failed", 500
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT b.*, r.room_number, rt.type_name 
            FROM bookings b
            JOIN rooms r ON b.room_id = r.room_id
            JOIN room_types rt ON r.type_id = rt.type_id
            WHERE b.booking_id = %s
        """, (booking_id,))
        
        booking = cursor.fetchone()
        
        if not booking:
            return "Booking not found", 404
        
        cursor.execute("""
            SELECT transaction_id, payment_method 
            FROM payments 
            WHERE booking_id = %s 
            LIMIT 1
        """, (booking_id,))
        
        payment = cursor.fetchone()
        cursor.close()
        
        if payment:
            booking['transaction_id'] = payment.get('transaction_id')
            booking['payment_method'] = payment.get('payment_method')
        else:
            booking['transaction_id'] = None
            booking['payment_method'] = 'Counter'
        
        if booking.get('created_at'):
            if isinstance(booking['created_at'], datetime):
                date_str = booking['created_at'].strftime('%Y%m%d')
            else:
                date_str = datetime.now().strftime('%Y%m%d')
        else:
            date_str = datetime.now().strftime('%Y%m%d')
        
        ticket_number = f"HTL{date_str}{booking_id:04d}"
        
        check_in = datetime.strptime(str(booking['check_in_date']), '%Y-%m-%d')
        check_out = datetime.strptime(str(booking['check_out_date']), '%Y-%m-%d')
        nights = (check_out - check_in).days
        
        total_amount = float(booking['total_amount']) if booking['total_amount'] else 0
        vat = total_amount * 0.07
        service = total_amount * 0.05
        grand_total = total_amount + vat + service
        
        conn.close()
        
        return render_template('ticket.html', 
                              booking=booking, 
                              ticket_number=ticket_number,
                              nights=nights,
                              total_amount=total_amount,
                              vat=vat,
                              service=service,
                              grand_total=grand_total)
    
    except Exception as e:
        print(f"Ticket error: {e}")
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass
        return f"Error loading ticket: {str(e)}", 500
    
    
@payment_bp.route('/process-counter-payment-json', methods=['POST'])
def process_counter_payment_json():
    """Process pay at counter and return JSON with receipt data + send email"""
    try:
        booking_id = request.form.get('booking_id')
        
        print(f"Processing counter payment for booking ID: {booking_id}")
        
        if not booking_id:
            return jsonify({'success': False, 'message': 'Booking ID is required'})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT b.*, r.room_number, rt.type_name 
            FROM bookings b
            JOIN rooms r ON b.room_id = r.room_id
            JOIN room_types rt ON r.type_id = rt.type_id
            WHERE b.booking_id = %s
        """, (booking_id,))
        
        booking = cursor.fetchone()
        
        if not booking:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Booking not found'})
        
        print(f"Found booking: {booking['guest_name']} - Room {booking['room_number']}")
        
        # Update booking status to confirmed (keeps payment_status as pending)
        cursor.execute("""
            UPDATE bookings 
            SET status = 'confirmed'
            WHERE booking_id = %s
        """, (booking_id,))
        
        conn.commit()
        
        # Calculate nights
        check_in = datetime.strptime(str(booking['check_in_date']), '%Y-%m-%d')
        check_out = datetime.strptime(str(booking['check_out_date']), '%Y-%m-%d')
        nights = (check_out - check_in).days
        
        # Get discount amount and coupon code
        discount_amount = float(booking.get('discount_amount', 0)) if booking.get('discount_amount') else 0
        coupon_code = booking.get('coupon_code', '')
        
        # Generate ticket number
        ticket_number = f"HTL{datetime.now().strftime('%Y%m%d%H%M%S')}{booking_id}"
        
        # Prepare receipt data
        booking_data = {
            'booking_id': booking['booking_id'],
            'guest_name': booking['guest_name'],
            'guest_email': booking.get('guest_email', ''),
            'guest_phone': booking.get('guest_phone', ''),
            'room_number': booking['room_number'],
            'type_name': booking.get('type_name', 'Standard'),
            'check_in_date': str(booking['check_in_date']),
            'check_out_date': str(booking['check_out_date']),
            'nights': nights,
            'total_amount': float(booking['total_amount']),
            'payment_status': 'pending',
            'payment_method': 'Pay at Counter',
            'discount_amount': discount_amount,
            'coupon_code': coupon_code,
            'room_type': booking.get('type_name', 'Standard')
        }
        
        cursor.close()
        conn.close()
        
        # 🔔 SEND EMAIL for counter payment (same as GCash but with counter payment note)
        try:
            email_service.send_booking_confirmation(booking, 'Pay at Counter', ticket_number)
            print(f"✅ Counter payment confirmation email sent to {booking['guest_email']}")
        except Exception as email_err:
            print(f"⚠️ Email sending failed but booking is confirmed: {email_err}")
        
        print(f"Receipt data prepared: {booking_data}")
        
        return jsonify({
            'success': True,
            'message': 'Booking confirmed! A confirmation email has been sent.',
            'receipt_data': booking_data
        })
        
    except Exception as e:
        print(f"Counter payment error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)})
