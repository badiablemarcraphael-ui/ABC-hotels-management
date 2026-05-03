from flask import Blueprint, request, jsonify
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from local db_config (NOT from config.db_config)
from flask_app.db_config import get_db_connection

amenities_bp = Blueprint('amenities', __name__)

@amenities_bp.route('/list', methods=['GET'])
def list_amenities():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM amenities ORDER BY amenity_id")
        amenities = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(amenities)
    
    except Exception as e:
        return jsonify({'error': str(e)})

@amenities_bp.route('/get/<int:amenity_id>', methods=['GET'])
def get_amenity(amenity_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM amenities WHERE amenity_id = %s", (amenity_id,))
        amenity = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if amenity:
            return jsonify(amenity)
        else:
            return jsonify({'error': 'Amenity not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)})

@amenities_bp.route('/save', methods=['POST'])
def save_amenity():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        amenity_id = request.form.get('amenity_id')
        amenity_name = request.form.get('amenity_name')
        description = request.form.get('description')
        price_per_day = request.form.get('price_per_day', 0)
        
        if amenity_id and amenity_id != '':
            # Update existing
            cursor.execute("""
                UPDATE amenities 
                SET amenity_name=%s, description=%s, price_per_day=%s
                WHERE amenity_id=%s
            """, (amenity_name, description, price_per_day, amenity_id))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO amenities (amenity_name, description, price_per_day)
                VALUES (%s, %s, %s)
            """, (amenity_name, description, price_per_day))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@amenities_bp.route('/delete/<int:amenity_id>', methods=['DELETE'])
def delete_amenity(amenity_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM amenities WHERE amenity_id = %s", (amenity_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
