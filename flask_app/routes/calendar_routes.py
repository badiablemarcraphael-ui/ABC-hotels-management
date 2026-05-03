from flask import Blueprint, jsonify, request
import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config import get_db_connection

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/bookings-for-calendar', methods=['GET'])
def bookings_for_calendar():
    """Get bookings formatted specifically for calendar display"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get date range from query params (optional)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        month = request.args.get('month')
        year = request.args.get('year')
        
        # Build query based on filters
        if month and year:
            # Get bookings for specific month
            query = """
                SELECT 
                    b.booking_id,
                    b.guest_name,
                    b.guest_email,
                    b.guest_phone,
                    b.room_id,
                    b.check_in_date,
                    b.check_out_date,
                    b.adults,
                    b.children,
                    b.total_amount,
                    b.discount_amount,
                    b.coupon_code,
                    b.status,
                    b.payment_status,
                    b.created_at,
                    r.room_number,
                    rt.type_name as room_type_name,
                    rt.base_price
                FROM bookings b
                LEFT JOIN rooms r ON b.room_id = r.room_id
                LEFT JOIN room_types rt ON r.type_id = rt.type_id
                WHERE b.status NOT IN ('cancelled', 'checked_out')
                AND (
                    (b.check_in_date BETWEEN %s AND %s)
                    OR (b.check_out_date BETWEEN %s AND %s)
                    OR (b.check_in_date <= %s AND b.check_out_date >= %s)
                )
                ORDER BY b.check_in_date ASC
            """
            first_day = f"{year}-{month}-01"
            last_day = f"{year}-{month}-31"
            cursor.execute(query, (first_day, last_day, first_day, last_day, first_day, first_day))
        elif start_date and end_date:
            query = """
                SELECT 
                    b.booking_id,
                    b.guest_name,
                    b.guest_email,
                    b.guest_phone,
                    b.room_id,
                    b.check_in_date,
                    b.check_out_date,
                    b.adults,
                    b.children,
                    b.total_amount,
                    b.discount_amount,
                    b.coupon_code,
                    b.status,
                    b.payment_status,
                    b.created_at,
                    r.room_number,
                    rt.type_name as room_type_name,
                    rt.base_price
                FROM bookings b
                LEFT JOIN rooms r ON b.room_id = r.room_id
                LEFT JOIN room_types rt ON r.type_id = rt.type_id
                WHERE b.status NOT IN ('cancelled', 'checked_out')
                AND (
                    (b.check_in_date BETWEEN %s AND %s)
                    OR (b.check_out_date BETWEEN %s AND %s)
                    OR (b.check_in_date <= %s AND b.check_out_date >= %s)
                )
                ORDER BY b.check_in_date ASC
            """
            cursor.execute(query, (start_date, end_date, start_date, end_date, start_date, start_date))
        else:
            # Get all active bookings (last 6 months and next 6 months)
            six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            six_months_later = (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')
            
            query = """
                SELECT 
                    b.booking_id,
                    b.guest_name,
                    b.guest_email,
                    b.guest_phone,
                    b.room_id,
                    b.check_in_date,
                    b.check_out_date,
                    b.adults,
                    b.children,
                    b.total_amount,
                    b.discount_amount,
                    b.coupon_code,
                    b.status,
                    b.payment_status,
                    b.created_at,
                    r.room_number,
                    rt.type_name as room_type_name,
                    rt.base_price
                FROM bookings b
                LEFT JOIN rooms r ON b.room_id = r.room_id
                LEFT JOIN room_types rt ON r.type_id = rt.type_id
                WHERE b.status NOT IN ('cancelled', 'checked_out')
                AND b.check_out_date >= %s
                ORDER BY b.check_in_date ASC
            """
            cursor.execute(query, (six_months_ago,))
        
        bookings = cursor.fetchall()
        
        # Convert Decimal to float and format dates
        for booking in bookings:
            if booking.get('total_amount'):
                booking['total_amount'] = float(booking['total_amount'])
            if booking.get('discount_amount'):
                booking['discount_amount'] = float(booking['discount_amount'])
            if booking.get('base_price'):
                booking['base_price'] = float(booking['base_price'])
            
            # Format dates as strings
            if booking.get('check_in_date'):
                booking['check_in_date'] = booking['check_in_date'].strftime('%Y-%m-%d')
            if booking.get('check_out_date'):
                booking['check_out_date'] = booking['check_out_date'].strftime('%Y-%m-%d')
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'bookings': bookings,
            'count': len(bookings)
        })
    
    except Exception as e:
        print(f"Error in bookings_for_calendar: {e}")
        return jsonify({'success': False, 'error': str(e), 'bookings': []})


@calendar_bp.route('/today-activity', methods=['GET'])
def today_activity():
    """Get today's check-ins, check-outs, and currently staying guests"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get today's check-ins
        cursor.execute("""
            SELECT 
                b.booking_id,
                b.guest_name,
                b.guest_email,
                b.guest_phone,
                b.room_id,
                b.check_in_date,
                b.check_out_date,
                b.adults,
                b.children,
                b.status,
                r.room_number,
                rt.type_name as room_type
            FROM bookings b
            LEFT JOIN rooms r ON b.room_id = r.room_id
            LEFT JOIN room_types rt ON r.type_id = rt.type_id
            WHERE b.check_in_date = %s
            AND b.status NOT IN ('cancelled', 'checked_out')
            ORDER BY b.guest_name
        """, (today,))
        checkins = cursor.fetchall()
        
        # Get today's check-outs
        cursor.execute("""
            SELECT 
                b.booking_id,
                b.guest_name,
                b.guest_email,
                b.guest_phone,
                b.room_id,
                b.check_in_date,
                b.check_out_date,
                b.adults,
                b.children,
                b.status,
                r.room_number,
                rt.type_name as room_type
            FROM bookings b
            LEFT JOIN rooms r ON b.room_id = r.room_id
            LEFT JOIN room_types rt ON r.type_id = rt.type_id
            WHERE b.check_out_date = %s
            AND b.status NOT IN ('cancelled', 'checked_out')
            ORDER BY b.guest_name
        """, (today,))
        checkouts = cursor.fetchall()
        
        # Get currently staying (checked in and within date range)
        cursor.execute("""
            SELECT 
                b.booking_id,
                b.guest_name,
                b.guest_email,
                b.guest_phone,
                b.room_id,
                b.check_in_date,
                b.check_out_date,
                b.adults,
                b.children,
                b.status,
                r.room_number,
                rt.type_name as room_type
            FROM bookings b
            LEFT JOIN rooms r ON b.room_id = r.room_id
            LEFT JOIN room_types rt ON r.type_id = rt.type_id
            WHERE b.check_in_date <= %s 
            AND b.check_out_date >= %s
            AND b.status = 'checked_in'
            ORDER BY b.guest_name
        """, (today, today))
        currently_staying = cursor.fetchall()
        
        # Format dates for response
        for item in checkins:
            if item.get('check_in_date'):
                item['check_in_date'] = item['check_in_date'].strftime('%Y-%m-%d')
            if item.get('check_out_date'):
                item['check_out_date'] = item['check_out_date'].strftime('%Y-%m-%d')
        
        for item in checkouts:
            if item.get('check_in_date'):
                item['check_in_date'] = item['check_in_date'].strftime('%Y-%m-%d')
            if item.get('check_out_date'):
                item['check_out_date'] = item['check_out_date'].strftime('%Y-%m-%d')
        
        for item in currently_staying:
            if item.get('check_in_date'):
                item['check_in_date'] = item['check_in_date'].strftime('%Y-%m-%d')
            if item.get('check_out_date'):
                item['check_out_date'] = item['check_out_date'].strftime('%Y-%m-%d')
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'checkins': checkins,
            'checkouts': checkouts,
            'currently_staying': currently_staying,
            'stats': {
                'checkins_count': len(checkins),
                'checkouts_count': len(checkouts),
                'currently_staying_count': len(currently_staying)
            }
        })
    
    except Exception as e:
        print(f"Error in today_activity: {e}")
        return jsonify({'success': False, 'error': str(e)})


