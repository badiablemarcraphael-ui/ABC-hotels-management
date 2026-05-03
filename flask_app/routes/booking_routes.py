from flask import Blueprint, request, jsonify, session
import sys
import os
from decimal import Decimal
from datetime import datetime
import json
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask_app.db_config import get_db_connection

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/create', methods=['POST'])
def create_booking():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get form data
        guest_name = request.form.get('guest_name')
        guest_email = request.form.get('guest_email')
        guest_phone = request.form.get('guest_phone')
        room_id = request.form.get('room_id')
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')
        adults = request.form.get('adults', 1)
        children = request.form.get('children', 0)
        coupon_code = request.form.get('coupon_code')
        
        # Calculate nights
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
        nights = (check_out_date - check_in_date).days
        
        # Get room price
        cursor.execute("""
            SELECT rt.base_price FROM rooms r
            JOIN room_types rt ON r.type_id = rt.type_id
            WHERE r.room_id = %s
        """, (room_id,))
        room = cursor.fetchone()
        base_price = Decimal(str(room[0])) if room else Decimal('100.00')
        
        # Calculate subtotal
        subtotal = base_price * Decimal(str(nights))
        
        # Apply coupon if provided
        discount_amount = Decimal('0.00')
        final_total = subtotal
        
        if coupon_code:
            cursor.execute("""
                SELECT * FROM coupons 
                WHERE coupon_code = %s 
                AND is_active = TRUE 
                AND (valid_from <= CURDATE() OR valid_from IS NULL)
                AND (valid_until >= CURDATE() OR valid_until IS NULL)
                AND used_count < usage_limit
            """, (coupon_code,))
            
            coupon = cursor.fetchone()
            
            if coupon:
                # coupon[0]=coupon_id, coupon[1]=coupon_code, coupon[2]=discount_type, coupon[3]=discount_value
                discount_value = Decimal(str(coupon[3]))
                if coupon[2] == 'percentage':
                    discount_amount = subtotal * (discount_value / Decimal('100.00'))
                else:
                    discount_amount = discount_value
                
                final_total = subtotal - discount_amount
                
                # Update coupon usage count
                cursor.execute("""
                    UPDATE coupons 
                    SET used_count = used_count + 1 
                    WHERE coupon_id = %s
                """, (coupon[0],))
                
                print(f"✅ Coupon {coupon_code} applied! Saved: ${discount_amount}")
        
        # Insert booking
        cursor.execute("""
            INSERT INTO bookings (guest_name, guest_email, guest_phone, room_id, 
            check_in_date, check_out_date, adults, children, total_amount, discount_amount, 
            coupon_code, status, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'confirmed', 'pending')
        """, (guest_name, guest_email, guest_phone, room_id, check_in, check_out, 
              adults, children, final_total, discount_amount, coupon_code))
        
        booking_id = cursor.lastrowid
        
        # Update room status
        cursor.execute("UPDATE rooms SET status = 'booked' WHERE room_id = %s", (room_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Calculate totals for payment page
        vat = float(final_total) * 0.07
        service = float(final_total) * 0.05
        grand_total = float(final_total) + vat + service
        
        return jsonify({
            'success': True, 
            'booking_id': booking_id, 
            'redirect': f'/api/payments/checkout/{booking_id}',
            'discount_applied': float(discount_amount),
            'final_total': float(final_total),
            'grand_total': grand_total,
            'message': f'Booking created! Coupon saved ${float(discount_amount):.2f}'
        })
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)})


