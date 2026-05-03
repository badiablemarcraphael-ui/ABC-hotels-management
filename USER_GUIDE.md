# Hotel Management System - User Guide

## Getting Started

### Login
- URL: http://localhost:5000
- Default Admin: admin / admin123
- Default Receptionist: reception1 / password123

## Features

### 1. Dashboard
- View occupancy rates
- See revenue charts
- Monitor monthly trends
- Quick statistics

### 2. Managing Bookings
- **Create**: Click "New Booking" button
- **View**: All bookings listed in table
- **Search**: Use search bar to find bookings
- **Filter**: Filter by status
- **Check-in**: Click "Check In" on confirmed bookings
- **Check-out**: Click "Check Out" on checked-in bookings
- **Cancel**: Click "Cancel" to cancel booking

### 3. Room Management
- View all rooms with status
- See room types and pricing
- Book available rooms directly

### 4. Amenities
- Add new amenities (WiFi, Breakfast, etc.)
- Set prices per day
- Edit or delete existing amenities

### 5. Reports
- Occupancy reports
- Revenue analytics
- Monthly trends

## Keyboard Shortcuts
- `Ctrl + N`: New booking
- `Ctrl + F`: Focus search
- `Ctrl + P`: Print receipt

## Troubleshooting

### Can't login?
- Check if MySQL is running
- Verify username/password
- Run `python create_admin.py`

### Bookings not showing?
- Refresh page
- Check database connection
- Clear browser cache

## Support
For issues, check the console logs (F12) or contact admin.