from flask import Blueprint, request, jsonify, session
import sys
import os
from datetime import datetime
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config import get_db_connection

comment_bp = Blueprint('comment', __name__)

# Configure upload folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@comment_bp.route('/list', methods=['GET'])
def list_comments():
    """Get comments - filters based on user role"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        user_role = session.get('role', 'guest')
        
        # Admin sees all comments (for moderation)
        # Non-admin users only see approved comments
        if user_role == 'admin':
            cursor.execute("""
                SELECT c.*, b.guest_name
                FROM comments c
                LEFT JOIN bookings b ON c.booking_id = b.booking_id
                ORDER BY 
                    CASE c.status 
                        WHEN 'pending' THEN 0 
                        WHEN 'approved' THEN 1 
                        WHEN 'rejected' THEN 2 
                    END,
                    c.created_at DESC
            """)
        else:
            cursor.execute("""
                SELECT c.*, b.guest_name
                FROM comments c
                LEFT JOIN bookings b ON c.booking_id = b.booking_id
                WHERE c.status = 'approved'
                ORDER BY c.created_at DESC
            """)
        
        comments = cursor.fetchall()
        
        # Convert datetime to string for JSON serialization
        for comment in comments:
            if comment.get('created_at'):
                comment['created_at'] = comment['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if comment.get('moderated_at'):
                comment['moderated_at'] = comment['moderated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.close()
        conn.close()
        
        return jsonify(comments)
    
    except Exception as e:
        print(f"Error in list_comments: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])

@comment_bp.route('/my-comments', methods=['GET'])
def my_comments():
    """Get comments submitted by the current user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify([])
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT c.*, b.guest_name, b.room_id, r.room_number
            FROM comments c
            LEFT JOIN bookings b ON c.booking_id = b.booking_id
            LEFT JOIN rooms r ON b.room_id = r.room_id
            WHERE c.user_id = %s
            ORDER BY c.created_at DESC
        """, (user_id,))
        
        comments = cursor.fetchall()
        
        for comment in comments:
            if comment.get('created_at'):
                comment['created_at'] = comment['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if comment.get('moderated_at'):
                comment['moderated_at'] = comment['moderated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.close()
        conn.close()
        
        return jsonify(comments)
    
    except Exception as e:
        print(f"Error in my_comments: {e}")
        return jsonify([])

@comment_bp.route('/pending-count', methods=['GET'])
def pending_count():
    """Get count of pending comments for admin dashboard"""
    try:
        if session.get('role') != 'admin':
            return jsonify({'count': 0})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM comments WHERE status = 'pending'")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({'count': result[0] if result else 0})
    
    except Exception as e:
        return jsonify({'count': 0})

@comment_bp.route('/count', methods=['GET'])
def comment_count():
    """Get total number of approved comments"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM comments WHERE status = 'approved'")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({'total': result[0] if result else 0})
    except Exception as e:
        return jsonify({'total': 0, 'error': str(e)})

@comment_bp.route('/dashboard-stats', methods=['GET'])
def dashboard_stats():
    """Get review statistics for dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get approved comments only for stats
        cursor.execute("SELECT * FROM comments WHERE status = 'approved'")
        all_comments = cursor.fetchall()
        
        total_reviews = len(all_comments)
        
        if total_reviews > 0:
            total_rating = sum(c['rating'] for c in all_comments)
            avg_rating = total_rating / total_reviews
            
            five_stars = sum(1 for c in all_comments if c['rating'] == 5)
            four_stars = sum(1 for c in all_comments if c['rating'] == 4)
            three_stars = sum(1 for c in all_comments if c['rating'] == 3)
            two_stars = sum(1 for c in all_comments if c['rating'] == 2)
            one_star = sum(1 for c in all_comments if c['rating'] == 1)
            with_photos = sum(1 for c in all_comments if c.get('image_path') and c['image_path'] != '')
        else:
            avg_rating = 0
            five_stars = four_stars = three_stars = two_stars = one_star = with_photos = 0
        
        # Get recent approved reviews (only last 5 for dashboard display)
        cursor.execute("""
            SELECT c.*, b.guest_name
            FROM comments c
            LEFT JOIN bookings b ON c.booking_id = b.booking_id
            WHERE c.status = 'approved'
            ORDER BY c.created_at DESC
            LIMIT 5
        """)
        
        recent_reviews = cursor.fetchall()
        
        for review in recent_reviews:
            if review.get('created_at'):
                review['created_at'] = review['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_reviews': total_reviews,
            'avg_rating': round(avg_rating, 1),
            'five_stars': five_stars,
            'four_stars': four_stars,
            'three_stars': three_stars,
            'two_stars': two_stars,
            'one_star': one_star,
            'with_photos': with_photos,
            'recent_reviews': recent_reviews
        })
    
    except Exception as e:
        print(f"Error in dashboard_stats: {e}")
        return jsonify({
            'total_reviews': 0,
            'avg_rating': 0,
            'five_stars': 0,
            'four_stars': 0,
            'three_stars': 0,
            'two_stars': 0,
            'one_star': 0,
            'with_photos': 0,
            'recent_reviews': []
        })

@comment_bp.route('/add', methods=['POST'])
def add_comment():
    """Add a new comment - always pending status"""
    try:
        booking_id = request.form.get('booking_id')
        rating = request.form.get('rating')
        comment_text = request.form.get('comment')
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': 'Please login to submit a review'})
        
        if not rating or not comment_text:
            return jsonify({'success': False, 'message': 'Rating and comment are required'})
        
        # Check if user already reviewed this booking
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT comment_id FROM comments WHERE booking_id = %s AND user_id = %s", (booking_id, user_id))
        existing = cursor.fetchone()
        if existing:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'You have already reviewed this booking'})
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"review_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}.{ext}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                image_path = f"/static/uploads/{filename}"
        
        # Insert comment with 'pending' status
        cursor.execute("""
            INSERT INTO comments (booking_id, user_id, rating, comment, image_path, status, created_at)
            VALUES (%s, %s, %s, %s, %s, 'pending', NOW())
        """, (booking_id, user_id, rating, comment_text, image_path))
        
        conn.commit()
        comment_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Review submitted! Awaiting admin approval.',
            'image_path': image_path,
            'comment_id': comment_id
        })
    
    except Exception as e:
        print(f"Error adding comment: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@comment_bp.route('/moderate/<int:comment_id>', methods=['POST'])
def moderate_comment(comment_id):
    """Admin only: approve or reject a comment"""
    try:
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        status = request.json.get('status')
        if status not in ['approved', 'rejected']:
            return jsonify({'success': False, 'message': 'Invalid status'})
        
        admin_id = session.get('user_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE comments 
            SET status = %s, moderated_by = %s, moderated_at = NOW()
            WHERE comment_id = %s
        """, (status, admin_id, comment_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Comment {status} successfully!'
        })
    
    except Exception as e:
        print(f"Error moderating comment: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@comment_bp.route('/delete/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    try:
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get image path to delete file
        cursor.execute("SELECT image_path FROM comments WHERE comment_id = %s", (comment_id,))
        result = cursor.fetchone()
        if result and result[0]:
            image_path = os.path.join(UPLOAD_FOLDER, os.path.basename(result[0]))
            if os.path.exists(image_path):
                os.remove(image_path)
        
        cursor.execute("DELETE FROM comments WHERE comment_id = %s", (comment_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Comment deleted'})
    
    except Exception as e:
        print(f"Error deleting comment: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500