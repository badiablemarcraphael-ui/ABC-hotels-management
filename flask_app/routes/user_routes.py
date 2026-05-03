from flask import Blueprint, request, jsonify, session
import sys
import os
import hashlib
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask_app.db_config import get_db_connection
from flask_app.utils.email_service import get_email_service


user_bp = Blueprint('user', __name__)

# In-memory OTP store
otp_store = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def archive_user_before_delete(cursor, user_id, deleted_by_user_id, deleted_by_username, reason='User deleted from system'):
    try:
        cursor.execute("""
            INSERT INTO users_archive 
            (original_user_id, username, password, email, phone, role, created_at, archived_by, archived_by_username, archive_reason)
            SELECT 
                user_id, username, password, email, phone, role, created_at, 
                %s, %s, %s
            FROM users 
            WHERE user_id = %s
        """, (deleted_by_user_id, deleted_by_username, reason, user_id))
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Archive error: {e}")
        return False


def send_email_via_sendgrid(to_email, subject, html_body):
    """Helper: Send email using SendGrid API"""
    try:
        email_svc = get_email_service()
        return email_svc._send_email(to_email, subject, html_body)
    except Exception as e:
        print(f"⚠️ Email error: {e}")
        return False


@user_bp.route('/login', methods=['POST'])
def login():
    try:
        username = request.form.get('username')
        password = hash_password(request.form.get('password'))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['email'] = user.get('email', '')
            session['role'] = user['role']
            session['logged_in'] = True
            print(f"✅ User logged in: {username}, Role: {session['role']}")
            return jsonify({'success': True, 'user': user})
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role', 'guest')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        hashed_password = hash_password(password)
        cursor.execute("""
            INSERT INTO users (username, password, email, phone, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, hashed_password, email, phone, role))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Registration successful'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@user_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@user_bp.route('/check-auth', methods=['GET'])
def check_auth():
    if session.get('logged_in'):
        return jsonify({
            'authenticated': True, 
            'user': session.get('username'), 
            'role': session.get('role'),
            'user_id': session.get('user_id'),
            'email': session.get('email')
        })
    else:
        return jsonify({'authenticated': False})

@user_bp.route('/list', methods=['GET'])
def list_users():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_role = session.get('role')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if user_role == 'admin':
        cursor.execute("SELECT user_id, username, email, phone, role, created_at FROM users ORDER BY user_id DESC")
    elif user_role == 'manager':
        cursor.execute("SELECT user_id, username, email, phone, role, created_at FROM users WHERE role != 'admin' ORDER BY user_id DESC")
    else:
        cursor.execute("SELECT user_id, username, email, phone, role, created_at FROM users WHERE role = 'guest' ORDER BY user_id DESC")
    
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

@user_bp.route('/archived', methods=['GET'])
def list_archived_users():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Only administrators can view archived users'}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT archive_id, original_user_id, username, email, phone, role, 
               created_at, archived_at, archived_by_username, archive_reason
        FROM users_archive ORDER BY archived_at DESC
    """)
    archived_users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(archived_users)

