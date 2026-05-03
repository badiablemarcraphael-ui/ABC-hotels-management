import mysql.connector
from mysql.connector import Error
import os
import sys

def get_db_connection():
    """Create and return a database connection using environment variables"""
    try:
        # SSL config for Aiven
        ssl_config = None
        
        # Check if we're on Render (has DB_HOST env variable set to Aiven)
        if 'monster-db' in os.environ.get('DB_HOST', ''):
            # On Render with Aiven - use SSL without cert verification
            ssl_config = {
                'ssl_disabled': False,
                'ssl_verify_cert': False,
                'ssl_verify_identity': False
            }
        
        config = {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'database': os.environ.get('DB_NAME', 'hotel_management'),
            'user': os.environ.get('DB_USER', 'root'),
            'password': os.environ.get('DB_PASSWORD', ''),
            'port': int(os.environ.get('DB_PORT', 3306)),
        }
        
        if ssl_config:
            config['ssl_ca'] = None
            config['ssl_disabled'] = ssl_config['ssl_disabled']
            config['ssl_verify_cert'] = ssl_config['ssl_verify_cert']
            config['ssl_verify_identity'] = ssl_config['ssl_verify_identity']
        
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            print("✅ Database connected successfully")
            return connection
            
    except Error as e:
        print(f"❌ Database Error: {e}")
        print(f"   Host: {os.environ.get('DB_HOST', 'localhost')}")
        print(f"   Database: {os.environ.get('DB_NAME', 'hotel_management')}")
        
        # Try alternative connection without SSL
        try:
            print("🔄 Retrying without SSL...")
            connection = mysql.connector.connect(
                host=os.environ.get('DB_HOST', 'localhost'),
                database=os.environ.get('DB_NAME', 'hotel_management'),
                user=os.environ.get('DB_USER', 'root'),
                password=os.environ.get('DB_PASSWORD', ''),
                port=int(os.environ.get('DB_PORT', 3306)),
                ssl_disabled=True,
                use_pure=True
            )
            if connection.is_connected():
                print("✅ Database connected successfully (no SSL)")
                return connection
        except Error as e2:
            print(f"❌ Alternative connection also failed: {e2}")
        
        return None
    
    return None

# Test the connection when this file is run directly
if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print("✅ Connection successful!")
        conn.close()
    else:
        print("❌ Connection failed!")