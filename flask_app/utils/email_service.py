import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
import os

class EmailService:
    class EmailService:
     def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.environ.get('EMAIL_SENDER', "badiablemarcraphael@gmail.com")
        self.sender_password = os.environ.get('EMAIL_PASSWORD', "")
        
        # Auto-disable if no password or on Render
        if not self.sender_password:
            self.enabled = False
            print("⚠️ Email service disabled - no EMAIL_PASSWORD set")
        else:
            self.enabled = True
    
    def _get_payment_status_html(self, payment_method, payment_status='pending'):
        """Get payment status badge HTML"""
        payment_method_lower = str(payment_method).lower()
        payment_status_lower = str(payment_status).lower()
        
        # Check if it's a counter payment
        if payment_method_lower in ['pay at counter', 'counter', 'cash']:
            return (
                '<span style="background: #f59e0b; color: #1f2937; padding: 8px 16px; border-radius: 20px; font-weight: bold;">⏳ PAY AT COUNTER</span>',
                'Please pay at the reception desk upon arrival. We accept cash and card payments.',
                'counter'
            )
        # Check if paid online
        elif payment_status_lower == 'paid' or payment_method_lower in ['gcash via paymongo', 'gcash', 'online', 'paymongo']:
            return (
                '<span style="background: #10b981; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold;">✅ PAID via GCash</span>',
                'Your payment has been processed successfully via GCash!',
                'paid'
            )
        # Pending payment
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
    
    def send_payment_receipt(self, booking, transaction_id, payment_method='GCash'):
        if not self.enabled:
         print(f"📧 Receipt skipped (disabled) - would send to {booking.get('guest_email', 'unknown')}")
        return True
        
        try:
            # Get payment status
            payment_status = booking.get('payment_status', 'pending')
            payment_status_badge, payment_message, payment_type = self._get_payment_status_html(payment_method, payment_status)
            
            # Calculate totals
            total_amount = float(booking.get('total_amount', 0))
            discount_amount = float(booking.get('discount_amount', 0))
            vat = total_amount * 0.07
            service = total_amount * 0.05
            grand_total = total_amount + vat + service
            
            # Get nights
            nights = booking.get('nights', 1)
            if 'check_in_date' in booking and 'check_out_date' in booking:
                try:
                    check_in = datetime.strptime(str(booking['check_in_date']), '%Y-%m-%d')
                    check_out = datetime.strptime(str(booking['check_out_date']), '%Y-%m-%d')
                    nights = (check_out - check_in).days
                except:
                    pass
            
            # Format dates
            check_in_formatted = booking.get('check_in_date', 'TBD')
            check_out_formatted = booking.get('check_out_date', 'TBD')
            
            # Determine if counter payment
            is_counter_payment = payment_type == 'counter'
            
            # Payment section color and content
            if is_counter_payment:
                payment_card_style = "background: linear-gradient(135deg, #fef3c7 0%, #fffbeb 100%); border-radius: 16px; padding: 24px; border: 1px solid #fde68a;"
                payment_title_color = "#92400e"
                payment_border_color = "#fde68a"
                payment_text_color = "#78350f"
                payment_badge_style = "background: #f59e0b; color: #1f2937; padding: 8px 16px; border-radius: 20px; font-weight: bold;"
                counter_info = """
                <div style="margin-top: 20px; padding: 16px; background: white; border-radius: 12px; border: 2px dashed #f59e0b;">
                    <p style="margin: 0 0 8px 0; color: #92400e; font-weight: bold; font-size: 16px;">💳 Payment Instructions:</p>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; line-height: 1.8;">
                        <li>Please proceed to the reception desk upon arrival</li>
                        <li>Present your Booking ID: <strong>#{}</strong></li>
                        <li>We accept: Cash, Credit Card, Debit Card</li>
                        <li>Payment must be completed before check-in</li>
                    </ul>
                </div>
                """.format(booking['booking_id'])
            else:
                payment_card_style = "background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%); border-radius: 16px; padding: 24px; border: 1px solid #10b981;"
                payment_title_color = "#166534"
                payment_border_color = "#10b981"
                payment_text_color = "#166534"
                payment_badge_style = "background: #10b981; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold;"
                counter_info = ""
            
            subject = f"✨ Booking Confirmation - #{ticket_number} | Grand Hotel"
            
            # Beautiful HTML Email Template
            html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Booking Confirmation</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #1a2744 0%, #0a0f1a 100%);">
    <div style="max-width: 600px; margin: 40px auto; background: white; border-radius: 24px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
        
        <!-- Header with gold gradient -->
        <div style="background: linear-gradient(135deg, #1a2744 0%, #243356 100%); padding: 40px 30px; text-align: center; border-bottom: 3px solid #c9a84c;">
            <div style="font-size: 48px; margin-bottom: 10px;">🏨</div>
            <h1 style="color: #c9a84c; margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 2px;">GRAND HOTEL</h1>
            <p style="color: rgba(255,255,255,0.8); margin: 10px 0 0 0; font-size: 14px; letter-spacing: 1px;">LUXURY HOSPITALITY</p>
        </div>
        
        <!-- Success badge -->
        <div style="text-align: center; margin-top: -20px;">
            <div style="display: inline-block; background: white; padding: 12px 24px; border-radius: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <span style="color: #10b981; font-size: 24px;">✓</span>
                <span style="color: #1f2937; font-weight: 600; margin-left: 8px;">Booking Confirmed!</span>
            </div>
        </div>
        
        <!-- Greeting -->
        <div style="padding: 30px 30px 20px 30px;">
            <h2 style="color: #1f2937; margin: 0 0 8px 0;">Dear {booking['guest_name']},</h2>
            <p style="color: #6b7280; margin: 0; line-height: 1.5;">
                Thank you for choosing <strong>Grand Hotel</strong>! Your booking has been confirmed. 
                {"Please complete your payment at the reception desk upon arrival." if is_counter_payment else "We look forward to providing you with an exceptional stay experience."}
            </p>
        </div>
        
        <!-- Booking Details Card -->
        <div style="padding: 0 30px;">
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); border-radius: 16px; padding: 24px; border: 1px solid #e5e7eb;">
                <h3 style="color: #1a2744; margin: 0 0 20px 0; font-size: 18px; border-bottom: 2px solid #c9a84c; padding-bottom: 10px; display: inline-block;">📋 Booking Details</h3>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">Ticket Number:</td>
                        <td style="padding: 12px 0; color: #1f2937; font-weight: 600; text-align: right;">{ticket_number}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">Booking ID:</td>
                        <td style="padding: 12px 0; color: #1f2937; font-weight: 600; text-align: right;">#{booking['booking_id']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">Guest Name:</td>
                        <td style="padding: 12px 0; color: #1f2937; text-align: right;">{booking['guest_name']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">Room:</td>
                        <td style="padding: 12px 0; color: #1f2937; text-align: right;">
                            <span style="background: #c9a84c20; padding: 4px 12px; border-radius: 12px; font-weight: 600;">{booking.get('room_number', 'TBD')}</span>
                            <span style="color: #6b7280;"> ({booking.get('type_name', 'Standard')})</span>
                        </td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">Check-in Date:</td>
                        <td style="padding: 12px 0; color: #1f2937; text-align: right;">📅 {check_in_formatted}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">Check-out Date:</td>
                        <td style="padding: 12px 0; color: #1f2937; text-align: right;">📅 {check_out_formatted}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">Duration:</td>
                        <td style="padding: 12px 0; color: #1f2937; text-align: right;">⭐ {nights} {'Night' if nights == 1 else 'Nights'}</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <!-- Payment Details Card -->
        <div style="padding: 20px 30px;">
            <div style="{payment_card_style}">
                <h3 style="color: {payment_title_color}; margin: 0 0 20px 0; font-size: 18px;">💰 Payment Details</h3>
                
                <div style="text-align: center; margin-bottom: 20px;">
                    {payment_status_badge}
                </div>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid {payment_border_color};">
                        <td style="padding: 10px 0; color: {payment_text_color};">Payment Method:</td>
                        <td style="padding: 10px 0; color: {payment_text_color}; text-align: right; font-weight: 600;">{payment_method}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid {payment_border_color};">
                        <td style="padding: 10px 0; color: {payment_text_color};">Room Charge:</td>
                        <td style="padding: 10px 0; color: {payment_text_color}; text-align: right;">${total_amount:.2f}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid {payment_border_color};">
                        <td style="padding: 10px 0; color: {payment_text_color};">VAT (7%):</td>
                        <td style="padding: 10px 0; color: {payment_text_color}; text-align: right;">${vat:.2f}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid {payment_border_color};">
                        <td style="padding: 10px 0; color: {payment_text_color};">Service Charge (5%):</td>
                        <td style="padding: 10px 0; color: {payment_text_color}; text-align: right;">${service:.2f}</td>
                    </tr>
                    {f'''<tr style="border-bottom: 1px solid {payment_border_color};">
                        <td style="padding: 10px 0; color: #10b981;">Discount:</td>
                        <td style="padding: 10px 0; color: #10b981; text-align: right;">-${discount_amount:.2f}</td>
                    </tr>''' if discount_amount > 0 else ''}
                    <tr>
                        <td style="padding: 15px 0 0 0; color: {payment_text_color}; font-size: 18px; font-weight: bold;">TOTAL AMOUNT:</td>
                        <td style="padding: 15px 0 0 0; color: {payment_text_color}; text-align: right; font-size: 22px; font-weight: bold;">${grand_total:.2f}</td>
                    </tr>
                </table>
                
                <div style="margin-top: 20px; padding: 12px; background: white; border-radius: 12px; text-align: center;">
                    <p style="margin: 0; color: {payment_text_color};">{payment_message}</p>
                </div>
                
                {counter_info}
            </div>
        </div>
        
        <!-- Important Information -->
        <div style="padding: 0 30px;">
            <div style="background: #eff6ff; border-left: 4px solid #3b82f6; border-radius: 8px; padding: 16px;">
                <p style="margin: 0; color: #1e40af; font-size: 14px;">
                    <strong>ℹ️ Important Information:</strong><br>
                    • Please present this email or Booking ID upon check-in<br>
                    • Check-in time: 2:00 PM | Check-out time: 11:00 AM<br>
                    • Early check-in and late check-out subject to availability<br>
                    • Free WiFi available throughout the hotel<br>
                    {'''• <strong>Payment is due at check-in (Pay at Counter)</strong>''' if is_counter_payment else '• Your payment has been processed successfully'}
                </p>
            </div>
        </div>
        
        <!-- Hotel Information -->
        <div style="padding: 30px;">
            <div style="background: linear-gradient(135deg, #1a2744 0%, #243356 100%); border-radius: 16px; padding: 24px; text-align: center; color: white; border: 1px solid #c9a84c;">
                <div style="font-size: 32px; margin-bottom: 10px;">🏨</div>
                <h4 style="margin: 0 0 10px 0; color: #c9a84c; font-size: 20px; letter-spacing: 2px;">GRAND HOTEL & RESORT</h4>
                <p style="margin: 5px 0; font-size: 14px; opacity: 0.9;">📍 123 Luxury Avenue, City, Country</p>
                <p style="margin: 5px 0; font-size: 14px; opacity: 0.9;">📞 +1 (555) 123-4567</p>
                <p style="margin: 5px 0; font-size: 14px; opacity: 0.9;">📧 info@grandhotel.com</p>
                
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(201,168,76,0.3);">
                    <p style="margin: 0; font-size: 12px; opacity: 0.7;">Need assistance? Contact our 24/7 concierge</p>
                    <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.7;">We're here to make your stay exceptional!</p>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background: #f9fafb; padding: 20px; text-align: center;">
            <p style="margin: 0; color: #6b7280; font-size: 12px;">© 2025 Grand Hotel & Resort. All rights reserved.</p>
            <p style="margin: 5px 0 0 0; color: #9ca3af; font-size: 11px;">This is an automated confirmation, please do not reply to this email.</p>
        </div>
        
    </div>
</body>
</html>
"""
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = booking['guest_email']
            msg['Subject'] = subject
            
            # Attach HTML version
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ {'Counter payment' if is_counter_payment else 'Online payment'} confirmation email sent to {booking['guest_email']}")
            return True
            
        except Exception as e:
            print(f"❌ Email error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_payment_receipt(self, booking, transaction_id, payment_method='GCash'):
        """Send beautiful HTML payment receipt email"""
        if not self.enabled:
            print(f"📧 Payment receipt would be sent to {booking['guest_email']}")
            return True
        
        try:
            total_amount = float(booking.get('total_amount', 0))
            discount_amount = float(booking.get('discount_amount', 0))
            vat = total_amount * 0.07
            service = total_amount * 0.05
            grand_total = total_amount + vat + service
            
            # Check if counter payment
            payment_method_lower = str(payment_method).lower()
            is_counter_payment = payment_method_lower in ['pay at counter', 'counter', 'cash']
            
            if is_counter_payment:
                subject = f"📋 Counter Payment Note - Booking #{booking['booking_id']} | Grand Hotel"
                status_badge = "⏳ PAY AT COUNTER"
                status_color = "#f59e0b"
                status_bg = "#fef3c7"
                payment_instruction = """
                <div style="margin-top: 20px; padding: 16px; background: white; border-radius: 12px; border: 2px dashed #f59e0b;">
                    <p style="margin: 0 0 8px 0; color: #92400e; font-weight: bold; font-size: 16px;">💳 Payment Instructions:</p>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; line-height: 1.8;">
                        <li>Please proceed to the reception desk upon arrival</li>
                        <li>Present your Booking ID: <strong>#{}</strong></li>
                        <li>We accept: Cash, Credit Card, Debit Card</li>
                        <li>Payment must be completed before check-in</li>
                    </ul>
                </div>
                """.format(booking['booking_id'])
            else:
                subject = f"💰 Payment Receipt - Booking #{booking['booking_id']} | Grand Hotel"
                status_badge = "✅ PAYMENT SUCCESSFUL"
                status_color = "#10b981"
                status_bg = "#f0fdf4"
                payment_instruction = ""
            
            # Beautiful HTML Payment Receipt
            html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{'Payment Receipt' if not is_counter_payment else 'Counter Payment Note'}</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #1a2744 0%, #0a0f1a 100%);">
    <div style="max-width: 600px; margin: 40px auto; background: white; border-radius: 24px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #1a2744 0%, #243356 100%); padding: 40px 30px; text-align: center; border-bottom: 3px solid #c9a84c;">
            <div style="font-size: 48px; margin-bottom: 10px;">{'💰' if not is_counter_payment else '📋'}</div>
            <h1 style="color: #c9a84c; margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 2px;">
                {'PAYMENT RECEIPT' if not is_counter_payment else 'PAYMENT NOTE'}
            </h1>
            <p style="color: rgba(255,255,255,0.8); margin: 10px 0 0 0; font-size: 14px;">
                {'Transaction Confirmation' if not is_counter_payment else 'Pay at Counter'}
            </p>
        </div>
        
        <!-- Status badge -->
        <div style="text-align: center; margin-top: -20px;">
            <div style="display: inline-block; background: white; padding: 12px 24px; border-radius: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <span style="color: {status_color}; font-size: 24px;">{'✓' if not is_counter_payment else '📋'}</span>
                <span style="color: #1f2937; font-weight: 600; margin-left: 8px;">{status_badge}</span>
            </div>
        </div>
        
        <!-- Greeting -->
        <div style="padding: 30px 30px 20px 30px;">
            <h2 style="color: #1f2937; margin: 0 0 8px 0;">Dear {booking['guest_name']},</h2>
            <p style="color: #6b7280; margin: 0; line-height: 1.5;">
                {'Thank you for your payment! Your transaction has been completed successfully.' if not is_counter_payment else 'This is a confirmation of your booking with counter payment option.'}
            </p>
        </div>
        
        <!-- Receipt Card -->
        <div style="padding: 0 30px;">
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); border-radius: 16px; padding: 24px; border: 2px solid {status_color};">
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 14px; color: #6b7280;">{'OFFICIAL RECEIPT' if not is_counter_payment else 'PAYMENT INSTRUCTION'}</div>
                    <div style="font-size: 12px; color: #9ca3af; margin-top: 5px;">#{transaction_id}</div>
                </div>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">{'Transaction ID' if not is_counter_payment else 'Reference ID'}:</td>
                        <td style="padding: 12px 0; color: #1f2937; font-weight: 600; text-align: right;">{transaction_id}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">Booking ID:</td>
                        <td style="padding: 12px 0; color: #1f2937; text-align: right;">#{booking['booking_id']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">Payment Method:</td>
                        <td style="padding: 12px 0; color: #1f2937; text-align: right;">
                            <span style="background: {status_bg}; padding: 4px 12px; border-radius: 12px; font-weight: 600;">{payment_method}</span>
                        </td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">Date:</td>
                        <td style="padding: 12px 0; color: #1f2937; text-align: right;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">Room Charge:</td>
                        <td style="padding: 12px 0; color: #1f2937; text-align: right;">${total_amount:.2f}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">VAT (7%):</td>
                        <td style="padding: 12px 0; color: #1f2937; text-align: right;">${vat:.2f}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280; font-weight: 500;">Service Charge (5%):</td>
                        <td style="padding: 12px 0; color: #1f2937; text-align: right;">${service:.2f}</td>
                    </tr>
                    {f'''<tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #10b981;">Discount:</td>
                        <td style="padding: 12px 0; color: #10b981; text-align: right;">-${discount_amount:.2f}</td>
                    </tr>''' if discount_amount > 0 else ''}
                    <tr>
                        <td style="padding: 15px 0 0 0; color: #1f2937; font-size: 18px; font-weight: bold;">TOTAL {'PAID' if not is_counter_payment else 'DUE'}:</td>
                        <td style="padding: 15px 0 0 0; color: {status_color}; text-align: right; font-size: 24px; font-weight: bold;">${grand_total:.2f}</td>
                    </tr>
                </table>
                
                <div style="margin-top: 20px; padding: 12px; background: {status_bg}; border-radius: 12px; text-align: center;">
                    <p style="margin: 0; color: {status_color}; font-weight: 500;">
                        {'✅ Payment Status: COMPLETED' if not is_counter_payment else '⏳ Payment Status: PAY AT COUNTER'}
                    </p>
                </div>
                
                {payment_instruction}
            </div>
        </div>
        
        <!-- Hotel Information -->
        <div style="padding: 30px;">
            <div style="background: linear-gradient(135deg, #1a2744 0%, #243356 100%); border-radius: 16px; padding: 24px; text-align: center; color: white; border: 1px solid #c9a84c;">
                <div style="font-size: 32px; margin-bottom: 10px;">🏨</div>
                <h4 style="margin: 0 0 10px 0; color: #c9a84c; font-size: 20px; letter-spacing: 2px;">GRAND HOTEL & RESORT</h4>
                <p style="margin: 5px 0; font-size: 14px; opacity: 0.9;">📍 123 Luxury Avenue, City, Country</p>
                <p style="margin: 5px 0; font-size: 14px; opacity: 0.9;">📞 +1 (555) 123-4567</p>
                <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">📧 info@grandhotel.com</p>
                
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(201,168,76,0.3);">
                    <p style="margin: 0; font-size: 12px; opacity: 0.7;">Thank you for choosing Grand Hotel!</p>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background: #f9fafb; padding: 20px; text-align: center;">
            <p style="margin: 0; color: #6b7280; font-size: 12px;">© 2025 Grand Hotel & Resort. All rights reserved.</p>
            <p style="margin: 5px 0 0 0; color: #9ca3af; font-size: 11px;">This is an automated {'receipt' if not is_counter_payment else 'notice'}, please keep it for your records.</p>
        </div>
        
    </div>
</body>
</html>
"""
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = booking['guest_email']
            msg['Subject'] = subject
            
            # Attach HTML version
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ {'Counter payment note' if is_counter_payment else 'Payment receipt'} sent to {booking['guest_email']}")
            return True
            
        except Exception as e:
            print(f"❌ Email error: {e}")
            import traceback
            traceback.print_exc()
            return False

# Initialize email service
email_service = EmailService()

# Test function
def test_email():
    """Test email configuration with beautiful HTML template"""
    test_booking = {
        'guest_email': 'test@example.com',
        'guest_name': 'John Doe',
        'booking_id': 12345,
        'room_number': '304',
        'type_name': 'Ocean View Suite',
        'check_in_date': '2024-12-25',
        'check_out_date': '2024-12-30',
        'total_amount': 850.00,
        'discount_amount': 0.00,
        'nights': 5,
        'payment_status': 'pending'
    }
    
    print("🎨 Testing Grand Hotel email service...")
    
    # Test booking confirmation with counter payment
    print("\n📧 Sending test booking confirmation (Counter Payment)...")
    result1 = email_service.send_booking_confirmation(test_booking, 'Pay at Counter', 'GH-2024-001')
    
    # Test payment receipt with counter payment
    print("\n📧 Sending test counter payment note...")
    result2 = email_service.send_payment_receipt(test_booking, 'GH-PAY-2024-001', 'Pay at Counter')
    
    if result1 and result2:
        print("\n✅ Email tests successful! Check your inbox for beautiful HTML emails.")
    else:
        print("\n❌ Email test failed. Check your credentials.")

if __name__ == "__main__":
    test_email()