@user_bp.route('/save', methods=['POST'])
def save_user():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    user_role = session.get('role')
    if user_role not in ['admin', 'manager']:
        return jsonify({'success': False, 'message': 'Access denied'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = request.form.get('user_id')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role', 'receptionist')
        
        if user_role == 'manager' and role == 'admin':
            return jsonify({'success': False, 'message': 'Managers cannot create or edit admin users'}), 403
        
        if user_id:
            if password:
                hashed = hash_password(password)
                cursor.execute("""UPDATE users SET username=%s, password=%s, email=%s, phone=%s, role=%s WHERE user_id=%s""",
                             (username, hashed, email, phone, role, user_id))
            else:
                cursor.execute("""UPDATE users SET username=%s, email=%s, phone=%s, role=%s WHERE user_id=%s""",
                             (username, email, phone, role, user_id))
        else:
            if not password:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Password is required'}), 400
            hashed = hash_password(password)
            cursor.execute("""INSERT INTO users (username, password, email, phone, role) VALUES (%s, %s, %s, %s, %s)""",
                         (username, hashed, email, phone, role))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'User saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@user_bp.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    user_role = session.get('role')
    current_user_id = session.get('user_id')
    current_username = session.get('username')
    
    if user_role not in ['admin', 'manager']:
        return jsonify({'success': False, 'message': 'Access denied'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        target_user = cursor.fetchone()
        
        if not target_user:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        if target_user['role'] == 'admin':
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Admin users cannot be deleted'}), 403
        
        if user_id == current_user_id:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Cannot delete yourself'}), 403
        
        reason = request.form.get('reason', 'User deleted from system')
        archive_success = archive_user_before_delete(cursor, user_id, current_user_id, current_username, reason)
        
        if not archive_success:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Failed to archive user'}), 500
        
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': f'User {target_user["username"]} deleted'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@user_bp.route('/archive/<int:user_id>', methods=['POST'])
def archive_user(user_id):
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Only administrators can archive users'}), 403
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        target_user = cursor.fetchone()
        
        if not target_user:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        reason = request.form.get('reason', 'User archived for review')
        current_user_id = session.get('user_id')
        current_username = session.get('username')
        
        archive_success = archive_user_before_delete(cursor, user_id, current_user_id, current_username, reason)
        if not archive_success:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Failed to archive'}), 500
        
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': f'User {target_user["username"]} archived'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@user_bp.route('/restore/<int:archive_id>', methods=['POST'])
def restore_user(archive_id):
    if not session.get('logged_in') or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users_archive WHERE archive_id = %s", (archive_id,))
        archived_user = cursor.fetchone()
        
        if not archived_user:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Archived user not found'}), 404
        
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (archived_user['username'],))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Username already exists'}), 409
        
        cursor.execute("""INSERT INTO users (username, password, email, phone, role) VALUES (%s, %s, %s, %s, %s)""",
                     (archived_user['username'], archived_user['password'], archived_user['email'], archived_user['phone'], archived_user['role']))
        cursor.execute("DELETE FROM users_archive WHERE archive_id = %s", (archive_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': f'User {archived_user["username"]} restored'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@user_bp.route('/archive/delete/<int:archive_id>', methods=['DELETE'])
def delete_archived_user(archive_id):
    if not session.get('logged_in') or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users_archive WHERE archive_id = %s", (archive_id,))
        archived_user = cursor.fetchone()
        if not archived_user:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Archived user not found'}), 404
        
        cursor.execute("DELETE FROM users_archive WHERE archive_id = %s", (archive_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': f'User {archived_user["username"]} permanently deleted'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# =============================================
# OTP VERIFICATION ROUTES (SENDGRID)
# =============================================

@user_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to email for registration verification via SendGrid"""
    try:
        email = request.form.get('email')
        username = request.form.get('username', '')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'})
        
        # Check if email already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        if username:
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': 'Username already exists'})
        
        cursor.close()
        conn.close()
        
        # Generate 6-digit OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Store OTP
        otp_store[email] = {
            'otp': otp,
            'expires': datetime.now().timestamp() + 600,
            'attempts': 0
        }
        
        # Send OTP via SendGrid
        subject = "🔐 Your OTP Code - Grand Hotel Registration"
        html_body = f"""
        <div style="max-width:500px;margin:0 auto;font-family:Arial,sans-serif;">
            <div style="background:linear-gradient(135deg,#1a2744,#243356);padding:30px;text-align:center;border-radius:16px 16px 0 0;border-bottom:3px solid #c9a84c;">
                <div style="font-size:40px;">🏨</div>
                <h2 style="color:#c9a84c;margin:10px 0 0;letter-spacing:2px;">GRAND HOTEL</h2>
                <p style="color:rgba(255,255,255,0.8);margin:8px 0 0;font-size:13px;">Email Verification</p>
            </div>
            <div style="background:white;padding:30px;border-radius:0 0 16px 16px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
                <p style="color:#374151;font-size:15px;margin:0;">Your one-time verification code is:</p>
                <div style="font-size:52px;font-weight:800;color:#1a2744;letter-spacing:10px;margin:20px 0;font-family:'Courier New',monospace;">{otp}</div>
                <p style="color:#6b7280;font-size:13px;margin:0;">This code expires in <strong>10 minutes</strong>.</p>
            </div>
        </div>
        """
        
        send_email_via_sendgrid(email, subject, html_body)
        print(f"✅ OTP sent to {email}: {otp}")
        
        return jsonify({
            'success': True, 
            'message': 'OTP sent to your email',
            'otp': otp  # ⚠️ REMOVE IN PRODUCTION
        })
    
    except Exception as e:
        print(f"Send OTP error: {e}")
        return jsonify({'success': False, 'message': 'Failed to send OTP. Please try again.'})


# =============================================
# FORGOT PASSWORD ROUTES
# =============================================

@user_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send OTP to email for password reset via SendGrid"""
    try:
        email = request.form.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'})
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id, username, email FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'success': False, 'message': 'No account found with this email'})
        
        # Generate OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        otp_store[f"reset_{email}"] = {
            'otp': otp,
            'expires': datetime.now().timestamp() + 600,
            'attempts': 0,
            'user_id': user['user_id'],
            'username': user['username']
        }
        
        # Send via SendGrid
        subject = "🔑 Password Reset OTP - Grand Hotel"
        html_body = f"""
        <div style="max-width:500px;margin:0 auto;font-family:Arial,sans-serif;">
            <div style="background:linear-gradient(135deg,#1a2744,#243356);padding:30px;text-align:center;border-radius:16px 16px 0 0;border-bottom:3px solid #c9a84c;">
                <div style="font-size:40px;">🔑</div>
                <h2 style="color:#c9a84c;margin:10px 0 0;letter-spacing:2px;">GRAND HOTEL</h2>
                <p style="color:rgba(255,255,255,0.8);margin:8px 0 0;font-size:13px;">Password Reset</p>
            </div>
            <div style="background:white;padding:30px;border-radius:0 0 16px 16px;text-align:center;">
                <p style="color:#374151;font-size:15px;">Hello <strong>{user['username']}</strong>,</p>
                <p style="color:#6b7280;">Your password reset code is:</p>
                <div style="font-size:52px;font-weight:800;color:#1a2744;letter-spacing:10px;margin:20px 0;font-family:'Courier New',monospace;">{otp}</div>
                <p style="color:#6b7280;font-size:13px;">Expires in <strong>10 minutes</strong>.</p>
            </div>
        </div>
        """
        
        send_email_via_sendgrid(email, subject, html_body)
        print(f"✅ Password reset OTP sent to {email}: {otp}")
        
        return jsonify({
            'success': True, 
            'message': 'Password reset OTP sent to your email',
            'otp': otp  # ⚠️ REMOVE IN PRODUCTION
        })
    
    except Exception as e:
        print(f"Forgot password error: {e}")
        return jsonify({'success': False, 'message': 'Failed to send OTP. Please try again.'})


@user_bp.route('/verify-reset-otp', methods=['POST'])
def verify_reset_otp():
    try:
        email = request.form.get('email')
        otp_input = request.form.get('otp')
        
        if not all([email, otp_input]):
            return jsonify({'success': False, 'message': 'Email and OTP are required'})
        
        stored = otp_store.get(f"reset_{email}")
        if not stored:
            return jsonify({'success': False, 'message': 'No OTP found. Please request a new one.'})
        
        if datetime.now().timestamp() > stored['expires']:
            del otp_store[f"reset_{email}"]
            return jsonify({'success': False, 'message': 'OTP expired.'})
        
        if stored['attempts'] >= 5:
            del otp_store[f"reset_{email}"]
            return jsonify({'success': False, 'message': 'Too many attempts.'})
        
        if stored['otp'] != otp_input:
            stored['attempts'] += 1
            return jsonify({'success': False, 'message': f'Invalid OTP. {5 - stored["attempts"]} attempts remaining.'})
        
        reset_token = hashlib.sha256(f"{email}{datetime.now().timestamp()}".encode()).hexdigest()[:32]
        otp_store[f"reset_token_{email}"] = {
            'token': reset_token,
            'expires': datetime.now().timestamp() + 300,
            'user_id': stored['user_id']
        }
        del otp_store[f"reset_{email}"]
        
        return jsonify({'success': True, 'message': 'OTP verified!', 'reset_token': reset_token})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@user_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        email = request.form.get('email')
        reset_token = request.form.get('reset_token')
        new_password = request.form.get('new_password')
        
        if not all([email, reset_token, new_password]):
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'})
        
        stored = otp_store.get(f"reset_token_{email}")
        if not stored or datetime.now().timestamp() > stored['expires']:
            return jsonify({'success': False, 'message': 'Reset session expired.'})
        
        if stored['token'] != reset_token:
            return jsonify({'success': False, 'message': 'Invalid reset token.'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (hash_password(new_password), stored['user_id']))
        conn.commit()
        cursor.close()
        conn.close()
        
        del otp_store[f"reset_token_{email}"]
        return jsonify({'success': True, 'message': 'Password reset successful!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@user_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        email = request.form.get('email')
        otp_input = request.form.get('otp')
        username = request.form.get('username')
        password = request.form.get('password')
        phone = request.form.get('phone')
        role = request.form.get('role', 'guest')
        
        if not all([email, otp_input, username, password]):
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        stored = otp_store.get(email)
        if not stored:
            return jsonify({'success': False, 'message': 'No OTP found.'})
        
        if datetime.now().timestamp() > stored['expires']:
            del otp_store[email]
            return jsonify({'success': False, 'message': 'OTP expired.'})
        
        if stored['attempts'] >= 5:
            del otp_store[email]
            return jsonify({'success': False, 'message': 'Too many attempts.'})
        
        if stored['otp'] != otp_input:
            stored['attempts'] += 1
            return jsonify({'success': False, 'message': f'Invalid OTP. {5 - stored["attempts"]} attempts remaining.'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        cursor.execute("""INSERT INTO users (username, password, email, phone, role) VALUES (%s, %s, %s, %s, %s)""",
                     (username, hash_password(password), email, phone, role))
        conn.commit()
        cursor.close()
        conn.close()
        
        del otp_store[email]
        return jsonify({'success': True, 'message': 'Registration successful! You can now login.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})