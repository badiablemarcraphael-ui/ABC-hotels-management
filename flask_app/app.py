"""
Grand Hotel Management System — Application Factory
Flask Application with Blueprint Architecture
Enhanced with Session Security & Auto-Termination
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import os
from datetime import datetime, timedelta
import time
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_app():
    """
    Application Factory Pattern
    Creates and configures the Flask application instance.
    """
    app = Flask(__name__)
    
    # ── Configuration ──
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'grand_hotel_secret_key_2025')
    
    # Session Security Settings
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_NAME'] = 'grand_hotel_session'
    
    # Session Lifetime & Auto-Expiry
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True
    app.config['SESSION_COOKIE_MAX_AGE'] = 28800
    
    # Idle Timeout
    app.config['SESSION_IDLE_TIMEOUT'] = 1800
    
    # File Upload
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    
    # Enable CORS
    CORS(app, supports_credentials=True)
    
    # ── Session Middleware ──
    @app.before_request
    def check_session_timeout():
        if session.get('logged_in'):
            now = time.time()
            last_activity = session.get('_last_activity', now)
            idle_timeout = app.config['SESSION_IDLE_TIMEOUT']
            
            if now - last_activity > idle_timeout:
                session.clear()
                if request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'message': 'Session expired due to inactivity. Please login again.',
                        'session_expired': True
                    }), 401
                return redirect(url_for('login_page', expired='idle'))
            
            session['_last_activity'] = now
            
            session_start = session.get('_session_start', now)
            max_lifetime = app.config['PERMANENT_SESSION_LIFETIME'].total_seconds()
            
            if now - session_start > max_lifetime:
                session.clear()
                if request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'message': 'Session expired. Please login again.',
                        'session_expired': True
                    }), 401
                return redirect(url_for('login_page', expired='max'))
    
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        return response
    
    # ── Register Components ──
    register_template_filters(app)
    register_blueprints(app)
    register_web_routes(app)
    register_error_handlers(app)
    
    return app


def register_template_filters(app):
    @app.template_filter('float')
    def float_filter(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
    
    @app.template_filter('format_currency')
    def format_currency(value):
        try:
            return f"${float(value):,.2f}"
        except (TypeError, ValueError):
            return "$0.00"
    
    @app.template_filter('format_date')
    def format_date(value, fmt='%B %d, %Y'):
        from datetime import datetime
        try:
            if isinstance(value, str):
                value = datetime.strptime(value, '%Y-%m-%d')
            return value.strftime(fmt)
        except (ValueError, TypeError):
            return str(value) if value else '—'


def register_blueprints(app):
    """Register all API blueprint routes with lazy imports to save memory"""
    
    # Lazy import to avoid loading all services at startup
    from flask_app.routes.booking_routes import booking_bp
    from flask_app.routes.room_routes import room_bp
    from flask_app.routes.user_routes import user_bp
    from flask_app.routes.report_routes import report_bp
    from flask_app.routes.amenities_routes import amenities_bp
    from flask_app.routes.payment_routes import payment_bp
    from flask_app.routes.coupon_routes import coupon_bp
    from flask_app.routes.comment_routes import comment_bp
    from flask_app.routes.calendar_routes import calendar_bp
    
    blueprints = [
        (booking_bp, '/api/bookings'),
        (room_bp, '/api/rooms'),
        (user_bp, '/api/users'),
        (report_bp, '/api/reports'),
        (amenities_bp, '/api/amenities'),
        (payment_bp, '/api/payments'),
        (coupon_bp, '/api/coupons'),
        (comment_bp, '/api/comments'),
        (calendar_bp, '/api/calendar'),
    ]
    
    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)


def register_web_routes(app):
    """Register all web page routes and API endpoints."""
    
    from flask_app.db_config import get_db_connection
    
    # ── Auth Decorators ──
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                if request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'message': 'Session expired. Please login again.',
                        'session_expired': True
                    }), 401
                return redirect(url_for('login_page'))
            return f(*args, **kwargs)
        return decorated_function
    
    def role_required(*roles):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not session.get('logged_in'):
                    if request.path.startswith('/api/'):
                        return jsonify({
                            'success': False,
                            'message': 'Session expired. Please login again.',
                            'session_expired': True
                        }), 401
                    return redirect(url_for('login_page'))
                if session.get('role') not in roles:
                    return render_template('error.html', 
                                          error_code=403,
                                          error_message='Access Denied'), 403
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    # ── Public Routes ──
    @app.route('/landing')
    def landing_page():
        if session.get('logged_in'):
            return redirect(url_for('dashboard'))
        return render_template('landing.html')
    
    @app.route('/')
    def index():
        if session.get('logged_in'):
            return redirect(url_for('dashboard'))
        return redirect(url_for('landing_page'))
    
    @app.route('/login')
    def login_page():
        if session.get('logged_in'):
            return redirect(url_for('dashboard'))
        expired = request.args.get('expired', '')
        return render_template('login.html', expired=expired)
    
    @app.route('/register')
    def register_page():
        if session.get('logged_in'):
            return redirect(url_for('dashboard'))
        return render_template('register.html')
    
    @app.route('/guest-register')
    def guest_register_page():
        return render_template('guest_register.html')
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('landing_page'))
    
    # ── Session Info ──
    @app.route('/api/session-info')
    @login_required
    def session_info():
        now = time.time()
        last_activity = session.get('_last_activity', now)
        session_start = session.get('_session_start', now)
        idle_timeout = app.config['SESSION_IDLE_TIMEOUT']
        max_lifetime = app.config['PERMANENT_SESSION_LIFETIME'].total_seconds()
        
        return jsonify({
            'authenticated': True,
            'username': session.get('username'),
            'role': session.get('role'),
            'session_start': datetime.fromtimestamp(session_start).isoformat(),
            'last_activity': datetime.fromtimestamp(last_activity).isoformat(),
            'idle_remaining_seconds': max(0, int(idle_timeout - (now - last_activity))),
            'session_remaining_hours': round(max(0, int(max_lifetime - (now - session_start))) / 3600, 1)
        })
    
    # ── Dashboard ──
    @app.route('/dashboard')
    @login_required
    def dashboard():
        role = session.get('role', 'guest')
        dashboard_map = {
            'admin': 'dashboard.html',
            'receptionist': 'reception_dashboard.html',
            'manager': 'manager_dashboard.html',
            'guest': 'guest_dashboard.html'
        }
        return render_template(dashboard_map.get(role, 'guest_dashboard.html'))
    
    # ── Guest Routes ──
    @app.route('/browse-rooms')
    @login_required
    @role_required('guest')
    def browse_rooms():
        return render_template('browse_rooms.html')
    
    @app.route('/my-bookings')
    @login_required
    @role_required('guest')
    def my_bookings():
        return render_template('my_bookings.html')
    
    @app.route('/my-reviews')
    @login_required
    @role_required('guest')
    def my_reviews():
        return render_template('my_reviews.html')
    
    # ── Admin/Staff Routes ──
    @app.route('/bookings')
    @login_required
    @role_required('admin', 'receptionist', 'manager')
    def bookings():
        return render_template('bookings.html')
    
    @app.route('/rooms')
    @login_required
    @role_required('admin', 'receptionist', 'manager')
    def rooms():
        return render_template('rooms.html')
    
    @app.route('/amenities')
    @login_required
    @role_required('admin', 'manager')
    def amenities():
        return render_template('amenities.html')
    
    @app.route('/users')
    @login_required
    @role_required('admin', 'manager')
    def users():
        return render_template('users.html')
    
    @app.route('/reports')
    @login_required
    @role_required('admin', 'manager')
    def reports():
        return render_template('reports.html')
    
    @app.route('/reviews')
    @login_required
    def reviews():
        return render_template('reviews.html')
    
    @app.route('/coupons')
    @login_required
    @role_required('admin', 'manager')
    def coupons():
        return render_template('coupons.html')
    
    @app.route('/calendar')
    @login_required
    @role_required('admin', 'receptionist', 'manager', 'guest')
    def calendar():
        return render_template('calendar.html')
    
    @app.route('/checkout')
    @login_required
    @role_required('admin', 'receptionist')
    def checkout():
        return render_template('checkout.html')
    
    @app.route('/receipt/<int:booking_id>')
    @login_required
    def view_receipt(booking_id):
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
        if booking:
            return render_template('receipt.html', booking=booking)
        return render_template('error.html', error_code=404, error_message='Booking not found'), 404
    
    # ── Public APIs ──
    @app.route('/api/public/top-rooms')
    def public_top_rooms():
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.room_id, r.room_number, r.floor, r.status, r.image_path,
                       rt.type_name, rt.base_price, rt.capacity, rt.description
                FROM rooms r
                JOIN room_types rt ON r.type_id = rt.type_id
                WHERE r.status = 'available'
                ORDER BY rt.base_price ASC LIMIT 6
            """)
            rooms = cursor.fetchall()
            for room in rooms:
                room['base_price'] = float(room['base_price']) if room.get('base_price') else 0
                room['avg_rating'] = 4.5
                room['review_count'] = 0
            cursor.close()
            conn.close()
            return jsonify(rooms)
        except Exception as e:
            print(f"Error fetching public rooms: {e}")
            return jsonify([])
    
    @app.route('/api/public/top-reviews')
    def public_top_reviews():
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.comment_id, c.rating, c.comment, c.image_path, c.created_at,
                       b.guest_name, r.room_number, rt.type_name
                FROM comments c
                LEFT JOIN bookings b ON c.booking_id = b.booking_id
                LEFT JOIN rooms r ON b.room_id = r.room_id
                LEFT JOIN room_types rt ON r.type_id = rt.type_id
                ORDER BY c.rating DESC, c.created_at DESC LIMIT 6
            """)
            reviews = cursor.fetchall()
            for review in reviews:
                if review.get('created_at'):
                    review['created_at'] = str(review['created_at'])
            cursor.close()
            conn.close()
            return jsonify(reviews)
        except Exception as e:
            print(f"Error fetching public reviews: {e}")
            return jsonify([])
    
    # ── Analytics APIs ──
    @app.route('/api/analytics/occupancy')
    @login_required
    def occupancy_rate():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT DATE(check_in_date) as date,
                COUNT(CASE WHEN status IN ('confirmed', 'checked_in') THEN 1 END) as booked_rooms,
                (SELECT COUNT(*) FROM rooms) as total_rooms
            FROM bookings
            WHERE check_in_date <= CURDATE() AND check_out_date >= CURDATE()
            GROUP BY DATE(check_in_date)
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data)
    
    @app.route('/api/analytics/revenue-per-room')
    @login_required
    def revenue_per_room():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.room_number, rt.type_name, SUM(b.total_amount) as total_revenue
            FROM bookings b
            JOIN rooms r ON b.room_id = r.room_id
            JOIN room_types rt ON r.type_id = rt.type_id
            WHERE b.status = 'checked_out'
            GROUP BY r.room_id ORDER BY total_revenue DESC
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data)
    
    @app.route('/api/analytics/monthly-trends')
    @login_required
    def monthly_trends():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT DATE_FORMAT(check_in_date, '%Y-%m') as month,
                COUNT(*) as total_bookings, SUM(total_amount) as revenue
            FROM bookings
            WHERE check_in_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(check_in_date, '%Y-%m')
            ORDER BY month DESC
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data)


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', error_code='404', error_title='Page Not Found',
                         error_message='The page you are looking for does not exist.'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', error_code='500', error_title='Internal Server Error',
                         error_message='Something went wrong on our end.'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('error.html', error_code='403', error_title='Access Forbidden',
                         error_message='You do not have permission to access this page.'), 403


# ── App instance for gunicorn ──
app = create_app()

# ── Development server ──
if __name__ == '__main__':
    import socket
    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    try:
        port = 5000
        app.run(debug=True, port=port, host='127.0.0.1')
    except OSError:
        port = find_free_port()
        print(f"Port 5000 in use. Starting on port {port}")
        app.run(debug=True, port=port, host='127.0.0.1')