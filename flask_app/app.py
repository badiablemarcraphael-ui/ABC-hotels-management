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


def create_app():
    """
    Application Factory Pattern
    Creates and configures the Flask application instance.
    """
    app = Flask(__name__)
    
    # ── Configuration ──
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'grand_hotel_secret_key_2025')
    
    # Session Security Settings
    app.config['SESSION_COOKIE_SECURE'] = False  # Set True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
    app.config['SESSION_COOKIE_NAME'] = 'grand_hotel_session'
    
    # Session Lifetime & Auto-Expiry
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)  # 8 hours max session
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Refresh session on each request
    app.config['SESSION_COOKIE_MAX_AGE'] = 28800  # 8 hours in seconds
    
    # Idle Timeout (30 minutes of inactivity)
    app.config['SESSION_IDLE_TIMEOUT'] = 1800  # 30 minutes in seconds
    
    # ── File Upload Configuration ──
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    
    # ── Enable CORS ──
    CORS(app, supports_credentials=True)
    
    # ── Register Session Middleware (Before Request) ──
    @app.before_request
    def check_session_timeout():
        """Check for session idle timeout on every request"""
        if session.get('logged_in'):
            now = time.time()
            last_activity = session.get('_last_activity', now)
            idle_timeout = app.config['SESSION_IDLE_TIMEOUT']
            
            # Check idle timeout
            if now - last_activity > idle_timeout:
                # Session expired due to inactivity
                session.clear()
                # If it's an API request, return JSON
                if request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'message': 'Session expired due to inactivity. Please login again.',
                        'session_expired': True
                    }), 401
                # For page requests, redirect to login
                return redirect(url_for('login_page', expired='idle'))
            
            # Update last activity timestamp
            session['_last_activity'] = now
            
            # Check absolute session expiry
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
        """Add security headers to all responses"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        return response
    
    # ── Register Custom Jinja2 Filters ──
    register_template_filters(app)
    
    # ── Register Blueprints (API Routes) ──
    register_blueprints(app)
    
    # ── Register Web Routes ──
    register_web_routes(app)
    
    # ── Register Error Handlers ──
    register_error_handlers(app)
    
    return app


def register_template_filters(app):
    """Register custom Jinja2 template filters."""
    
    @app.template_filter('float')
    def float_filter(value):
        """Convert value to float safely."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
    
    @app.template_filter('format_currency')
    def format_currency(value):
        """Format value as currency string."""
        try:
            return f"${float(value):,.2f}"
        except (TypeError, ValueError):
            return "$0.00"
    
    @app.template_filter('format_date')
    def format_date(value, fmt='%B %d, %Y'):
        """Format date string."""
        from datetime import datetime
        try:
            if isinstance(value, str):
                value = datetime.strptime(value, '%Y-%m-%d')
            return value.strftime(fmt)
        except (ValueError, TypeError):
            return str(value) if value else '—'


