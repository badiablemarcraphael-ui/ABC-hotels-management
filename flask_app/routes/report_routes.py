from flask import Blueprint, jsonify, request
import sys
import os
from decimal import Decimal
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask_app.db_config import get_db_connection

report_bp = Blueprint('report', __name__)

@report_bp.route('/monthly-trends', methods=['GET'])
def monthly_trends():
    """Get monthly booking trends with date filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date and end_date:
            query = """
                SELECT 
                    DATE_FORMAT(check_in_date, '%Y-%m') as month,
                    COUNT(*) as total_bookings,
                    SUM(total_amount) as revenue,
                    AVG(DATEDIFF(check_out_date, check_in_date)) as avg_stay
                FROM bookings
                WHERE check_in_date BETWEEN %s AND %s
                GROUP BY DATE_FORMAT(check_in_date, '%Y-%m')
                ORDER BY month ASC
            """
            cursor.execute(query, (start_date, end_date))
        else:
            query = """
                SELECT 
                    DATE_FORMAT(check_in_date, '%Y-%m') as month,
                    COUNT(*) as total_bookings,
                    SUM(total_amount) as revenue,
                    AVG(DATEDIFF(check_out_date, check_in_date)) as avg_stay
                FROM bookings
                GROUP BY DATE_FORMAT(check_in_date, '%Y-%m')
                ORDER BY month ASC
            """
            cursor.execute(query)
        
        data = cursor.fetchall()
        
        # Convert Decimal to float
        for row in data:
            if row.get('revenue'):
                row['revenue'] = float(row['revenue'])
            if row.get('avg_stay'):
                row['avg_stay'] = float(row['avg_stay']) if row['avg_stay'] else 0
        
        cursor.close()
        conn.close()
        
        return jsonify(data)
    
    except Exception as e:
        print(f"Error in monthly_trends: {e}")
        return jsonify([])


@report_bp.route('/revenue-by-room', methods=['GET'])
def revenue_by_room():
    """Get revenue per room with date filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date and end_date:
            query = """
                SELECT 
                    r.room_number,
                    rt.type_name,
                    COUNT(b.booking_id) as total_bookings,
                    SUM(b.total_amount) as total_revenue
                FROM bookings b
                JOIN rooms r ON b.room_id = r.room_id
                JOIN room_types rt ON r.type_id = rt.type_id
                WHERE b.check_in_date BETWEEN %s AND %s
                GROUP BY r.room_id
                ORDER BY total_revenue DESC
                LIMIT 10
            """
            cursor.execute(query, (start_date, end_date))
        else:
            query = """
                SELECT 
                    r.room_number,
                    rt.type_name,
                    COUNT(b.booking_id) as total_bookings,
                    SUM(b.total_amount) as total_revenue
                FROM bookings b
                JOIN rooms r ON b.room_id = r.room_id
                JOIN room_types rt ON r.type_id = rt.type_id
                GROUP BY r.room_id
                ORDER BY total_revenue DESC
                LIMIT 10
            """
            cursor.execute(query)
        
        data = cursor.fetchall()
        
        for row in data:
            if row.get('total_revenue'):
                row['total_revenue'] = float(row['total_revenue'])
        
        cursor.close()
        conn.close()
        
        return jsonify(data)
    
    except Exception as e:
        print(f"Error in revenue_by_room: {e}")
        return jsonify([])

