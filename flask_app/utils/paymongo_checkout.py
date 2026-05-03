import os
import requests
import base64
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class PayMongoCheckout:
    def __init__(self):
        # Get keys from environment variables
        self.secret_key = os.getenv('PAYMONGO_SECRET_KEY', '')
        self.public_key = os.getenv('PAYMONGO_PUBLIC_KEY', '')
        self.base_url = "https://api.paymongo.com/v1"
        
        # Check if keys are set
        if not self.secret_key or not self.public_key:
            print("⚠️ WARNING: PayMongo keys not found in environment variables!")
            print("Please create a .env file with:")
            print("PAYMONGO_SECRET_KEY=sk_test_xxx")
            print("PAYMONGO_PUBLIC_KEY=pk_test_xxx")
        else:
            print(f"✅ PayMongo initialized with keys: {self.secret_key[:10]}...")
    
    def _get_auth_header(self):
        """Generate Basic Auth header"""
        auth_string = base64.b64encode(f"{self.secret_key}:".encode()).decode()
        return {
            "accept": "application/json",
            "authorization": f"Basic {auth_string}",
            "content-type": "application/json"
        }
    
    def create_checkout_session(self, booking_id, amount, guest_name, guest_email, description):
        """
        Create a Checkout Session for GCash payment
        Returns checkout_url to redirect customer
        """
        try:
            # Amount should be in centavos (PHP 100 = 10000 centavos)
            amount_in_cents = int(float(amount) * 100)
            
            # IMPORTANT: Use your actual server URL
            # For local testing with ngrok, use your ngrok URL
            # For production, use your domain
            base_url = "http://127.0.0.1:5000"
            
            success_url = f"{base_url}/api/payments/paymongo-success?booking_id={booking_id}"
            failed_url = f"{base_url}/api/payments/paymongo-failed?booking_id={booking_id}"
            
            print(f"💰 Creating checkout session for booking {booking_id}")
            print(f"Amount: PHP {amount} ({amount_in_cents} centavos)")
            print(f"Success URL: {success_url}")
            print(f"Failed URL: {failed_url}")
            
            payload = {
                "data": {
                    "attributes": {
                        "send_email_receipt": False,
                        "show_description": True,
                        "show_line_items": True,
                        "cancel_url": failed_url,
                        "success_url": success_url,
                        "description": f"Hotel Booking #{booking_id}",
                        "line_items": [
                            {
                                "currency": "PHP",
                                "amount": amount_in_cents,
                                "description": description,
                                "name": f"Hotel Room Booking #{booking_id}",
                                "quantity": 1
                            }
                        ],
                        "payment_method_types": ["gcash", "card"],
                        "metadata": {
                            "booking_id": booking_id,
                            "guest_name": guest_name,
                            "guest_email": guest_email
                        }
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/checkout_sessions",
                headers=self._get_auth_header(),
                json=payload
            )
            
            print(f"PayMongo API Response Status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                checkout_url = result['data']['attributes']['checkout_url']
                session_id = result['data']['id']
                
                print(f"✅ Checkout session created: {session_id}")
                print(f"🔗 Checkout URL: {checkout_url}")
                
                # Store session in database
                self._store_checkout_session(booking_id, session_id)
                
                return {
                    'success': True,
                    'checkout_url': checkout_url,
                    'session_id': session_id
                }
            else:
                error_response = response.json()
                print(f"❌ API Error Response: {error_response}")
                error_detail = error_response.get('errors', [{}])[0].get('detail', 'Unknown error')
                return {
                    'success': False,
                    'message': f"API Error: {error_detail}"
                }
                
        except Exception as e:
            print(f"❌ PayMongo error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': str(e)
            }
    
    def _store_checkout_session(self, booking_id, session_id):
        """Store checkout session ID in database"""
        try:
            from flask_app.db_config import get_db_connection
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Create checkout_sessions table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkout_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    booking_id INT,
                    session_id VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
                )
            """)
            
            cursor.execute("""
                INSERT INTO checkout_sessions (booking_id, session_id, status)
                VALUES (%s, %s, 'pending')
            """, (booking_id, session_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            print(f"✅ Checkout session stored for booking {booking_id}")
        except Exception as e:
            print(f"Error storing session: {e}")
    
    def get_checkout_session(self, session_id):
        """Retrieve checkout session status"""
        try:
            response = requests.get(
                f"{self.base_url}/checkout_sessions/{session_id}",
                headers=self._get_auth_header()
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error retrieving session: {e}")
            return None
    
    def expire_checkout_session(self, session_id):
        """Expire a checkout session (useful for cleanup)"""
        try:
            response = requests.post(
                f"{self.base_url}/checkout_sessions/{session_id}/expire",
                headers=self._get_auth_header()
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error expiring session: {e}")
            return False

# Create instance
paymongo_checkout = PayMongoCheckout()