def register_blueprints(app):
    """Register all API blueprint routes."""
    
    # Import blueprints
    from routes.booking_routes import booking_bp
    from routes.room_routes import room_bp
    from routes.user_routes import user_bp
    from routes.report_routes import report_bp
    from routes.amenities_routes import amenities_bp
    from routes.payment_routes import payment_bp
    from routes.coupon_routes import coupon_bp
    from routes.comment_routes import comment_bp
    from routes.calendar_routes import calendar_bp
    
    # Register with URL prefixes
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
    
    from db_config import get_db_connection
    
    # ── Authentication Decorator ──
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                # Check if it's an API request
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
        """Decorator to restrict access based on user role."""
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
    
    # =============================================
    # PUBLIC ROUTES (No Login Required)
    # =============================================
    
    @app.route('/landing')
    def landing_page():
        """Public landing page - no login required"""
        if session.get('logged_in'):
            return redirect(url_for('dashboard'))
        return render_template('landing.html')
    
    @app.route('/')
    def index():
        """Redirect to landing page if not logged in"""
        if session.get('logged_in'):
            return redirect(url_for('dashboard'))
        return redirect(url_for('landing_page'))
    
    # =============================================
    # PUBLIC API ENDPOINTS (No Login Required)
    # =============================================
    
    @app.route('/browse-rooms')
    @login_required
    @role_required('guest')
    def browse_rooms():
        return render_template('browse_rooms.html')

    @app.route('/api/public/top-rooms')
    def public_top_rooms():
        """Get top rooms for landing page - public access"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT r.room_id, r.room_number, r.floor, r.status, r.image_path,
                       rt.type_name, rt.base_price, rt.capacity, rt.description
                FROM rooms r
                JOIN room_types rt ON r.type_id = rt.type_id
                WHERE r.status = 'available'
                ORDER BY rt.base_price ASC
                LIMIT 6
            """)
            
            rooms = cursor.fetchall()
            
            for room in rooms:
                room['base_price'] = float(room['base_price']) if room.get('base_price') else 0
                room['avg_rating'] = 4.5
                room['review_count'] = 0
                
                try:
                    cursor.execute("""
                        SELECT AVG(c.rating) as avg_rating, COUNT(*) as review_count
                        FROM comments c
                        JOIN bookings b ON c.booking_id = b.booking_id
                        WHERE b.room_id = %s
                    """, (room['room_id'],))
                    rating_data = cursor.fetchone()
                    if rating_data and rating_data['avg_rating']:
                        room['avg_rating'] = float(rating_data['avg_rating'])
                        room['review_count'] = int(rating_data['review_count'])
                except:
                    pass
            
            cursor.close()
            conn.close()
            
            print(f"✅ Landing page: Loaded {len(rooms)} rooms")
            return jsonify(rooms)
            
        except Exception as e:
            print(f"❌ Error fetching public rooms: {e}")
            import traceback
            traceback.print_exc()
            return jsonify([])
    
    @app.route('/api/public/top-reviews')
    def public_top_reviews():
        """Get top reviews for landing page - public access"""
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
                ORDER BY c.rating DESC, c.created_at DESC
                LIMIT 6
            """)
            
            reviews = cursor.fetchall()
            
            for review in reviews:
                if review.get('created_at'):
                    review['created_at'] = str(review['created_at'])
            
            cursor.close()
            conn.close()
            
            print(f"✅ Landing page: Loaded {len(reviews)} reviews")
            return jsonify(reviews)
            
        except Exception as e:
            print(f"❌ Error fetching public reviews: {e}")
            import traceback
            traceback.print_exc()
            return jsonify([])
    
    # =============================================
    # AUTHENTICATION ROUTES
    # =============================================
    @app.route('/login')
    def login_page():
        if session.get('logged_in'):
            return redirect(url_for('dashboard'))
        # Get expiration reason from query param
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
    
    # =============================================
    # SESSION INFO ENDPOINT
    # =============================================
    @app.route('/api/session-info')
    @login_required
    def session_info():
        """Get current session information"""
        now = time.time()
        last_activity = session.get('_last_activity', now)
        session_start = session.get('_session_start', now)
        idle_timeout = app.config['SESSION_IDLE_TIMEOUT']
        max_lifetime = app.config['PERMANENT_SESSION_LIFETIME'].total_seconds()
        
        idle_remaining = max(0, int(idle_timeout - (now - last_activity)))
        session_remaining = max(0, int(max_lifetime - (now - session_start)))
        
        return jsonify({
            'authenticated': True,
            'username': session.get('username'),
            'role': session.get('role'),
            'session_start': datetime.fromtimestamp(session_start).isoformat(),
            'last_activity': datetime.fromtimestamp(last_activity).isoformat(),
            'idle_timeout_seconds': idle_timeout,
            'idle_remaining_seconds': idle_remaining,
            'session_remaining_seconds': session_remaining,
            'session_remaining_hours': round(session_remaining / 3600, 1)
        })
    
    # =============================================
    # MAIN WEB ROUTES
    # =============================================
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
        
        template = dashboard_map.get(role, 'guest_dashboard.html')
        return render_template(template)
    
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
        return render_template('error.html', 
                              error_code=404,
                              error_message='Booking not found'), 404
    
    # =============================================
    # ANALYTICS API ENDPOINTS
    # =============================================
    @app.route('/api/analytics/occupancy')
    @login_required
    def occupancy_rate():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                DATE(check_in_date) as date,
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
            SELECT 
                r.room_number,
                rt.type_name,
                SUM(b.total_amount) as total_revenue
            FROM bookings b
            JOIN rooms r ON b.room_id = r.room_id
            JOIN room_types rt ON r.type_id = rt.type_id
            WHERE b.status = 'checked_out'
            GROUP BY r.room_id
            ORDER BY total_revenue DESC
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
            SELECT 
                DATE_FORMAT(check_in_date, '%%Y-%%m') as month,
                COUNT(*) as total_bookings,
                SUM(total_amount) as revenue
            FROM bookings
            WHERE check_in_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(check_in_date, '%%Y-%%m')
            ORDER BY month DESC
        """)
        
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data)
    
    @app.route('/api/reports/revenue')
    @login_required
    def revenue_report():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                DATE_FORMAT(check_in_date, '%Y-%m') as month,
                SUM(total_amount) as total_revenue
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
    
    @app.route('/api/analytics/top-guests')
    @login_required
    def top_guests():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT guest_name, COUNT(*) as total_stays, SUM(total_amount) as total_spent
            FROM bookings
            GROUP BY guest_name
            ORDER BY total_spent DESC
            LIMIT 5
        """)
        
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data)
    
    @app.route('/api/analytics/room-utilization')
    @login_required
    def room_utilization():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                rt.type_name,
                COUNT(r.room_id) as total_rooms,
                SUM(CASE WHEN r.status = 'booked' THEN 1 ELSE 0 END) as booked_rooms
            FROM room_types rt
            LEFT JOIN rooms r ON rt.type_id = r.type_id
            GROUP BY rt.type_id
        """)
        
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data)


def register_error_handlers(app):
    """Register custom error handlers."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', 
                         error_code='404',
                         error_title='Page Not Found',
                         error_message='The page you are looking for does not exist.',
                         error_details='Please check the URL or navigate back to the dashboard.'), 404

    @app.errorhandler(500)
    def internal_error(error):
         return render_template('error.html',
                         error_code='500',
                         error_title='Internal Server Error',
                         error_message='Something went wrong on our end.',
                         error_details='Our team has been notified. Please try again later.'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('error.html',
                         error_code='403',
                         error_title='Access Forbidden',
                         error_message='You do not have permission to access this page.',
                         error_details='Please contact an administrator if you believe this is an error.'), 403

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return render_template('error.html',
                             error_code='405',
                         error_title='Method Not Allowed',
                             error_message='The requested method is not allowed.',
                             error_details='Please check your request and try again.'), 405


# ── Allow running directly for development ──
# ── Application instance for gunicorn ──
app = create_app()

# ── Allow running directly for development ──
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