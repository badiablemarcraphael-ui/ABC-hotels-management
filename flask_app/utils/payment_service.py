import json
import uuid
from datetime import datetime

class PaymentService:
    def __init__(self):
        self.demo_mode = True  # Set to False for real payments
    
    def process_online_payment(self, booking_id, amount, payment_details):
        """Process online payment (demo mode)"""
        try:
            # Generate fake transaction ID
            transaction_id = f"TXN_{uuid.uuid4().hex[:8].upper()}"
            
            if self.demo_mode:
                # Demo mode - always successful
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'amount': amount,
                    'status': 'completed',
                    'payment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'message': 'Payment processed successfully (Demo Mode)'
                }
            else:
                # Real payment integration would go here
                # Stripe, PayPal, etc.
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'amount': amount,
                    'status': 'completed',
                    'payment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'message': 'Payment processed successfully'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Payment failed: {str(e)}'
            }
    
    def generate_ticket_number(self, booking_id):
        """Generate unique ticket number"""
        return f"HTL{datetime.now().strftime('%Y%m%d')}{booking_id:04d}"

payment_service = PaymentService()