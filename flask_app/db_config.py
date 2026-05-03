import mysql.connector
from mysql.connector import Error
import os
import sys

def get_db_connection():
    """Create and return a database connection using environment variables"""
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            database=os.environ.get('DB_NAME', 'hotel_management'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', ''),
            port=int(os.environ.get('DB_PORT', 3306)),
            ssl_ca=os.environ.get('DB_SSL_CA', '') if os.environ.get('DB_SSL_CA') else None,
            ssl_verify_identity=True
        )
        
        if connection.is_connected():
            print("✅ Database connected successfully")
            return connection
            
    except Error as e:
        print(f"❌ Database Error: {e}")
        print(f"   Host: {os.environ.get('DB_HOST', 'localhost')}")
        print(f"   Database: {os.environ.get('DB_NAME', 'hotel_management')}")
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