@calendar_bp.route('/monthly-summary', methods=['GET'])
def monthly_summary():
    """Get summary statistics for a specific month"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        month = request.args.get('month')
        year = request.args.get('year')
        
        if not month or not year:
            today = datetime.now()
            month = str(today.month)
            year = str(today.year)
        
        first_day = f"{year}-{month}-01"
        # Get last day of month
        if int(month) == 12:
            last_day = f"{int(year)+1}-01-01"
        else:
            last_day = f"{year}-{int(month)+1}-01"
        
        # Get monthly statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_bookings,
                SUM(total_amount) as total_revenue,
                COUNT(DISTINCT CASE WHEN status = 'checked_in' THEN booking_id END) as checked_in_count,
                COUNT(DISTINCT CASE WHEN check_in_date BETWEEN %s AND %s THEN booking_id END) as checkins_this_month,
                COUNT(DISTINCT CASE WHEN check_out_date BETWEEN %s AND %s THEN booking_id END) as checkouts_this_month
            FROM bookings
            WHERE check_in_date <= %s 
            AND status NOT IN ('cancelled', 'checked_out')
        """, (first_day, last_day, first_day, last_day, last_day))
        
        stats = cursor.fetchone()
        
        if stats.get('total_revenue'):
            stats['total_revenue'] = float(stats['total_revenue']) if stats['total_revenue'] else 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'month': month,
            'year': year,
            'stats': stats
        })
    
    except Exception as e:
        print(f"Error in monthly_summary: {e}")
        return jsonify({'success': False, 'error': str(e)})