@booking_bp.route('/validate-coupon', methods=['POST'])
def validate_coupon():
    """Validate coupon before booking"""
    try:
        coupon_code = request.form.get('coupon_code')
        total_amount = float(request.form.get('total_amount', 0))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM coupons 
            WHERE coupon_code = %s 
            AND is_active = TRUE 
            AND (valid_from <= CURDATE() OR valid_from IS NULL)
            AND (valid_until >= CURDATE() OR valid_until IS NULL)
            AND used_count < usage_limit
        """, (coupon_code,))
        
        coupon = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not coupon:
            return jsonify({'valid': False, 'message': 'Invalid or expired coupon code'})
        
        min_amount = float(coupon['min_booking_amount']) if coupon['min_booking_amount'] else 0
        if total_amount < min_amount:
            return jsonify({
                'valid': False, 
                'message': f'Minimum booking amount of ${min_amount:.2f} required'
            })
        
        discount_value = float(coupon['discount_value'])
        if coupon['discount_type'] == 'percentage':
            discount_amount = total_amount * (discount_value / 100)
        else:
            discount_amount = discount_value
        
        return jsonify({
            'valid': True,
            'discount_amount': discount_amount,
            'new_total': total_amount - discount_amount,
            'message': f'Coupon applied! You saved ${discount_amount:.2f}'
        })
        
    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)})
    
    
@booking_bp.route('/list', methods=['GET'])
def list_bookings():
    try:
        print("=" * 50)
        print("DEBUG: Fetching bookings from database...")
        
        conn = get_db_connection()
        
        if not conn:
            print("ERROR: Database connection failed!")
            return jsonify([])
        
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT b.*, r.room_number, rt.type_name 
            FROM bookings b
            LEFT JOIN rooms r ON b.room_id = r.room_id
            LEFT JOIN room_types rt ON r.type_id = rt.type_id
            ORDER BY b.created_at DESC
        """
        
        cursor.execute(query)
        bookings = cursor.fetchall()
        
        print(f"✅ Found {len(bookings)} bookings in database")
        
        # Convert Decimal to float for JSON serialization
        for booking in bookings:
            if 'total_amount' in booking and booking['total_amount'] is not None:
                booking['total_amount'] = float(booking['total_amount'])
            if 'discount_amount' in booking and booking['discount_amount'] is not None:
                booking['discount_amount'] = float(booking['discount_amount'])
        
        cursor.close()
        conn.close()
        
        return jsonify(bookings)
    
    except Exception as e:
        print(f"ERROR in list_bookings: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])

@booking_bp.route('/mark-paid/<int:booking_id>', methods=['POST'])
def mark_as_paid(booking_id):
    """Mark a counter payment booking as paid"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get booking details
        cursor.execute("SELECT * FROM bookings WHERE booking_id = %s", (booking_id,))
        booking = cursor.fetchone()
        
        if not booking:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Booking not found'})
        
        if booking['payment_status'] == 'paid':
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Booking is already paid'})
        
        # Update payment status to paid
        cursor.execute("""
            UPDATE bookings 
            SET payment_status = 'paid' 
            WHERE booking_id = %s
        """, (booking_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Payment for booking #{booking_id} has been marked as paid'
        })
    
    except Exception as e:
        print(f"Error marking as paid: {e}")
        return jsonify({'success': False, 'message': str(e)})

@booking_bp.route('/check-in/<int:booking_id>', methods=['POST'])
def check_in(booking_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE bookings 
            SET status = 'checked_in' 
            WHERE booking_id = %s AND status = 'confirmed'
        """, (booking_id,))
        
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        
        if affected:
            return jsonify({'success': True, 'message': 'Checked in successfully'})
        else:
            return jsonify({'success': False, 'message': 'Booking not found or already checked in'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@booking_bp.route('/check-out/<int:booking_id>', methods=['POST'])
def check_out(booking_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First, get booking details before updating
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
        
        if booking['status'] != 'checked_in':
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Booking is not in checked-in status'})
        
        # Update booking status
        cursor.execute("""
            UPDATE bookings 
            SET status = 'checked_out',
                check_out_date = CURDATE()
            WHERE booking_id = %s AND status = 'checked_in'
        """, (booking_id,))
        
        # Free the room
        cursor.execute("""
            UPDATE rooms r
            JOIN bookings b ON r.room_id = b.room_id
            SET r.status = 'available'
            WHERE b.booking_id = %s
        """, (booking_id,))
        
        conn.commit()
        
        # Get updated booking details
        cursor.execute("""
            SELECT b.*, r.room_number, rt.type_name 
            FROM bookings b
            JOIN rooms r ON b.room_id = r.room_id
            JOIN room_types rt ON r.type_id = rt.type_id
            WHERE b.booking_id = %s
        """, (booking_id,))
        
        updated_booking = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        # Convert Decimal to float for JSON serialization
        response_data = {
            'success': True,
            'message': 'Checked out successfully',
            'booking_id': updated_booking['booking_id'],
            'guest_name': updated_booking['guest_name'],
            'guest_email': updated_booking.get('guest_email', ''),
            'room_number': updated_booking['room_number'],
            'room_type': updated_booking.get('type_name', 'Standard'),
            'check_in_date': str(updated_booking['check_in_date']),
            'check_out_date': str(updated_booking['check_out_date']),
            'total_amount': float(updated_booking['total_amount']) if updated_booking.get('total_amount') else 0.00,
            'discount_amount': float(updated_booking['discount_amount']) if updated_booking.get('discount_amount') else 0.00,
            'payment_status': updated_booking.get('payment_status', 'pending'),
            'coupon_code': updated_booking.get('coupon_code', '')
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Error in check_out: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)})


@booking_bp.route('/get/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
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
        
        if booking and 'total_amount' in booking and booking['total_amount']:
            booking['total_amount'] = float(booking['total_amount'])
        if booking and 'discount_amount' in booking and booking['discount_amount']:
            booking['discount_amount'] = float(booking['discount_amount'])
        
        cursor.close()
        conn.close()
        
        if booking:
            return jsonify(booking)
        else:
            return jsonify({'error': 'Booking not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)})


@booking_bp.route('/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update booking status
        cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE booking_id = %s", (booking_id,))
        
        # Get room_id and free the room
        cursor.execute("SELECT room_id FROM bookings WHERE booking_id = %s", (booking_id,))
        result = cursor.fetchone()
        if result:
            room_id = result[0]
            cursor.execute("UPDATE rooms SET status = 'available' WHERE room_id = %s", (room_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@booking_bp.route('/comments/add', methods=['POST'])
def add_comment():
    try:
        booking_id = request.form.get('booking_id')
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        user_id = session.get('user_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO comments (booking_id, user_id, rating, comment)
            VALUES (%s, %s, %s, %s)
        """, (booking_id, user_id, rating, comment))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Review added successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
