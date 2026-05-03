from flask import Blueprint, request, jsonify, current_app
import sys
import os
import uuid
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask_app.db_config import get_db_connection

room_bp = Blueprint('room', __name__)

# Configuration for file uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_room_image(file, room_number):
    """Save uploaded image and return the file path"""
    if file and allowed_file(file.filename):
        # Create unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"room_{room_number}_{uuid.uuid4().hex[:8]}.{ext}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'rooms')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Return relative path for database
        return f"/static/uploads/rooms/{filename}"
    return None

def delete_room_image(image_path):
    """Delete image file from server"""
    if image_path:
        # Convert URL path to file system path
        relative_path = image_path.lstrip('/')
        full_path = os.path.join(current_app.root_path, relative_path)
        if os.path.exists(full_path):
            os.remove(full_path)

@room_bp.route('/list', methods=['GET'])
def list_rooms():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT r.*, rt.type_name, rt.base_price, rt.capacity
        FROM rooms r
        JOIN room_types rt ON r.type_id = rt.type_id
        ORDER BY r.room_number
    """)
    
    rooms = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(rooms)

@room_bp.route('/types/get/<int:type_id>', methods=['GET'])
def get_room_type(type_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM room_types WHERE type_id = %s", (type_id,))
        room_type = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if room_type:
            return jsonify(room_type)
        else:
            return jsonify({'error': 'Room type not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)})

@room_bp.route('/types/save', methods=['POST'])
def save_room_type():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        type_id = request.form.get('type_id')
        type_name = request.form.get('type_name')
        description = request.form.get('description')
        base_price = request.form.get('base_price')
        capacity = request.form.get('capacity', 2)
        
        if type_id and type_id != '':
            # Update existing
            cursor.execute("""
                UPDATE room_types 
                SET type_name=%s, description=%s, base_price=%s, capacity=%s
                WHERE type_id=%s
            """, (type_name, description, base_price, capacity, type_id))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO room_types (type_name, description, base_price, capacity)
                VALUES (%s, %s, %s, %s)
            """, (type_name, description, base_price, capacity))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@room_bp.route('/types/delete/<int:type_id>', methods=['DELETE'])
def delete_room_type(type_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM room_types WHERE type_id = %s", (type_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
@room_bp.route('/available', methods=['GET'])
def available_rooms():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT r.*, rt.type_name, rt.base_price 
        FROM rooms r
        JOIN room_types rt ON r.type_id = rt.type_id
        WHERE r.status = 'available'
    """)
    
    rooms = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(rooms)

@room_bp.route('/types/list', methods=['GET'])
def list_room_types():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM room_types")
    types = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(types)

# ============ NEW ROOM MANAGEMENT ROUTES ============

@room_bp.route('/save', methods=['POST'])
def save_room():
    """Add or update a room with image upload"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        room_id = request.form.get('room_id')
        room_number = request.form.get('room_number')
        type_id = request.form.get('type_id')
        floor = request.form.get('floor')
        status = request.form.get('status', 'available')
        remove_image_flag = request.form.get('remove_image')  # Check if image should be removed
        
        # Validate required fields
        if not room_number or not type_id or not floor:
            return jsonify({'success': False, 'message': 'Room number, type, and floor are required'})
        
        # Handle image upload
        image_path = None
        if 'room_image' in request.files:
            file = request.files['room_image']
            if file and file.filename:
                image_path = save_room_image(file, room_number)
        
        if room_id and room_id != '':
            # Update existing room
            room_id = int(room_id)
            
            # Handle image removal
            if remove_image_flag == '1':
                # Get old image path to delete
                cursor.execute("SELECT image_path FROM rooms WHERE room_id = %s", (room_id,))
                old_image = cursor.fetchone()
                if old_image and old_image[0]:
                    delete_room_image(old_image[0])
                image_path = None
            
            if image_path:
                # Get old image path to delete (if not already deleted)
                cursor.execute("SELECT image_path FROM rooms WHERE room_id = %s", (room_id,))
                old_image = cursor.fetchone()
                if old_image and old_image[0] and remove_image_flag != '1':
                    delete_room_image(old_image[0])
                
                cursor.execute("""
                    UPDATE rooms 
                    SET room_number=%s, type_id=%s, floor=%s, status=%s, image_path=%s
                    WHERE room_id=%s
                """, (room_number, type_id, floor, status, image_path, room_id))
            else:
                # Update without changing image (or setting to NULL if removed)
                cursor.execute("""
                    UPDATE rooms 
                    SET room_number=%s, type_id=%s, floor=%s, status=%s, image_path=%s
                    WHERE room_id=%s
                """, (room_number, type_id, floor, status, image_path, room_id))
        else:
            # Insert new room
            cursor.execute("""
                INSERT INTO rooms (room_number, type_id, floor, status, image_path)
                VALUES (%s, %s, %s, %s, %s)
            """, (room_number, type_id, floor, status, image_path))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"Error saving room: {str(e)}")  # For debugging
        return jsonify({'success': False, 'message': str(e)})

@room_bp.route('/delete/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    """Delete a room and its image"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get image path to delete the file
        cursor.execute("SELECT image_path FROM rooms WHERE room_id = %s", (room_id,))
        result = cursor.fetchone()
        if result and result[0]:
            delete_room_image(result[0])
        
        cursor.execute("DELETE FROM rooms WHERE room_id = %s", (room_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@room_bp.route('/get/<int:room_id>', methods=['GET'])
def get_room(room_id):
    """Get a single room for editing"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT r.*, rt.type_name, rt.base_price, rt.capacity
            FROM rooms r
            JOIN room_types rt ON r.type_id = rt.type_id
            WHERE r.room_id = %s
        """, (room_id,))
        
        room = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if room:
            return jsonify(room)
        else:
            return jsonify({'error': 'Room not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)})
