"""
Grand Hotel Email Service
Uses SendGrid API for sending emails (works on Render free tier)
"""
import os
from datetime import datetime
import python_http_client

class EmailService:
    def __init__(self):
        self.sender_email = os.environ.get('EMAIL_SENDER', 'badiablemarcraphael@gmail.com')
        self.sendgrid_api_key = os.environ.get('SENDGRID_API_KEY', '')
        self.sender_name = 'Grand Hotel & Resort'
        
        if not self.sendgrid_api_key:
            self.enabled = False
            print("⚠️ Email service disabled - no SENDGRID_API_KEY set")
        else:
            self.enabled = True
            print("✅ Email service enabled (SendGrid API)")
    
    def _send_email(self, to_email, subject, html_content):
        """Send email using SendGrid API"""
        if not self.enabled:
            print(f"📧 Email skipped (disabled) - would send '{subject}' to {to_email}")
            return True
        
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            sg = SendGridAPIClient(self.sendgrid_api_key)
            
            message = Mail(
                from_email=Email(self.sender_email, self.sender_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=html_content
            )
            
            response = sg.send(message)
            
            print(f"✅ Email sent! Status: {response.status_code}")
            print(f"   To: {to_email}")
            print(f"   Subject: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False
    
    def _get_payment_status_html(self, payment_method, payment_status='pending'):
        """Get payment status badge HTML"""
        payment_method_lower = str(payment_method).lower()
        payment_status_lower = str(payment_status).lower()
        
        if payment_method_lower in ['pay at counter', 'counter', 'cash']:
            return (
                '<span style="background: #f59e0b; color: #1f2937; padding: 8px 16px; border-radius: 20px; font-weight: bold;">⏳ PAY AT COUNTER</span>',
                'Please pay at the reception desk upon arrival. We accept cash and card payments.',
                'counter'
            )
        elif payment_status_lower == 'paid' or payment_method_lower in ['gcash via paymongo', 'gcash', 'online', 'paymongo']:
            return (
                '<span style="background: #10b981; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold;">✅ PAID via GCash</span>',
                'Your payment has been processed successfully via GCash!',
                'paid'
            )
        elif payment_status_lower == 'pending':
            return (
                '<span style="background: #f59e0b; color: #1f2937; padding: 8px 16px; border-radius: 20px; font-weight: bold;">⏳ PENDING PAYMENT</span>',
                'Your payment is pending. Please complete the payment at your earliest convenience.',
                'pending'
            )
        else:
            return (
                '<span style="background: #10b981; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold;">✅ COMPLETED</span>',
                'Your payment has been processed successfully!',
                'completed'
            )
    
    def send_booking_confirmation(self, booking, payment_method, ticket_number):
        """Send beautiful HTML booking confirmation email"""
        if not self.enabled:
            print(f"📧 Email skipped - would send booking confirmation to {booking.get('guest_email', 'unknown')}")
            return True
        
        try:
            payment_status = booking.get('payment_status', 'pending')
            payment_status_badge, payment_message, payment_type = self._get_payment_status_html(payment_method, payment_status)
            
            total_amount = float(booking.get('total_amount', 0))
            discount_amount = float(booking.get('discount_amount', 0))
            vat = total_amount * 0.07
            service = total_amount * 0.05
            grand_total = total_amount + vat + service
            
            nights = booking.get('nights', 1)
            if 'check_in_date' in booking and 'check_out_date' in booking:
                try:
                    check_in = datetime.strptime(str(booking['check_in_date']), '%Y-%m-%d')
                    check_out = datetime.strptime(str(booking['check_out_date']), '%Y-%m-%d')
                    nights = (check_out - check_in).days
                except:
                    pass
            
            check_in_formatted = booking.get('check_in_date', 'TBD')
            check_out_formatted = booking.get('check_out_date', 'TBD')
            is_counter_payment = payment_type == 'counter'
            
            # Simple, beautiful email template
            discount_row = ''
            if discount_amount > 0:
                discount_row = f'''
                <tr>
                    <td style="padding: 8px 0; color: #10b981;">💚 Discount:</td>
                    <td style="padding: 8px 0; text-align: right; color: #10b981;">-${discount_amount:.2f}</td>
                </tr>'''
            
            payment_note = 'Please pay at the reception desk upon arrival.' if is_counter_payment else 'Your payment has been processed successfully!'
            
            subject = f"✨ Booking Confirmation - #{ticket_number} | Grand Hotel"
            
            html_body = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Arial,sans-serif;background:#f5f0e8;">
    <div style="max-width:600px;margin:30px auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 10px 40px rgba(0,0,0,0.1);">
        
        <!-- Header -->
        <div style="background:linear-gradient(135deg,#1a2744,#243356);padding:35px 25px;text-align:center;border-bottom:3px solid #c9a84c;">
            <div style="font-size:40px;">🏨</div>
            <h1 style="color:#c9a84c;margin:8px 0 0;font-size:24px;letter-spacing:2px;">GRAND HOTEL</h1>
            <p style="color:rgba(255,255,255,0.8);margin:6px 0 0;font-size:13px;">LUXURY HOSPITALITY</p>
        </div>
        
        <!-- Content -->
        <div style="padding:30px;">
            <!-- Success Badge -->
            <div style="text-align:center;margin-bottom:25px;">
                <span style="display:inline-block;background:#f0fdf4;color:#166534;padding:10px 20px;border-radius:30px;font-weight:bold;font-size:14px;">
                    ✅ Booking Confirmed!
                </span>
            </div>
            
            <h2 style="color:#1a2744;margin:0 0 5px;">Dear {booking['guest_name']},</h2>
            <p style="color:#6b7280;line-height:1.6;margin:0 0 20px;">
                Thank you for choosing <strong>Grand Hotel</strong>! Your booking has been confirmed.
                {payment_note}
            </p>
            
            <!-- Booking Details -->
            <div style="background:#f9fafb;border-radius:12px;padding:20px;border:1px solid #e5e7eb;margin-bottom:20px;">
                <h3 style="color:#1a2744;margin:0 0 15px;font-size:16px;border-bottom:2px solid #c9a84c;padding-bottom:8px;">📋 Booking Details</h3>
                <table style="width:100%;border-collapse:collapse;">
                    <tr><td style="padding:8px 0;color:#6b7280;">Ticket Number:</td><td style="text-align:right;font-weight:bold;">{ticket_number}</td></tr>
                    <tr><td style="padding:8px 0;color:#6b7280;">Booking ID:</td><td style="text-align:right;font-weight:bold;">#{booking['booking_id']}</td></tr>
                    <tr><td style="padding:8px 0;color:#6b7280;">Room:</td><td style="text-align:right;font-weight:bold;">{booking.get('room_number', 'TBD')} ({booking.get('type_name', 'Standard')})</td></tr>
                    <tr><td style="padding:8px 0;color:#6b7280;">Check-in:</td><td style="text-align:right;">📅 {check_in_formatted}</td></tr>
                    <tr><td style="padding:8px 0;color:#6b7280;">Check-out:</td><td style="text-align:right;">📅 {check_out_formatted}</td></tr>
                    <tr><td style="padding:8px 0;color:#6b7280;">Duration:</td><td style="text-align:right;">⭐ {nights} {'Night' if nights == 1 else 'Nights'}</td></tr>
                </table>
            </div>
            
            <!-- Payment Details -->
            <div style="background:#f0fdf4;border-radius:12px;padding:20px;border:1px solid #10b981;margin-bottom:20px;">
                <h3 style="color:#166534;margin:0 0 15px;font-size:16px;">💰 Payment Details</h3>
                {payment_status_badge}
                <table style="width:100%;border-collapse:collapse;margin-top:15px;">
                    <tr><td style="padding:8px 0;">Room Charge:</td><td style="text-align:right;">${total_amount:.2f}</td></tr>
                    <tr><td style="padding:8px 0;">VAT (7%):</td><td style="text-align:right;">${vat:.2f}</td></tr>
                    <tr><td style="padding:8px 0;">Service (5%):</td><td style="text-align:right;">${service:.2f}</td></tr>
                    {discount_row}
                    <tr style="border-top:2px solid #10b981;"><td style="padding:12px 0 0;font-size:18px;font-weight:bold;">TOTAL:</td><td style="text-align:right;padding:12px 0 0;font-size:22px;font-weight:bold;color:#166534;">${grand_total:.2f}</td></tr>
                </table>
            </div>
            
            <!-- Info -->
            <div style="background:#eff6ff;border-left:4px solid #3b82f6;padding:15px;border-radius:8px;margin-bottom:15px;">
                <p style="margin:0;color:#1e40af;font-size:13px;">
                    <strong>ℹ️ Important:</strong> Check-in 2:00 PM | Check-out 11:00 AM<br>
                    Present this email or Booking ID upon arrival.
                </p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background:#1a2744;padding:25px;text-align:center;color:white;">
            <h4 style="color:#c9a84c;margin:0 0 10px;">GRAND HOTEL & RESORT</h4>
            <p style="margin:3px 0;font-size:13px;opacity:0.8;">📍 123 Luxury Avenue, City, Country</p>
            <p style="margin:3px 0;font-size:13px;opacity:0.8;">📞 +1 (555) 123-4567 | 📧 info@grandhotel.com</p>
        </div>
        
        <div style="background:#f9fafb;padding:15px;text-align:center;">
            <p style="margin:0;color:#9ca3af;font-size:11px;">© 2026 Grand Hotel & Resort. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
            
            return self._send_email(booking['guest_email'], subject, html_body)
            
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False
    
    def send_payment_receipt(self, booking, transaction_id, payment_method='GCash'):
        """Send payment receipt email"""
        if not self.enabled:
            print(f"📧 Receipt skipped - would send to {booking.get('guest_email', 'unknown')}")
            return True
        
        try:
            total_amount = float(booking.get('total_amount', 0))
            discount_amount = float(booking.get('discount_amount', 0))
            vat = total_amount * 0.07
            service = total_amount * 0.05
            grand_total = total_amount + vat + service
            
            is_counter = str(payment_method).lower() in ['pay at counter', 'counter', 'cash']
            
            subject = f"{'📋 Payment Note' if is_counter else '💰 Payment Receipt'} - Booking #{booking['booking_id']} | Grand Hotel"
            
            html_body = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Arial,sans-serif;background:#f5f0e8;">
    <div style="max-width:600px;margin:30px auto;background:white;border-radius:16px;overflow:hidden;">
        <div style="background:linear-gradient(135deg,#1a2744,#243356);padding:35px 25px;text-align:center;border-bottom:3px solid #c9a84c;">
            <div style="font-size:40px;">{'💰' if not is_counter else '📋'}</div>
            <h1 style="color:#c9a84c;margin:8px 0 0;font-size:24px;">{'PAYMENT RECEIPT' if not is_counter else 'PAYMENT NOTE'}</h1>
        </div>
        <div style="padding:30px;">
            <h2 style="color:#1a2744;">Dear {booking['guest_name']},</h2>
            <p style="color:#6b7280;line-height:1.6;">
                {'Thank you for your payment! Transaction completed successfully.' if not is_counter else 'Booking confirmed with counter payment option.'}
            </p>
            
            <div style="background:#f9fafb;border-radius:12px;padding:20px;margin:20px 0;">
                <table style="width:100%;">
                    <tr><td style="color:#6b7280;">Transaction ID:</td><td style="text-align:right;font-weight:bold;">{transaction_id}</td></tr>
                    <tr><td style="color:#6b7280;">Booking ID:</td><td style="text-align:right;">#{booking['booking_id']}</td></tr>
                    <tr><td style="color:#6b7280;">Payment:</td><td style="text-align:right;font-weight:bold;">{payment_method}</td></tr>
                    <tr><td style="color:#6b7280;">Room Charge:</td><td style="text-align:right;">${total_amount:.2f}</td></tr>
                    <tr><td style="color:#6b7280;">VAT (7%):</td><td style="text-align:right;">${vat:.2f}</td></tr>
                    <tr><td style="color:#6b7280;">Service (5%):</td><td style="text-align:right;">${service:.2f}</td></tr>
                    {'<tr><td style="color:#10b981;">Discount:</td><td style="text-align:right;color:#10b981;">-$' + f'{discount_amount:.2f}' + '</td></tr>' if discount_amount > 0 else ''}
                    <tr style="border-top:2px solid #ddd;"><td style="padding-top:12px;font-size:18px;font-weight:bold;">TOTAL:</td><td style="text-align:right;padding-top:12px;font-size:22px;font-weight:bold;color:#166534;">${grand_total:.2f}</td></tr>
                </table>
            </div>
            
            <div style="text-align:center;padding:15px;background:#f0fdf4;border-radius:8px;">
                <strong style="color:#166534;">{'✅ PAID' if not is_counter else '⏳ PAY AT COUNTER'}</strong>
            </div>
        </div>
        <div style="background:#1a2744;padding:20px;text-align:center;color:white;">
            <h4 style="color:#c9a84c;margin:0;">GRAND HOTEL & RESORT</h4>
        </div>
    </div>
</body>
</html>
"""
            
            return self._send_email(booking['guest_email'], subject, html_body)
            
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False


# Lazy initialization to save memory
_email_service_instance = None

def get_email_service():
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailService()
    return _email_service_instance

# Legacy support
email_service = None