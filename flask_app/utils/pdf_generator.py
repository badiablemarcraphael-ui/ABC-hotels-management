from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the absolute path to the static folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TICKETS_DIR = os.path.join(STATIC_DIR, 'tickets')
RECEIPTS_DIR = os.path.join(STATIC_DIR, 'receipts')

# Create directories with proper permissions
os.makedirs(TICKETS_DIR, mode=0o755, exist_ok=True)
os.makedirs(RECEIPTS_DIR, mode=0o755, exist_ok=True)

# Define color palette for grocery receipt style
COLORS = {
    'primary': colors.HexColor('#2c3e50'),
    'secondary': colors.HexColor('#e74c3c'),  # Grocery store red
    'accent': colors.HexColor('#27ae60'),
    'warning': colors.HexColor('#f39c12'),
    'danger': colors.HexColor('#e74c3c'),
    'light_bg': colors.HexColor('#f9f9f9'),
    'discount_bg': colors.HexColor('#e8f8f5'),
    'border': colors.HexColor('#dddddd'),
    'text_muted': colors.HexColor('#7f8c8d'),
    'white': colors.white,
    'black': colors.black,
    'dark_text': colors.HexColor('#333333'),
}

# Receipt-specific dimensions
RECEIPT_WIDTH = 280  # Points (approximately 3.9 inches / 99mm)
RECEIPT_MARGIN = 10  # Points

def safe_float(value, default=0.0):
    """Safely convert value to float"""
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"Failed to convert {value} to float, using default {default}")
        return default

def safe_string(value, default='N/A'):
    """Safely convert value to string"""
    if value is None or value == '':
        return default
    return str(value)

def create_receipt_styles():
    """Create and return all paragraph styles for receipt"""
    styles = getSampleStyleSheet()
    
    custom_styles = {
        'header_style': ParagraphStyle(
            'ReceiptHeader',
            parent=styles['Normal'],
            fontSize=14,
            textColor=COLORS['dark_text'],
            alignment=TA_CENTER,
            spaceAfter=5,
            fontName='Helvetica-Bold',
            leading=18,
        ),
        'subheader_style': ParagraphStyle(
            'ReceiptSubheader',
            parent=styles['Normal'],
            fontSize=9,
            textColor=COLORS['text_muted'],
            alignment=TA_CENTER,
            spaceAfter=15,
            leading=12,
        ),
        'title_style': ParagraphStyle(
            'ReceiptTitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=COLORS['secondary'],
            alignment=TA_CENTER,
            spaceAfter=10,
            fontName='Helvetica-Bold',
            leading=14,
        ),
        'section_title_style': ParagraphStyle(
            'SectionTitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=COLORS['primary'],
            alignment=TA_LEFT,
            spaceAfter=6,
            spaceBefore=8,
            fontName='Helvetica-Bold',
            leading=12,
        ),
        'label_style': ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=8,
            textColor=COLORS['text_muted'],
            alignment=TA_LEFT,
            leading=10,
        ),
        'value_style': ParagraphStyle(
            'Value',
            parent=styles['Normal'],
            fontSize=9,
            textColor=COLORS['dark_text'],
            alignment=TA_LEFT,
            leading=12,
        ),
        'item_style': ParagraphStyle(
            'Item',
            parent=styles['Normal'],
            fontSize=9,
            textColor=COLORS['dark_text'],
            alignment=TA_LEFT,
            leading=12,
        ),
        'price_style': ParagraphStyle(
            'Price',
            parent=styles['Normal'],
            fontSize=9,
            textColor=COLORS['dark_text'],
            alignment=TA_RIGHT,
            leading=12,
        ),
        'total_style': ParagraphStyle(
            'Total',
            parent=styles['Normal'],
            fontSize=11,
            textColor=COLORS['dark_text'],
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
            leading=14,
        ),
        'total_label_style': ParagraphStyle(
            'TotalLabel',
            parent=styles['Normal'],
            fontSize=11,
            textColor=COLORS['dark_text'],
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            leading=14,
        ),
        'footer_style': ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=7,
            textColor=COLORS['text_muted'],
            alignment=TA_CENTER,
            leading=9,
        ),
        'discount_style': ParagraphStyle(
            'DiscountStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=COLORS['accent'],
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
            leading=12,
        ),
        'barcode_style': ParagraphStyle(
            'Barcode',
            parent=styles['Normal'],
            fontSize=6,
            textColor=COLORS['text_muted'],
            alignment=TA_CENTER,
            leading=8,
        ),
    }
    
    return styles, custom_styles

