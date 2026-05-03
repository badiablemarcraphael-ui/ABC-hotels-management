from flask import Blueprint, request, jsonify, session
import sys
import os
from decimal import Decimal
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config import get_db_connection

coupon_bp = Blueprint('coupon', __name__)

@coupon_bp.route('/list', methods=['GET'])
def list_coupons():
    """Get all coupons"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM coupons 
            ORDER BY coupon_id DESC
        """)
        
        coupons = cursor.fetchall()
        
        # Convert Decimal to float
        for coupon in coupons:
            if coupon.get('discount_value'):
                coupon['discount_value'] = float(coupon['discount_value'])
            if coupon.get('min_booking_amount'):
                coupon['min_booking_amount'] = float(coupon['min_booking_amount'])
        
        cursor.close()
        conn.close()
        
        return jsonify(coupons)
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@coupon_bp.route('/get/<int:coupon_id>', methods=['GET'])
def get_coupon(coupon_id):
    """Get single coupon by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM coupons WHERE coupon_id = %s", (coupon_id,))
        coupon = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if coupon:
            if coupon.get('discount_value'):
                coupon['discount_value'] = float(coupon['discount_value'])
            if coupon.get('min_booking_amount'):
                coupon['min_booking_amount'] = float(coupon['min_booking_amount'])
            return jsonify(coupon)
        else:
            return jsonify({'error': 'Coupon not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@coupon_bp.route('/create', methods=['POST'])
def create_coupon():
    """Create a new coupon"""
    try:
        coupon_code = request.form.get('coupon_code')
        discount_type = request.form.get('discount_type')
        discount_value = request.form.get('discount_value')
        min_booking_amount = request.form.get('min_booking_amount', 0)
        valid_from = request.form.get('valid_from')
        valid_until = request.form.get('valid_until')
        usage_limit = request.form.get('usage_limit', 1)
        is_active = request.form.get('is_active') == 'true' or request.form.get('is_active') == 'on'
        
        if not coupon_code or not discount_type or not discount_value:
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        # Clean up empty dates
        if not valid_from:
            valid_from = None
        if not valid_until:
            valid_until = None
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if coupon code already exists
        cursor.execute("SELECT coupon_id FROM coupons WHERE coupon_code = %s", (coupon_code,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Coupon code already exists'})
        
        cursor.execute("""
            INSERT INTO coupons (coupon_code, discount_type, discount_value, min_booking_amount, 
                               valid_from, valid_until, usage_limit, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (coupon_code, discount_type, discount_value, min_booking_amount, 
              valid_from, valid_until, usage_limit, is_active))
        
        conn.commit()
        coupon_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'coupon_id': coupon_id, 'message': 'Coupon created successfully'})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@coupon_bp.route('/update/<int:coupon_id>', methods=['POST'])
def update_coupon(coupon_id):
    """Update an existing coupon"""
    try:
        coupon_code = request.form.get('coupon_code')
        discount_type = request.form.get('discount_type')
        discount_value = request.form.get('discount_value')
        min_booking_amount = request.form.get('min_booking_amount', 0)
        valid_from = request.form.get('valid_from')
        valid_until = request.form.get('valid_until')
        usage_limit = request.form.get('usage_limit', 1)
        is_active = request.form.get('is_active') == 'true' or request.form.get('is_active') == 'on'
        
        # Clean up empty dates
        if not valid_from:
            valid_from = None
        if not valid_until:
            valid_until = None
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE coupons 
            SET coupon_code = %s, discount_type = %s, discount_value = %s, 
                min_booking_amount = %s, valid_from = %s, valid_until = %s, 
                usage_limit = %s, is_active = %s
            WHERE coupon_id = %s
        """, (coupon_code, discount_type, discount_value, min_booking_amount,
              valid_from, valid_until, usage_limit, is_active, coupon_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Coupon updated successfully'})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@coupon_bp.route('/toggle-status/<int:coupon_id>', methods=['POST'])
def toggle_coupon_status(coupon_id):
    """Toggle coupon active status only"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current status first
        cursor.execute("SELECT is_active FROM coupons WHERE coupon_id = %s", (coupon_id,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Coupon not found'})
        
        new_status = not result[0]
        
        cursor.execute("""
            UPDATE coupons 
            SET is_active = %s
            WHERE coupon_id = %s
        """, (new_status, coupon_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': f'Coupon {"activated" if new_status else "deactivated"} successfully', 'is_active': new_status})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@coupon_bp.route('/delete/<int:coupon_id>', methods=['DELETE'])
def delete_coupon(coupon_id):
    """Delete a coupon"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM coupons WHERE coupon_id = %s", (coupon_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Coupon deleted successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@coupon_bp.route('/validate', methods=['POST'])
def validate_coupon():
    """Validate a coupon code for a booking"""
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
                'message': f'Minimum booking amount of ${min_amount:.2f} required for this coupon'
            })
        
        discount_value = float(coupon['discount_value'])
        if coupon['discount_type'] == 'percentage':
            discount_amount = total_amount * (discount_value / 100)
        else:
            discount_amount = discount_value
        
        new_total = total_amount - discount_amount
        
        return jsonify({
            'valid': True,
            'discount_type': coupon['discount_type'],
            'discount_value': discount_value,
            'discount_amount': discount_amount,
            'new_total': new_total,
            'message': f'Coupon applied! You saved ${discount_amount:.2f}'
        })
    
    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)}), 500