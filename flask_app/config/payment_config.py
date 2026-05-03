# Payment Configuration (for demo purposes)
# For production, use actual Stripe/PayPal keys

# Stripe Configuration (for online payments)
STRIPE_PUBLIC_KEY = 'pk_test_ci7qqB5BidHyWPXt4NhJvMwK'
STRIPE_SECRET_KEY = 'sk_test_UBsk1RmhhQQ9aRVEzGL6Pe3B'

# PayPal Configuration
PAYPAL_CLIENT_ID = 'your_paypal_client_id'
PAYPAL_CLIENT_SECRET = 'your_paypal_client_secret'

# Payment Methods
PAYMENT_METHODS = {
    'online': ['credit_card', 'paypal', 'gcash'],
    'counter': ['cash', 'card']
}

# Demo mode (set to False for real payments)
DEMO_MODE = True