def add_receipt_header(story, custom_styles, store_name="HOTEL MANAGEMENT SYSTEM"):
    """Add grocery-style receipt header"""
    story.append(Paragraph(store_name, custom_styles['header_style']))
    story.append(Paragraph("123 Business Street, City, Country", custom_styles['subheader_style']))
    story.append(Paragraph("Tel: +1-234-567-8900", custom_styles['subheader_style']))
    story.append(Paragraph("GSTIN: 22AAAAA0000A1Z", custom_styles['subheader_style']))
    story.append(Spacer(1, 5))
    
    # Decorative line (dashed-like with asterisks)
    story.append(Paragraph("*" * 50, custom_styles['footer_style']))
    story.append(Spacer(1, 5))

def add_receipt_footer(story, custom_styles):
    """Add grocery-style receipt footer"""
    story.append(Spacer(1, 5))
    story.append(Paragraph("*" * 50, custom_styles['footer_style']))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Thank you for choosing us!", custom_styles['footer_style']))
    story.append(Paragraph("Please visit again!", custom_styles['footer_style']))
    story.append(Spacer(1, 3))
    story.append(Paragraph("** This is a computer-generated receipt **", custom_styles['footer_style']))
    story.append(Paragraph("No signature required", custom_styles['footer_style']))
    story.append(Spacer(1, 3))
    
    # Simulated barcode
    story.append(Paragraph("||||||||||||||||||||||||||||||||", custom_styles['barcode_style']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", custom_styles['barcode_style']))

def create_receipt_info_line(label, value, custom_styles):
    """Create a single line of info for receipt"""
    data = [[
        Paragraph(f"{label}:", custom_styles['label_style']),
        Paragraph(safe_string(value), custom_styles['value_style'])
    ]]
    table = Table(data, colWidths=[80, 170])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return table

def create_receipt_items_table(items_data):
    """Create items table for receipt (grocery-style)"""
    if not items_data:
        return None
    
    table_data = [['Item', 'Qty', 'Price', 'Total']]
    table_data.extend(items_data)
    
    table = Table(table_data, colWidths=[100, 30, 60, 60])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (3, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, 0), 0.5, COLORS['border']),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, COLORS['border']),
    ]))
    
    return table

def create_receipt_payment_section(total_amount, discount_amount, custom_styles):
    """Create payment summary section (grocery-style)"""
    total_amount = safe_float(total_amount)
    discount_amount = safe_float(discount_amount)
    vat = total_amount * 0.07
    service = total_amount * 0.05
    after_discount = total_amount - discount_amount
    grand_total = after_discount + vat + service
    
    payment_rows = []
    
    # Room charge
    payment_rows.append([
        Paragraph("Room Charge", custom_styles['item_style']),
        Paragraph(f"${total_amount:,.2f}", custom_styles['price_style'])
    ])
    
    # Discount if applied
    if discount_amount > 0:
        payment_rows.append([
            Paragraph("Coupon Discount", custom_styles['item_style']),
            Paragraph(f"-${discount_amount:,.2f}", custom_styles['discount_style'])
        ])
        payment_rows.append([
            Paragraph("Subtotal", custom_styles['item_style']),
            Paragraph(f"${after_discount:,.2f}", custom_styles['price_style'])
        ])
    
    # Taxes
    payment_rows.append([
        Paragraph("VAT (7%)", custom_styles['item_style']),
        Paragraph(f"${vat:,.2f}", custom_styles['price_style'])
    ])
    payment_rows.append([
        Paragraph("Service Charge (5%)", custom_styles['item_style']),
        Paragraph(f"${service:,.2f}", custom_styles['price_style'])
    ])
    
    # Separator line
    payment_rows.append([
        Paragraph("─" * 35, custom_styles['footer_style']),
        Paragraph("", custom_styles['footer_style'])
    ])
    
    # Grand total
    payment_rows.append([
        Paragraph("<b>TOTAL</b>", custom_styles['total_label_style']),
        Paragraph(f"<b>${grand_total:,.2f}</b>", custom_styles['total_style'])
    ])
    
    # Create table
    table = Table(payment_rows, colWidths=[180, 70])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    return table, grand_total

