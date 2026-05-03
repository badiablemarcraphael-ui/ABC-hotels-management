import requests
import json
import uuid
from datetime import datetime
import base64

class PayMongoService:
    def __init__(self):
        # Demo mode - set to True for testing without real API
        self.demo_mode = True
        
        # PayMongo API Keys (get from https://dashboard.paymongo.com)
        # These are for demo - replace with your actual keys
        self.public_key = "pk_test_ci7qqB5BidHyWPXt4NhJvMwK"
        self.secret_key = "sk_test_UBsk1RmhhQQ9aRVEzGL6Pe3B"
        
        # API URLs
        self.base_url = "https://api.paymongo.com/v1"
        
    def create_payment_link(self, amount, description, booking_id):
        """Create a payment link for GCash payment"""
        
        if self.demo_mode:
            # Demo mode - return fake payment link
            return {
                'success': True,
                'payment_link': f"https://demo.paymongo.com/pay/{booking_id}",
                'checkout_url': f"/api/payments/demo-payment/{booking_id}",
                'reference_id': f"DEMO_{booking_id}_{uuid.uuid4().hex[:6]}"
            }
        
        # Real PayMongo API call (uncomment when ready)
        """
        auth = base64.b64encode(f"{self.secret_key}:".encode()).decode()
        
        headers = {
            'accept': 'application/json',
            'authorization': f'Basic {auth}',
            'content-type': 'application/json'
        }
        
        payload = {
            "data": {
                "attributes": {
                    "amount": int(amount * 100),  # Convert to centavos
                    "description": description,
                    "remarks": f"Hotel Booking #{booking_id}",
                    "payment_method_limits": [
                        {"allowed": ["gcash"]}
                    ]
                }
            }
        }
        
        response = requests.post(
            f"{self.base_url}/links",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'payment_link': data['data']['attributes']['checkout_url'],
                'checkout_url': data['data']['attributes']['checkout_url'],
                'reference_id': data['data']['id']
            }
        else:
            return {
                'success': False,
                'message': response.json().get('errors', [{}])[0].get('detail', 'Payment failed')
            }
        """
    
    def check_payment_status(self, payment_id):
        """Check payment status"""
        
        if self.demo_mode:
            # Demo mode - always return paid
            return {
                'success': True,
                'status': 'paid',
                'message': 'Payment successful (Demo Mode)'
            }
        
        # Real API call (uncomment when ready)
        """
        auth = base64.b64encode(f"{self.secret_key}:".encode()).decode()
        
        headers = {
            'accept': 'application/json',
            'authorization': f'Basic {auth}'
        }
        
        response = requests.get(
            f"{self.base_url}/payments/{payment_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'status': data['data']['attributes']['status'],
                'message': 'Payment checked'
            }
        else:
            return {
                'success': False,
                'message': 'Failed to check payment'
            }
        """

paymongo = PayMongoService()