@report_bp.route('/occupancy-trend', methods=['GET'])
def occupancy_trend():
    """Get occupancy trend with date filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date and end_date:
            query = """
                SELECT 
                    DATE_FORMAT(check_in_date, '%Y-%m') as month,
                    COUNT(*) as total_bookings,
                    COUNT(DISTINCT room_id) as occupied_rooms
                FROM bookings
                WHERE check_in_date BETWEEN %s AND %s
                GROUP BY DATE_FORMAT(check_in_date, '%Y-%m')
                ORDER BY month ASC
            """
            cursor.execute(query, (start_date, end_date))
        else:
            query = """
                SELECT 
                    DATE_FORMAT(check_in_date, '%Y-%m') as month,
                    COUNT(*) as total_bookings,
                    COUNT(DISTINCT room_id) as occupied_rooms
                FROM bookings
                GROUP BY DATE_FORMAT(check_in_date, '%Y-%m')
                ORDER BY month ASC
            """
            cursor.execute(query)
        
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(data)
    
    except Exception as e:
        print(f"Error in occupancy_trend: {e}")
        return jsonify([])
    
    
@report_bp.route('/occupancy-rate', methods=['GET'])
def occupancy_rate():
    """Get occupancy rate with date filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Get total rooms
        cursor.execute("SELECT COUNT(*) as total FROM rooms")
        total_rooms = cursor.fetchone()
        total = total_rooms['total'] if total_rooms else 1
        
        if start_date and end_date:
            # Count booked rooms within date range
            query = """
                SELECT COUNT(DISTINCT room_id) as booked_rooms
                FROM bookings
                WHERE check_in_date <= %s AND check_out_date >= %s
                AND status IN ('confirmed', 'checked_in')
            """
            cursor.execute(query, (end_date, start_date))
        else:
            # Current occupancy
            query = """
                SELECT COUNT(DISTINCT room_id) as booked_rooms
                FROM bookings
                WHERE check_in_date <= CURDATE() AND check_out_date >= CURDATE()
                AND status IN ('confirmed', 'checked_in')
            """
            cursor.execute(query)
        
        result = cursor.fetchone()
        booked = result['booked_rooms'] if result else 0
        
        occupancy_rate = (booked / total * 100) if total > 0 else 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'occupancy_rate': round(occupancy_rate, 1),
            'booked_rooms': booked,
            'total_rooms': total
        })
    
    except Exception as e:
        print(f"Error in occupancy_rate: {e}")
        return jsonify({'occupancy_rate': 0, 'booked_rooms': 0, 'total_rooms': 0})


@report_bp.route('/status-distribution', methods=['GET'])
def status_distribution():
    """Get booking status distribution"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date and end_date:
            query = """
                SELECT 
                    status,
                    COUNT(*) as count
                FROM bookings
                WHERE check_in_date BETWEEN %s AND %s
                GROUP BY status
            """
            cursor.execute(query, (start_date, end_date))
        else:
            query = """
                SELECT 
                    status,
                    COUNT(*) as count
                FROM bookings
                GROUP BY status
            """
            cursor.execute(query)
        
        data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(data)
    
    except Exception as e:
        print(f"Error in status_distribution: {e}")
        return jsonify([])


@report_bp.route('/revenue', methods=['GET'])
def revenue_report():
    """Get revenue data for dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                DATE_FORMAT(check_in_date, '%Y-%m') as month,
                COALESCE(SUM(total_amount), 0) as total_revenue,
                COUNT(*) as total_bookings
            FROM bookings
            WHERE status != 'cancelled'
            GROUP BY DATE_FORMAT(check_in_date, '%Y-%m')
            ORDER BY month DESC
            LIMIT 12
        """)
        
        data = cursor.fetchall()
        
        for row in data:
            if row.get('total_revenue'):
                row['total_revenue'] = float(row['total_revenue'])
        
        cursor.close()
        conn.close()
        
        return jsonify(data)
    
    except Exception as e:
        print(f"Error in revenue_report: {e}")
        return jsonify([])
    
    
@report_bp.route('/debug-stats', methods=['GET'])
def debug_stats():
    """Get overall statistics for debugging"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total bookings
        cursor.execute("SELECT COUNT(*) as total FROM bookings")
        total_bookings = cursor.fetchone()
        
        # Total revenue
        cursor.execute("SELECT SUM(total_amount) as revenue FROM bookings")
        total_revenue = cursor.fetchone()
        
        # Bookings by status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM bookings 
            GROUP BY status
        """)
        status_counts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_bookings': total_bookings['total'] if total_bookings else 0,
            'total_revenue': float(total_revenue['revenue']) if total_revenue and total_revenue['revenue'] else 0,
            'status_counts': status_counts
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})