def generate_booking_ticket(booking_data, ticket_number):
    """Generate grocery receipt-style ticket for booking"""
    
    try:
        filename = f"ticket_{ticket_number}.pdf"
        filepath = os.path.join(TICKETS_DIR, filename)
        
        logger.info(f"Generating receipt-style ticket PDF at: {filepath}")
        
        # Create document with receipt dimensions
        doc = SimpleDocTemplate(
            filepath,
            pagesize=(RECEIPT_WIDTH, A4[1]),  # Width = receipt width, Height = A4 height
            rightMargin=RECEIPT_MARGIN,
            leftMargin=RECEIPT_MARGIN,
            topMargin=15,
            bottomMargin=15,
            title=f"Booking Ticket #{ticket_number}",
            author="Hotel Management System",
            subject="Booking Confirmation"
        )
        
        styles, custom_styles = create_receipt_styles()
        story = []
        
        # Header
        add_receipt_header(story, custom_styles)
        
        # Ticket Type
        story.append(Paragraph("BOOKING TICKET", custom_styles['title_style']))
        story.append(Paragraph(f"#{ticket_number}", custom_styles['subheader_style']))
        story.append(Spacer(1, 5))
        story.append(Paragraph("-" * 40, custom_styles['footer_style']))
        story.append(Spacer(1, 5))
        
        # Guest Information
        story.append(Paragraph("GUEST INFO", custom_styles['section_title_style']))
        story.append(create_receipt_info_line("Name", booking_data.get('guest_name'), custom_styles))
        story.append(create_receipt_info_line("Phone", booking_data.get('guest_phone'), custom_styles))
        story.append(create_receipt_info_line("Booking ID", f"#{booking_data.get('booking_id')}", custom_styles))
        story.append(Spacer(1, 3))
        
        # Room Details
        story.append(Paragraph("ROOM DETAILS", custom_styles['section_title_style']))
        story.append(create_receipt_info_line("Room No", f"{booking_data.get('room_number')} ({booking_data.get('type_name', 'Standard')})", custom_styles))
        story.append(create_receipt_info_line("Check-in", booking_data.get('check_in_date'), custom_styles))
        story.append(create_receipt_info_line("Check-out", booking_data.get('check_out_date'), custom_styles))
        story.append(create_receipt_info_line("Nights", f"{booking_data.get('nights', 1)}", custom_styles))
        story.append(Spacer(1, 5))
        
        # Separator
        story.append(Paragraph("-" * 40, custom_styles['footer_style']))
        story.append(Spacer(1, 5))
        
        # Payment Section
        story.append(Paragraph("PAYMENT SUMMARY", custom_styles['section_title_style']))
        
        total_amount = safe_float(booking_data.get('total_amount', 0))
        discount_amount = safe_float(booking_data.get('discount_amount', 0))
        
        payment_table, grand_total = create_receipt_payment_section(total_amount, discount_amount, custom_styles)
        story.append(payment_table)
        story.append(Spacer(1, 5))
        
        # Coupon Information
        coupon_code = booking_data.get('coupon_code', '')
        if coupon_code and discount_amount > 0:
            story.append(Paragraph("-" * 40, custom_styles['footer_style']))
            coupon_style = ParagraphStyle(
                'CouponInfo',
                parent=custom_styles['footer_style'],
                textColor=COLORS['accent'],
                fontName='Helvetica-Bold',
            )
            story.append(Paragraph(f"Coupon: {coupon_code}", coupon_style))
            story.append(Paragraph(f"Saved: ${discount_amount:,.2f}", coupon_style))
            story.append(Paragraph("-" * 40, custom_styles['footer_style']))
            story.append(Spacer(1, 3))
        
        # Payment Status
        payment_status = booking_data.get('payment_status', 'pending')
        if payment_status == 'paid':
            status_style = ParagraphStyle(
                'StatusPaid',
                parent=custom_styles['title_style'],
                textColor=COLORS['accent'],
            )
            story.append(Paragraph("✓ PAID", status_style))
        else:
            status_style = ParagraphStyle(
                'StatusPending',
                parent=custom_styles['title_style'],
                textColor=COLORS['warning'],
            )
            story.append(Paragraph("⚠ PENDING - Pay at Counter", status_style))
        
        story.append(Spacer(1, 5))
        
        # Footer
        add_receipt_footer(story, custom_styles)
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Receipt-style ticket PDF generated successfully: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error generating receipt-style ticket PDF: {str(e)}")
        raise