@calendar_bp.route('/room-availability', methods=['GET'])
def room_availability():
    """Get room availability for a specific date range"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        check_in = request.args.get('check_in')
        check_out = request.args.get('check_out')
        
        if not check_in or not check_out:
            return jsonify({'success': False, 'error': 'Missing dates'})
        
        # Get all rooms
        cursor.execute("SELECT room_id, room_number, type_id FROM rooms WHERE status = 'available'")
        all_rooms = cursor.fetchall()
        
        # Get booked rooms for the date range
        cursor.execute("""
            SELECT DISTINCT room_id
            FROM bookings
            WHERE status NOT IN ('cancelled', 'checked_out')
            AND (
                (check_in_date <= %s AND check_out_date >= %s)
                OR (check_in_date BETWEEN %s AND %s)
                OR (check_out_date BETWEEN %s AND %s)
            )
        """, (check_out, check_in, check_in, check_out, check_in, check_out))
        
        booked_rooms = cursor.fetchall()
        booked_room_ids = [room['room_id'] for room in booked_rooms]
        
        # Filter available rooms
        available_rooms = [room for room in all_rooms if room['room_id'] not in booked_room_ids]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'available_rooms': available_rooms,
            'available_count': len(available_rooms),
            'total_rooms': len(all_rooms),
            'booked_count': len(booked_room_ids)
        })
    
    except Exception as e:
        print(f"Error in room_availability: {e}")
        return jsonify({'success': False, 'error': str(e)})


@calendar_bp.route('/booking-details/<int:booking_id>', methods=['GET'])
def booking_details(booking_id):
    """Get detailed information for a specific booking"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                b.*,
                r.room_number,
                rt.type_name as room_type,
                rt.base_price,
                rt.capacity,
                (SELECT COUNT(*) FROM payments WHERE booking_id = b.booking_id AND status = 'completed') as payment_count,
                (SELECT SUM(amount) FROM payments WHERE booking_id = b.booking_id AND status = 'completed') as total_paid
            FROM bookings b
            LEFT JOIN rooms r ON b.room_id = r.room_id
            LEFT JOIN room_types rt ON r.type_id = rt.type_id
            WHERE b.booking_id = %s
        """, (booking_id,))
        
        booking = cursor.fetchone()
        
        if booking:
            # Convert Decimal to float
            for field in ['total_amount', 'discount_amount', 'base_price', 'total_paid']:
                if booking.get(field):
                    booking[field] = float(booking[field])
            
            # Format dates
            if booking.get('check_in_date'):
                booking['check_in_date'] = booking['check_in_date'].strftime('%Y-%m-%d')
            if booking.get('check_out_date'):
                booking['check_out_date'] = booking['check_out_date'].strftime('%Y-%m-%d')
            if booking.get('created_at'):
                booking['created_at'] = booking['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'booking': booking
        })
    
    except Exception as e:
        print(f"Error in booking_details: {e}")
        return jsonify({'success': False, 'error': str(e)})