def generate_receipt_pdf(booking_data, receipt_number):
    """Generate grocery receipt-style PDF receipt"""
    
    try:
        filename = f"receipt_{receipt_number}.pdf"
        filepath = os.path.join(RECEIPTS_DIR, filename)
        
        logger.info(f"Generating receipt-style PDF at: {filepath}")
        
        # Create document with receipt dimensions
        doc = SimpleDocTemplate(
            filepath,
            pagesize=(RECEIPT_WIDTH, A4[1]),  # Width = receipt width, Height = A4 height
            rightMargin=RECEIPT_MARGIN,
            leftMargin=RECEIPT_MARGIN,
            topMargin=15,
            bottomMargin=15,
            title=f"Payment Receipt #{receipt_number}",
            author="Hotel Management System",
            subject="Payment Receipt"
        )
        
        styles, custom_styles = create_receipt_styles()
        story = []
        
        # Header
        add_receipt_header(story, custom_styles)
        
        # Receipt Title
        story.append(Paragraph("OFFICIAL RECEIPT", custom_styles['title_style']))
        story.append(Paragraph(f"#{receipt_number}", custom_styles['subheader_style']))
        story.append(Spacer(1, 5))
        story.append(Paragraph("-" * 40, custom_styles['footer_style']))
        story.append(Spacer(1, 5))
        
        # Transaction Info
        story.append(Paragraph("TRANSACTION INFO", custom_styles['section_title_style']))
        story.append(create_receipt_info_line("Date", datetime.now().strftime('%Y-%m-%d %H:%M'), custom_styles))
        story.append(create_receipt_info_line("Booking ID", f"#{booking_data.get('booking_id')}", custom_styles))
        story.append(create_receipt_info_line("Guest", booking_data.get('guest_name'), custom_styles))
        story.append(Spacer(1, 3))
        
        # Booking Details
        story.append(Paragraph("BOOKING DETAILS", custom_styles['section_title_style']))
        story.append(create_receipt_info_line("Room", f"{booking_data.get('room_number')} ({booking_data.get('type_name', 'Standard')})", custom_styles))
        story.append(create_receipt_info_line("Period", f"{booking_data.get('check_in_date')} to {booking_data.get('check_out_date')}", custom_styles))
        story.append(create_receipt_info_line("Nights", f"{booking_data.get('nights', 1)}", custom_styles))
        story.append(Spacer(1, 5))
        
        # Separator
        story.append(Paragraph("-" * 40, custom_styles['footer_style']))
        story.append(Spacer(1, 5))
        
        # Payment Breakdown
        story.append(Paragraph("PAYMENT BREAKDOWN", custom_styles['section_title_style']))
        
        total_amount = safe_float(booking_data.get('total_amount', 0))
        discount_amount = safe_float(booking_data.get('discount_amount', 0))
        
        payment_table, grand_total = create_receipt_payment_section(total_amount, discount_amount, custom_styles)
        story.append(payment_table)
        story.append(Spacer(1, 5))
        
        # Coupon Information
        coupon_code = booking_data.get('coupon_code', '')
        if coupon_code and discount_amount > 0:
            story.append(Paragraph("-" * 40, custom_styles['footer_style']))
            coupon_style = ParagraphStyle(
                'CouponInfo',
                parent=custom_styles['footer_style'],
                textColor=COLORS['accent'],
                fontName='Helvetica-Bold',
            )
            story.append(Paragraph(f"Coupon Applied: {coupon_code}", coupon_style))
            story.append(Paragraph(f"Amount Saved: ${discount_amount:,.2f}", coupon_style))
            story.append(Paragraph("-" * 40, custom_styles['footer_style']))
            story.append(Spacer(1, 3))
        
        # Payment Method
        payment_method = booking_data.get('payment_method', 'Cash')
        story.append(create_receipt_info_line("Payment Method", payment_method.upper(), custom_styles))
        story.append(create_receipt_info_line("Payment Status", "COMPLETED", custom_styles))
        story.append(Spacer(1, 5))
        
        # Footer
        add_receipt_footer(story, custom_styles)
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Receipt-style PDF generated successfully: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error generating receipt-style PDF: {str(e)}")
        raise

def validate_booking_data(booking_data):
    """Validate booking data before PDF generation"""
    required_fields = ['guest_name', 'booking_id', 'room_number', 'check_in_date', 'check_out_date']
    missing_fields = [field for field in required_fields if not booking_data.get(field)]
    
    if missing_fields:
        logger.warning(f"Missing booking data fields: {missing_fields}")
        # Set defaults for missing fields
        for field in missing_fields:
            booking_data[field] = f"Missing_{field}"
    
    # Ensure numeric fields have proper defaults
    booking_data['total_amount'] = safe_float(booking_data.get('total_amount'), 0)
    booking_data['discount_amount'] = safe_float(booking_data.get('discount_amount'), 0)
    booking_data['nights'] = booking_data.get('nights', 1)
    
    return booking_data