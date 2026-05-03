// =====================================================
// ABC hotels — LUXURY MODAL MANAGEMENT SYSTEM
// 60-30-10 Design: Gold Accents, Navy Depth, Cream Base
// Philippine Peso (₱) Currency Support
// Enhanced with Live Map & GPS Tracking
// =====================================================

'use strict';

// =====================================================
// HOTEL CONFIGURATION - CHANGE YOUR LOCATION HERE
// =====================================================
const HotelLocation = {
    name: 'ABC Hotels',
    address: 'Laguna University, Laguna Sports Complex, Bubukal, Santa Cruz, 4009 Laguna, Philippines',
    phone: '+63 (49) 501-1234',
    email: 'reservations@abchotels.ph',
    coordinates: {
        lat: 14.2825,  // Laguna University / Laguna Sports Complex area
        lng: 121.4126  // Santa Cruz, Laguna
    },
    rating: 4,
    starDisplay: '★★★★☆'
};

// =====================================================
// MAP CONFIGURATION - LAGUNA AREA
// =====================================================
const MapConfig = {
    // Tile layer - change map style here
    tileLayer: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    // Alternative tile layers:
    // 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'  // OpenStreetMap default
    // 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}'  // ESRI Street
    
    defaultZoom: 16,
    minZoom: 3,
    maxZoom: 19,
    
    // Nearby places around Laguna University / Santa Cruz
    nearbyPlaces: [
        { name: 'Laguna University', lat: 14.2826, lng: 121.4130, icon: '🎓', type: 'University' },
        { name: 'Laguna Sports Complex', lat: 14.2818, lng: 121.4120, icon: '🏟️', type: 'Sports Complex' },
        { name: 'Santa Cruz Public Market', lat: 14.2810, lng: 121.4150, icon: '🛒', type: 'Market' },
        { name: 'Santa Cruz Town Plaza', lat: 14.2795, lng: 121.4155, icon: '🌳', type: 'Town Plaza' },
        { name: 'Pagsanjan Falls', lat: 14.2645, lng: 121.4538, icon: '💧', type: 'Tourist Spot' },
        { name: 'Calamba Medical Center', lat: 14.2022, lng: 121.1578, icon: '🏥', type: 'Hospital' },
        { name: 'SM City Calamba', lat: 14.2050, lng: 121.1522, icon: '🛍️', type: 'Shopping Mall' },
        { name: 'Los Baños Hot Springs', lat: 14.1789, lng: 121.2255, icon: '♨️', type: 'Hot Springs' }
    ]
};

// =====================================================
// GLOBAL MAP VARIABLES
// =====================================================
let hotelMap = null;
let routingControl = null;
let hotelMarker = null;
let userMarker = null;
let nearbyMarkers = [];
let liveLocationWatchId = null;
let isLiveTracking = false;
let pulseCircle = null;
let currentRouteDistance = null;
let currentRouteDuration = null;

// =====================================================
// ELEGANT MODAL STYLES INJECTION
// =====================================================
$('head').append(`
    <style>
        /* Luxury Modal Base Styles */
        .grand-modal .modal-content {
            border: none;
            border-radius: 20px;
            box-shadow: 0 25px 80px rgba(10, 15, 26, 0.2), 0 4px 16px rgba(201, 168, 76, 0.1);
            overflow: hidden;
        }
        
        .grand-modal .modal-header {
            background: linear-gradient(135deg, #1a2744 0%, #243356 100%);
            color: white;
            border-bottom: 2px solid #c9a84c;
            padding: 20px 24px;
        }
        
        .grand-modal .modal-header .modal-title {
            font-family: 'Cormorant Garamond', 'Playfair Display', Georgia, serif;
            font-weight: 600;
            letter-spacing: 0.5px;
            font-size: 1.3rem;
        }
        
        .grand-modal .btn-close {
            filter: brightness(0) invert(1);
            opacity: 0.8;
            transition: all 0.3s ease;
        }
        
        .grand-modal .btn-close:hover {
            opacity: 1;
            transform: rotate(90deg) scale(1.1);
        }
        
        .grand-modal .modal-body {
            padding: 24px;
            background: #fdfcf9;
        }
        
        .grand-modal .modal-footer {
            background: #f5f0e8;
            border-top: 1px solid rgba(201, 168, 76, 0.2);
            padding: 16px 24px;
        }
        
        .grand-modal .form-label {
            font-weight: 600;
            color: #1a2744;
            font-size: 0.85rem;
            letter-spacing: 0.3px;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        
        .grand-modal .form-control,
        .grand-modal .form-select {
            border: 2px solid #e8e0d5;
            border-radius: 12px;
            padding: 10px 14px;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            background: white;
        }
        
        .grand-modal .form-control:focus,
        .grand-modal .form-select:focus {
            border-color: #c9a84c;
            box-shadow: 0 0 0 4px rgba(201, 168, 76, 0.1), 0 0 20px rgba(201, 168, 76, 0.08);
            outline: none;
        }
        
        .grand-modal .btn-primary {
            background: linear-gradient(135deg, #c9a84c 0%, #a88838 100%);
            border: none;
            padding: 10px 24px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            font-size: 0.85rem;
            border-radius: 10px;
            color: #0a0f1a;
            transition: all 0.3s ease;
        }
        
        .grand-modal .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(201, 168, 76, 0.35);
            filter: brightness(1.05);
        }
        
        .grand-modal .btn-secondary {
            background: transparent;
            border: 2px solid #1a2744;
            color: #1a2744;
            padding: 10px 24px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            font-size: 0.85rem;
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        
        .grand-modal .btn-secondary:hover {
            background: #1a2744;
            color: white;
            transform: translateY(-2px);
        }
        
        /* Map Styles */
        .map-container {
            border-radius: 16px;
            overflow: hidden;
            border: 2px solid #e8e0d5;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        }
        
        .custom-div-icon {
            border: none !important;
            background: none !important;
        }
        
        .hotel-popup .leaflet-popup-content-wrapper {
            border-radius: 14px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }
        
        /* Route Info Panel */
        .route-info-panel {
            background: white;
            border-radius: 14px;
            padding: 16px;
            margin-top: 12px;
            border: 1px solid #e8e0d5;
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
            display: none;
        }
        
        .route-info-panel.show {
            display: block;
            animation: slideDown 0.3s ease;
        }
        
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .route-stat {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .route-stat:last-child {
            border-bottom: none;
        }
        
        .route-stat-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            flex-shrink: 0;
        }
        
        .route-stat-icon.distance {
            background: rgba(201, 168, 76, 0.1);
            color: #c9a84c;
        }
        
        .route-stat-icon.duration {
            background: rgba(45, 106, 79, 0.1);
            color: #2d6a4f;
        }
        
        .route-stat-icon.arrival {
            background: rgba(74, 124, 150, 0.1);
            color: #4a7c96;
        }
        
        .route-stat-value {
            font-weight: 700;
            font-size: 1.1rem;
            color: #1a2744;
        }
        
        .route-stat-label {
            font-size: 0.75rem;
            color: #6b7280;
            font-weight: 500;
        }
        
        /* Tab Styles */
        .luxury-tabs {
            border-bottom: 2px solid #e8e0d5;
            gap: 0.5rem;
        }
        
        .luxury-tabs .nav-link {
            color: #8b7355;
            font-weight: 600;
            border: none;
            border-bottom: 3px solid transparent;
            padding: 12px 20px;
            transition: all 0.3s ease;
            border-radius: 8px 8px 0 0;
        }
        
        .luxury-tabs .nav-link:hover {
            color: #a88838;
            border-bottom-color: rgba(201, 168, 76, 0.3);
            background: rgba(201, 168, 76, 0.03);
        }
        
        .luxury-tabs .nav-link.active {
            color: #a88838;
            border-bottom-color: #c9a84c;
            background: transparent;
        }
        
        /* Rating Stars */
        .rating-star {
            cursor: pointer;
            transition: all 0.2s ease;
            color: #d4d0c8;
            font-size: 1.8rem;
        }
        
        .rating-star:hover,
        .rating-star.active,
        .rating-star.fas {
            color: #c9a84c;
            transform: scale(1.15);
        }
        
        /* Coupon Switch */
        .luxury-switch {
            position: relative;
            display: inline-block;
            width: 48px;
            height: 26px;
        }
        
        .luxury-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .luxury-switch .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: #d4d0c8;
            transition: 0.4s;
            border-radius: 26px;
        }
        
        .luxury-switch .slider:before {
            position: absolute;
            content: "";
            height: 22px;
            width: 22px;
            left: 2px;
            bottom: 2px;
            background: white;
            transition: 0.4s;
            border-radius: 50%;
        }
        
        .luxury-switch input:checked + .slider {
            background: #c9a84c;
        }
        
        .luxury-switch input:checked + .slider:before {
            transform: translateX(22px);
        }
        
        /* Map Buttons */
        .map-action-btn {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.8rem;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        
        .map-action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }
        
        /* Dark Mode */
        .dark-mode .grand-modal .modal-body {
            background: #1c2135;
        }
        
        .dark-mode .grand-modal .modal-footer {
            background: #252540;
            border-top-color: rgba(201, 168, 76, 0.12);
        }
        
        .dark-mode .grand-modal .form-control,
        .dark-mode .grand-modal .form-select {
            background: #2a2a3e;
            border-color: rgba(201, 168, 76, 0.2);
            color: #d4cec4;
        }
        
        .dark-mode .grand-modal .form-label {
            color: #c4b393;
        }
        
        .dark-mode .luxury-tabs .nav-link {
            color: #8b8a95;
        }
        
        .dark-mode .luxury-tabs .nav-link.active {
            color: #dfc278;
        }
        
        .dark-mode .route-info-panel {
            background: #1c2135;
            border-color: rgba(255,255,255,0.05);
        }
        
        .dark-mode .route-stat-value {
            color: #d4cec4;
        }
        
        .dark-mode .map-container {
            border-color: rgba(255,255,255,0.1);
        }
        
        /* Peso Input Styling */
        .peso-input-group .input-group-text {
            background: #f5f0e8;
            border-color: #e8e0d5;
            font-weight: 700;
            color: #1a2744;
        }
        
        .dark-mode .peso-input-group .input-group-text {
            background: #2a2a3e;
            border-color: rgba(201, 168, 76, 0.2);
            color: #d4cec4;
        }
        
        /* Live tracking indicator */
        .live-tracking-dot {
            width: 10px;
            height: 10px;
            background: #ef4444;
            border-radius: 50%;
            display: inline-block;
            animation: livePulse 1.5s ease-in-out infinite;
        }
        
        @keyframes livePulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6); }
            50% { opacity: 0.5; box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
        }
        
        @keyframes markerPulse {
            0%, 100% { box-shadow: 0 6px 20px rgba(201, 168, 76, 0.5), 0 0 30px rgba(201, 168, 76, 0.3); }
            50% { box-shadow: 0 6px 30px rgba(201, 168, 76, 0.7), 0 0 50px rgba(201, 168, 76, 0.5); }
        }
        
        /* Leaflet control customization */
        .leaflet-control-locate a {
            border-radius: 10px !important;
        }
        
        .leaflet-control-zoom a {
            border-radius: 8px !important;
        }
        
        .route-steps {
            max-height: 250px;
            overflow-y: auto;
            padding-right: 8px;
        }
        
        .route-steps::-webkit-scrollbar {
            width: 4px;
        }
        
        .route-steps::-webkit-scrollbar-thumb {
            background: #c9a84c;
            border-radius: 2px;
        }
    </style>
`);

// =====================================================
// MODAL MANAGER
// =====================================================
const ModalManager = {
    
    // ==========================================
    // BOOKING MODAL
    // ==========================================
    showBookingModal: function(roomId = null) {
        $.ajax({
            url: '/api/rooms/available',
            method: 'GET',
            timeout: GrandHotelConfig ? GrandHotelConfig.apiTimeout : 15000,
            success: function(rooms) {
                let roomOptions = '<option value="">Select a luxurious room</option>';
                
                if (rooms && rooms.length > 0) {
                    rooms.forEach(room => {
                        const price = window.formatPHP ? window.formatPHP(room.base_price) : '₱' + parseFloat(room.base_price).toFixed(2);
                        roomOptions += `
                            <option value="${room.room_id}">
                                Room ${room.room_number} — ${room.type_name} (${price}/night)
                            </option>
                        `;
                    });
                }
                
                const modalHtml = `
                    <div class="modal fade grand-modal" id="bookingModal" tabindex="-1" aria-hidden="true">
                        <div class="modal-dialog modal-lg modal-dialog-centered">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">
                                        <i class="fas fa-calendar-plus me-2" style="color: #dfc278;"></i>
                                        New Reservation
                                    </h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <ul class="nav nav-tabs luxury-tabs mb-4" id="bookingTabs" role="tablist">
                                        <li class="nav-item">
                                            <a class="nav-link active" data-bs-toggle="tab" href="#bookingFormTab">
                                                <i class="fas fa-clipboard-list me-2"></i>Reservation Details
                                            </a>
                                        </li>
                                        <li class="nav-item">
                                            <a class="nav-link" data-bs-toggle="tab" href="#mapTab">
                                                <i class="fas fa-map-location-dot me-2"></i>Location & Map
                                            </a>
                                        </li>
                                    </ul>
                                    
                                    <div class="tab-content">
                                        <!-- Booking Form -->
                                        <div class="tab-pane fade show active" id="bookingFormTab">
                                            <form id="bookingForm" novalidate>
                                                <div class="row g-3">
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-user me-1" style="color: #c9a84c;"></i>
                                                            Guest Name *
                                                        </label>
                                                        <input type="text" class="form-control" name="guest_name" 
                                                               placeholder="Enter full name" required>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-envelope me-1" style="color: #c9a84c;"></i>
                                                            Email Address *
                                                        </label>
                                                        <input type="email" class="form-control" name="guest_email" 
                                                               placeholder="guest@example.com" required>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-phone me-1" style="color: #c9a84c;"></i>
                                                            Phone Number *
                                                        </label>
                                                        <input type="tel" class="form-control" name="guest_phone" 
                                                               placeholder="+63 9XX XXX XXXX" required>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-door-open me-1" style="color: #c9a84c;"></i>
                                                            Select Room
                                                        </label>
                                                        <select class="form-select" name="room_id" id="roomSelect">
                                                            ${roomOptions}
                                                        </select>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-calendar-check me-1" style="color: #c9a84c;"></i>
                                                            Check-in Date *
                                                        </label>
                                                        <input type="date" class="form-control" name="check_in" 
                                                               min="${new Date().toISOString().split('T')[0]}" required>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-calendar-times me-1" style="color: #c9a84c;"></i>
                                                            Check-out Date *
                                                        </label>
                                                        <input type="date" class="form-control" name="check_out" required>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-user-friends me-1" style="color: #c9a84c;"></i>
                                                            Adults
                                                        </label>
                                                        <input type="number" class="form-control" name="adults" 
                                                               value="1" min="1" max="10">
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-child me-1" style="color: #c9a84c;"></i>
                                                            Children
                                                        </label>
                                                        <input type="number" class="form-control" name="children" 
                                                               value="0" min="0" max="10">
                                                    </div>
                                                    <div class="col-12">
                                                        <label class="form-label">
                                                            <i class="fas fa-ticket-alt me-1" style="color: #c9a84c;"></i>
                                                            Promotional Code
                                                        </label>
                                                        <div class="input-group">
                                                            <input type="text" class="form-control" name="coupon_code" 
                                                                   id="couponCode" placeholder="Enter code (optional)"
                                                                   style="text-transform: uppercase;">
                                                            <button class="btn btn-gold" type="button" 
                                                                    onclick="validateCouponCode()">
                                                                <i class="fas fa-check me-1"></i> Apply
                                                            </button>
                                                        </div>
                                                        <small id="couponMessage" class="form-text"></small>
                                                    </div>
                                                </div>
                                            </form>
                                        </div>
                                        
                                        <!-- Map Tab -->
                                        <div class="tab-pane fade" id="mapTab">
                                            <div class="alert" style="background: rgba(201, 168, 76, 0.08); border: 1px solid rgba(201, 168, 76, 0.2); margin-bottom: 1rem; border-radius: 12px;">
                                                <div class="d-flex justify-content-between align-items-center">
                                                    <div>
                                                        <i class="fas fa-hotel me-2" style="color: #c9a84c;"></i>
                                                        <strong>${HotelLocation.name}</strong><br>
                                                        <small class="text-muted">${HotelLocation.address}</small>
                                                    </div>
                                                    <span id="liveTrackingStatus" style="display: none;">
                                                        <span class="live-tracking-dot"></span>
                                                        <small class="fw-bold text-danger ms-1">LIVE</small>
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="map-container mb-3">
                                                <div id="hotelMap" style="height: 400px; width: 100%;"></div>
                                            </div>
                                            <div class="d-flex gap-2 flex-wrap">
                                                <button class="map-action-btn" id="getDirectionsBtn" 
                                                        style="background: linear-gradient(135deg, #c9a84c, #a88838); color: #1a2744;">
                                                    <i class="fas fa-location-dot"></i> Get Directions
                                                </button>
                                                <button class="map-action-btn" id="startLiveTrackingBtn"
                                                        style="background: #2d6a4f; color: white;">
                                                    <i class="fas fa-satellite-dish"></i> Live Track Me
                                                </button>
                                                <button class="map-action-btn" id="stopLiveTrackingBtn"
                                                        style="background: #8b3a3a; color: white; display: none;">
                                                    <i class="fas fa-stop"></i> Stop Tracking
                                                </button>
                                                <button class="map-action-btn" id="resetMapBtn"
                                                        style="background: #f0f0f0; color: #1a2744; border: 1px solid #d4d0c8;">
                                                    <i class="fas fa-undo"></i> Reset Map
                                                </button>
                                            </div>
                                            <div class="route-info-panel" id="routeInfoPanel">
                                                <div class="route-stat">
                                                    <div class="route-stat-icon distance">
                                                        <i class="fas fa-route"></i>
                                                    </div>
                                                    <div>
                                                        <div class="route-stat-value" id="routeDistance">-- km</div>
                                                        <div class="route-stat-label">Total Distance</div>
                                                    </div>
                                                </div>
                                                <div class="route-stat">
                                                    <div class="route-stat-icon duration">
                                                        <i class="fas fa-clock"></i>
                                                    </div>
                                                    <div>
                                                        <div class="route-stat-value" id="routeDuration">-- mins</div>
                                                        <div class="route-stat-label">Estimated Time</div>
                                                    </div>
                                                </div>
                                                <div class="route-stat">
                                                    <div class="route-stat-icon arrival">
                                                        <i class="fas fa-flag-checkered"></i>
                                                    </div>
                                                    <div>
                                                        <div class="route-stat-value" id="routeArrival">--</div>
                                                        <div class="route-stat-label">Estimated Arrival</div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div id="directionsSteps" class="route-steps mt-3" style="display: none;"></div>
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                        <i class="fas fa-times me-1"></i> Cancel
                                    </button>
                                    <button type="button" class="btn btn-primary" onclick="submitBookingReservation()">
                                        <i class="fas fa-credit-card me-1"></i> Proceed to Payment
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                $('#modals-container').html(modalHtml);
                
                // Initialize map when map tab is shown
                $('#bookingModal').on('shown.bs.modal', function() {
                    setTimeout(() => {
                        if ($('#mapTab').hasClass('active')) {
                            initializeHotelMap();
                        }
                    }, 200);
                });
                
                // Initialize map when switching to map tab
                $('a[href="#mapTab"]').on('shown.bs.tab', function() {
                    setTimeout(() => initializeHotelMap(), 200);
                });
                
                // Map button handlers
                $('#getDirectionsBtn').on('click', getUserLocationAndRoute);
                $('#resetMapBtn').on('click', resetMapToHotel);
                $('#startLiveTrackingBtn').on('click', startLiveTracking);
                $('#stopLiveTrackingBtn').on('click', stopLiveTracking);
                
                // Date validation
                $('input[name="check_in"]').on('change', function() {
                    const checkIn = $(this).val();
                    $('input[name="check_out"]').attr('min', checkIn);
                });
                
                // Pre-select room if provided
                if (roomId) {
                    $('#roomSelect').val(roomId);
                }
                
                // Clean up when hidden
                $('#bookingModal').on('hidden.bs.modal', function() {
                    stopLiveTracking();
                    destroyMap();
                    $('#bookingModal').remove();
                    $('.modal-backdrop').remove();
                    $('body').removeClass('modal-open');
                    $('body').css('overflow', '');
                });
                
                $('#bookingModal').modal('show');
            },
            error: function(xhr, status, error) {
                console.error('Failed to load rooms:', error);
                window.showNotification('Unable to load room availability. Please try again.', 'error');
            }
        });
    },
    
    // ==========================================
    // AMENITY MODAL
    // ==========================================
    showAmenityModal: function(amenity = null) {
        const isEdit = amenity !== null;
        
        if (isEdit && amenity.amenity_id) {
            this.currentEditId = amenity.amenity_id;
        }
        
        const modalHtml = `
            <div class="modal fade grand-modal" id="amenityModal" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-spa me-2" style="color: #dfc278;"></i>
                                ${isEdit ? 'Edit' : 'Add'} Amenity
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="amenityForm">
                                <input type="hidden" name="amenity_id" value="${isEdit ? amenity.amenity_id : ''}">
                                <div class="mb-3">
                                    <label class="form-label">
                                        <i class="fas fa-tag me-1"></i> Amenity Name *
                                    </label>
                                    <input type="text" class="form-control" name="amenity_name" 
                                           value="${isEdit ? escapeHtml(amenity.amenity_name) : ''}" 
                                           placeholder="e.g., Spa Treatment" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">
                                        <i class="fas fa-align-left me-1"></i> Description
                                    </label>
                                    <textarea class="form-control" name="description" rows="3" 
                                              placeholder="Describe the amenity...">${isEdit ? escapeHtml(amenity.description || '') : ''}</textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">
                                        <i class="fas fa-peso-sign me-1"></i> Price per Day
                                    </label>
                                    <div class="input-group peso-input-group">
                                        <span class="input-group-text">₱</span>
                                        <input type="number" step="0.01" class="form-control" name="price_per_day" 
                                               value="${isEdit ? amenity.price_per_day : '0.00'}" min="0">
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="submitAmenityForm()">
                                <i class="fas fa-save me-1"></i> Save Amenity
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#modals-container').html(modalHtml);
        
        $('#amenityModal').on('hidden.bs.modal', function() {
            $('#amenityModal').remove();
            $('.modal-backdrop').remove();
            $('body').removeClass('modal-open');
            $('body').css('overflow', '');
        });
        
        $('#amenityModal').modal('show');
    },
    
    // ==========================================
    // ROOM TYPE MODAL
    // ==========================================
    showRoomTypeModal: function(roomType = null) {
        const isEdit = roomType !== null;
        
        const modalHtml = `
            <div class="modal fade grand-modal" id="roomTypeModal" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-door-open me-2" style="color: #dfc278;"></i>
                                ${isEdit ? 'Edit' : 'Add'} Room Category
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="roomTypeForm">
                                <input type="hidden" name="type_id" value="${isEdit ? roomType.type_id : ''}">
                                <div class="mb-3">
                                    <label class="form-label">
                                        <i class="fas fa-tag me-1"></i> Category Name *
                                    </label>
                                    <input type="text" class="form-control" name="type_name" 
                                           value="${isEdit ? escapeHtml(roomType.type_name) : ''}" 
                                           placeholder="e.g., Deluxe Suite" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">
                                        <i class="fas fa-align-left me-1"></i> Description
                                    </label>
                                    <textarea class="form-control" name="description" rows="3">${isEdit ? escapeHtml(roomType.description || '') : ''}</textarea>
                                </div>
                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <label class="form-label">
                                            <i class="fas fa-peso-sign me-1"></i> Base Price *
                                        </label>
                                        <div class="input-group peso-input-group">
                                            <span class="input-group-text">₱</span>
                                            <input type="number" step="0.01" class="form-control" name="base_price" 
                                                   value="${isEdit ? roomType.base_price : ''}" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">
                                            <i class="fas fa-users me-1"></i> Capacity
                                        </label>
                                        <input type="number" class="form-control" name="capacity" 
                                               value="${isEdit ? (roomType.capacity || 2) : 2}" min="1" max="10">
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="submitRoomTypeForm()">
                                <i class="fas fa-save me-1"></i> Save Category
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#modals-container').html(modalHtml);
        
        $('#roomTypeModal').on('hidden.bs.modal', function() {
            $('#roomTypeModal').remove();
            $('.modal-backdrop').remove();
            $('body').removeClass('modal-open');
            $('body').css('overflow', '');
        });
        
        $('#roomTypeModal').modal('show');
    },
    
    // ==========================================
    // COUPON MODAL
    // ==========================================
    showCouponModal: function(coupon = null) {
        const isEdit = coupon !== null;
        
        const modalHtml = `
            <div class="modal fade grand-modal" id="couponModal" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-ticket-alt me-2" style="color: #dfc278;"></i>
                                ${isEdit ? 'Edit' : 'Create'} Promotion
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="couponForm">
                                <input type="hidden" name="coupon_id" id="couponId" value="${isEdit ? coupon.coupon_id : ''}">
                                
                                <div class="mb-3">
                                    <label class="form-label" for="couponCodeInput">
                                        <i class="fas fa-tag me-1"></i> Promo Code *
                                    </label>
                                    <input type="text" class="form-control text-uppercase" name="coupon_code" 
                                           id="couponCodeInput" required 
                                           placeholder="e.g., WELCOME20"
                                           value="${isEdit ? escapeHtml(coupon.coupon_code) : ''}">
                                    <small class="text-muted">Use uppercase letters and numbers</small>
                                </div>
                                
                                <div class="row g-3 mb-3">
                                    <div class="col-md-6">
                                        <label class="form-label" for="discountType">
                                            <i class="fas fa-percent me-1"></i> Discount Type
                                        </label>
                                        <select class="form-select" name="discount_type" id="discountType" required>
                                            <option value="percentage" ${isEdit && coupon.discount_type === 'percentage' ? 'selected' : ''}>
                                                Percentage (%)
                                            </option>
                                            <option value="fixed" ${isEdit && coupon.discount_type === 'fixed' ? 'selected' : ''}>
                                                Fixed Amount (₱)
                                            </option>
                                        </select>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label" for="discountValue">
                                            <i class="fas fa-peso-sign me-1"></i> Discount Value *
                                        </label>
                                        <input type="number" step="0.01" class="form-control" name="discount_value" 
                                               id="discountValue" required 
                                               value="${isEdit ? coupon.discount_value : ''}">
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label" for="minAmount">
                                        <i class="fas fa-chart-line me-1"></i> Minimum Booking Amount
                                    </label>
                                    <div class="input-group peso-input-group">
                                        <span class="input-group-text">₱</span>
                                        <input type="number" step="0.01" class="form-control" name="min_booking_amount" 
                                               id="minAmount" value="${isEdit ? (coupon.min_booking_amount || 0) : 0}">
                                    </div>
                                    <small class="text-muted">Set 0 for no minimum</small>
                                </div>
                                
                                <div class="row g-3 mb-3">
                                    <div class="col-md-6">
                                        <label class="form-label" for="validFrom">
                                            <i class="fas fa-calendar-day me-1"></i> Valid From
                                        </label>
                                        <input type="date" class="form-control" name="valid_from" id="validFrom"
                                               value="${isEdit && coupon.valid_from ? coupon.valid_from : ''}">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label" for="validUntil">
                                            <i class="fas fa-calendar-xmark me-1"></i> Valid Until
                                        </label>
                                        <input type="date" class="form-control" name="valid_until" id="validUntil"
                                               value="${isEdit && coupon.valid_until ? coupon.valid_until : ''}">
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label" for="usageLimit">
                                        <i class="fas fa-hashtag me-1"></i> Usage Limit
                                    </label>
                                    <input type="number" class="form-control" name="usage_limit" id="usageLimit" 
                                           value="${isEdit ? coupon.usage_limit : 1}" min="1">
                                </div>
                                
                                <div class="p-3 rounded" style="background: rgba(201, 168, 76, 0.05); border: 1px solid #e8e0d5;">
                                    <label class="luxury-switch mb-0">
                                        <input type="checkbox" name="is_active" id="isActive" 
                                               ${isEdit && (coupon.is_active === 1 || coupon.is_active === true) ? 'checked' : 'checked'}>
                                        <span class="slider"></span>
                                    </label>
                                    <span class="ms-3 fw-semibold" style="color: #1a2744;">
                                        <i class="fas fa-circle-check me-1" style="color: #2d6a4f;"></i>
                                        Coupon Active
                                    </span>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="submitCouponForm()">
                                <i class="fas fa-save me-1"></i> Save Promotion
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#modals-container').html(modalHtml);
        
        $('#couponModal').on('hidden.bs.modal', function() {
            $('#couponModal').remove();
            $('.modal-backdrop').remove();
            $('body').removeClass('modal-open');
            $('body').css('overflow', '');
        });
        
        $('#couponModal').modal('show');
    },
    
    // ==========================================
    // REVIEW/COMMENT MODAL
    // ==========================================
    showCommentModal: function(bookingId) {
        const modalHtml = `
            <div class="modal fade grand-modal" id="commentModal" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-star me-2" style="color: #dfc278;"></i>
                                Share Your Experience
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="commentForm" enctype="multipart/form-data">
                                <input type="hidden" name="booking_id" value="${bookingId}">
                                
                                <div class="mb-4 text-center">
                                    <label class="form-label d-block mb-3">Your Rating</label>
                                    <div class="rating-stars" id="starRating">
                                        <i class="fas fa-star rating-star" data-rating="1"></i>
                                        <i class="fas fa-star rating-star" data-rating="2"></i>
                                        <i class="fas fa-star rating-star" data-rating="3"></i>
                                        <i class="fas fa-star rating-star" data-rating="4"></i>
                                        <i class="fas fa-star rating-star" data-rating="5"></i>
                                    </div>
                                    <input type="hidden" name="rating" id="ratingValue" required>
                                    <div id="ratingError" class="text-danger small mt-2" style="display: none;">
                                        Please select a rating
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">
                                        <i class="fas fa-pen-fancy me-1"></i> Your Review
                                    </label>
                                    <textarea class="form-control" name="comment" rows="4" 
                                              placeholder="Tell us about your stay..." required></textarea>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">
                                        <i class="fas fa-camera me-1"></i> Add Photos (Optional)
                                    </label>
                                    <input type="file" class="form-control" name="image" 
                                           accept="image/*" id="reviewImage">
                                    <small class="text-muted">Share a photo of your experience (max 5MB)</small>
                                    <div id="imagePreview" class="mt-3 text-center" style="display: none;">
                                        <img id="previewImg" 
                                             style="max-width: 100%; max-height: 200px; border-radius: 12px; 
                                                    box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="submitGuestReview()">
                                <i class="fas fa-paper-plane me-1"></i> Submit Review
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#modals-container').html(modalHtml);
        
        // Star rating interaction
        $('#starRating .rating-star').on('click', function() {
            const rating = $(this).data('rating');
            $('#ratingValue').val(rating);
            $('#ratingError').hide();
            
            $('#starRating .rating-star').each(function(index) {
                if (index < rating) {
                    $(this).addClass('active fas').removeClass('far');
                } else {
                    $(this).removeClass('active fas').addClass('far');
                }
            });
        });
        
        $('#starRating .rating-star').on('mouseenter', function() {
            const rating = $(this).data('rating');
            $('#starRating .rating-star').each(function(index) {
                if (index < rating) {
                    $(this).addClass('fas').removeClass('far');
                }
            });
        });
        
        $('#starRating').on('mouseleave', function() {
            const currentRating = parseInt($('#ratingValue').val()) || 0;
            $('#starRating .rating-star').each(function(index) {
                if (index >= currentRating) {
                    $(this).removeClass('fas').addClass('far');
                }
            });
        });
        
        // Image preview
        $('#reviewImage').on('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) {
                    window.showNotification('Image must be less than 5MB', 'warning');
                    this.value = '';
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(event) {
                    $('#previewImg').attr('src', event.target.result);
                    $('#imagePreview').slideDown(300);
                };
                reader.readAsDataURL(file);
            } else {
                $('#imagePreview').slideUp(300);
            }
        });
        
        $('#commentModal').on('hidden.bs.modal', function() {
            $('#commentModal').remove();
            $('.modal-backdrop').remove();
            $('body').removeClass('modal-open');
            $('body').css('overflow', '');
        });
        
        $('#commentModal').modal('show');
    }
};

// =====================================================
// ENHANCED MAP FUNCTIONS
// =====================================================

function initializeHotelMap() {
    const mapContainer = document.getElementById('hotelMap');
    if (!mapContainer) return;
    
    if (hotelMap) {
        hotelMap.invalidateSize();
        return;
    }
    
    // Create map
    hotelMap = L.map('hotelMap', {
        center: [HotelLocation.coordinates.lat, HotelLocation.coordinates.lng],
        zoom: MapConfig.defaultZoom,
        zoomControl: true,
        scrollWheelZoom: true,
        doubleClickZoom: true,
        dragging: true
    });
    
    // Add tile layer
    L.tileLayer(MapConfig.tileLayer, {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> | ABC hotels',
        maxZoom: MapConfig.maxZoom,
        minZoom: MapConfig.minZoom
    }).addTo(hotelMap);
    
    // Add hotel marker
    addHotelMarker();
    
    // Add nearby places
    addNearbyPlaces();
    
    // Add scale control
    L.control.scale({
        imperial: false,
        metric: true,
        position: 'bottomleft'
    }).addTo(hotelMap);
    
    // Invalidate size after delay
    setTimeout(() => {
        hotelMap.invalidateSize();
    }, 300);
}

function addHotelMarker() {
    const hotelIconHtml = `
        <div style="
            background: linear-gradient(135deg, #c9a84c, #a88838);
            color: white;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            box-shadow: 0 6px 20px rgba(201, 168, 76, 0.5), 0 0 30px rgba(201, 168, 76, 0.3);
            border: 3px solid white;
            animation: markerPulse 2s ease-in-out infinite;
        ">
            <i class="fas fa-crown"></i>
        </div>
    `;
    
    const hotelIcon = L.divIcon({
        html: hotelIconHtml,
        iconSize: [50, 50],
        iconAnchor: [25, 25],
        popupAnchor: [0, -28],
        className: 'custom-div-icon'
    });
    
    hotelMarker = L.marker([HotelLocation.coordinates.lat, HotelLocation.coordinates.lng], { 
        icon: hotelIcon,
        zIndexOffset: 1000
    })
        .addTo(hotelMap)
        .bindPopup(createHotelPopup(), { maxWidth: 320 })
        .openPopup();
    
    // Add pulsing circle
    pulseCircle = L.circle([HotelLocation.coordinates.lat, HotelLocation.coordinates.lng], {
        radius: 200,
        color: '#c9a84c',
        fillColor: '#c9a84c',
        fillOpacity: 0.1,
        weight: 1,
        dashArray: '5, 10',
        interactive: false
    }).addTo(hotelMap);
    
    // Animate pulse
    let growing = true;
    const pulseInterval = setInterval(() => {
        if (!pulseCircle || !hotelMap) {
            clearInterval(pulseInterval);
            return;
        }
        const currentRadius = pulseCircle.getRadius();
        if (growing) {
            pulseCircle.setRadius(currentRadius + 5);
            if (currentRadius > 300) growing = false;
        } else {
            pulseCircle.setRadius(currentRadius - 5);
            if (currentRadius < 180) growing = true;
        }
    }, 100);
}

function createHotelPopup() {
    return `
        <div style="font-family: 'Inter', sans-serif; padding: 8px; min-width: 220px;">
            <div style="text-align: center; margin-bottom: 8px;">
                <h5 style="color: #1a2744; margin: 0; font-weight: 700;">
                    ${HotelLocation.starDisplay}
                </h5>
                <h4 style="color: #1a2744; margin: 5px 0; font-family: 'Playfair Display', serif; font-weight: 700;">
                    ${HotelLocation.name}
                </h4>
            </div>
            <hr style="margin: 8px 0; border-color: #e8e0d5;">
            <p style="margin: 5px 0; font-size: 0.82rem;">
                <i class="fas fa-map-marker-alt" style="color: #c9a84c; width: 18px;"></i> 
                ${HotelLocation.address}
            </p>
            <p style="margin: 5px 0; font-size: 0.82rem;">
                <i class="fas fa-phone" style="color: #c9a84c; width: 18px;"></i> 
                ${HotelLocation.phone}
            </p>
            <div style="text-align: center; margin-top: 10px;">
                <button onclick="getUserLocationAndRoute()" 
                    style="background: linear-gradient(135deg, #c9a84c, #a88838); color: #1a2744; 
                    border: none; padding: 8px 16px; border-radius: 20px; font-weight: 600; 
                    cursor: pointer; font-size: 0.8rem; width: 100%;">
                    <i class="fas fa-location-arrow me-1"></i> Get Directions
                </button>
            </div>
        </div>
    `;
}

function addNearbyPlaces() {
    nearbyMarkers.forEach(m => hotelMap.removeLayer(m));
    nearbyMarkers = [];
    
    MapConfig.nearbyPlaces.forEach(place => {
        const distance = calculateDistance(
            HotelLocation.coordinates.lat, HotelLocation.coordinates.lng,
            place.lat, place.lng
        );
        
        const placeIcon = L.divIcon({
            html: `<div style="
                background: white;
                border-radius: 50%;
                width: 36px;
                height: 36px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.15);
                border: 2px solid #8b7355;
                cursor: pointer;
            ">${place.icon}</div>`,
            iconSize: [36, 36],
            iconAnchor: [18, 18],
            className: 'custom-div-icon'
        });
        
        const marker = L.marker([place.lat, place.lng], { icon: placeIcon })
            .addTo(hotelMap)
            .bindPopup(`
                <div style="font-family: 'Inter', sans-serif; padding: 5px;">
                    <strong style="color: #1a2744;">${place.name}</strong><br>
                    <small style="color: #6b7280;">${place.type}</small><br>
                    <small style="color: #8b7355; font-weight: 600;">
                        <i class="fas fa-route me-1"></i> ${distance} km
                    </small><br>
                    <button onclick="getDirectionsToPlace(${place.lat}, ${place.lng}, '${place.name.replace(/'/g, "\\'")}')" 
                        style="background: #1a2744; color: white; border: none; padding: 4px 12px; 
                        border-radius: 12px; font-size: 0.7rem; cursor: pointer; margin-top: 5px;">
                        <i class="fas fa-directions me-1"></i> Directions
                    </button>
                </div>
            `);
        
        nearbyMarkers.push(marker);
    });
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return (R * c).toFixed(1);
}

function getUserLocationAndRoute() {
    if (!navigator.geolocation) {
        window.showNotification('Geolocation not supported by your browser', 'warning');
        return;
    }
    
    window.showNotification('📍 Locating your position...', 'info');
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const userLat = position.coords.latitude;
            const userLng = position.coords.longitude;
            
            addUserMarker(userLat, userLng);
            
            const bounds = L.latLngBounds(
                [userLat, userLng],
                [HotelLocation.coordinates.lat, HotelLocation.coordinates.lng]
            );
            hotelMap.fitBounds(bounds, { padding: [80, 80] });
            
            calculateRoute(userLat, userLng, HotelLocation.coordinates.lat, HotelLocation.coordinates.lng);
        },
        function(error) {
            const messages = {
                1: 'Please enable location access in your browser settings',
                2: 'Unable to determine your location',
                3: 'Location request timed out'
            };
            window.showNotification(messages[error.code] || 'Could not get location', 'warning');
        },
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );
}

function getDirectionsToPlace(lat, lng, placeName) {
    if (!navigator.geolocation) {
        window.showNotification('Geolocation not supported', 'warning');
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const userLat = position.coords.latitude;
            const userLng = position.coords.longitude;
            
            addUserMarker(userLat, userLng);
            
            const bounds = L.latLngBounds(
                [userLat, userLng],
                [lat, lng]
            );
            hotelMap.fitBounds(bounds, { padding: [80, 80] });
            
            calculateRoute(userLat, userLng, lat, lng, placeName);
        },
        function(error) {
            window.showNotification('Could not get your location', 'warning');
        },
        { enableHighAccuracy: true, timeout: 15000 }
    );
}

function startLiveTracking() {
    if (!navigator.geolocation) {
        window.showNotification('Geolocation not supported', 'warning');
        return;
    }
    
    isLiveTracking = true;
    window.showNotification('🛰️ Live tracking started! Moving map will update automatically', 'success');
    
    // Update UI
    $('#startLiveTrackingBtn').hide();
    $('#stopLiveTrackingBtn').show();
    $('#liveTrackingStatus').show();
    
    // Center map on user
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                hotelMap.setView([position.coords.latitude, position.coords.longitude], 16);
                addUserMarker(position.coords.latitude, position.coords.longitude);
            },
            null,
            { enableHighAccuracy: true }
        );
    }
    
    // Start watching position
    liveLocationWatchId = navigator.geolocation.watchPosition(
        function(position) {
            const userLat = position.coords.latitude;
            const userLng = position.coords.longitude;
            
            addUserMarker(userLat, userLng);
            
            // Keep map centered on user during live tracking
            if (isLiveTracking) {
                hotelMap.setView([userLat, userLng], hotelMap.getZoom());
            }
            
            // Update route if exists
            if (routingControl) {
                routingControl.setWaypoints([
                    L.latLng(userLat, userLng),
                    L.latLng(HotelLocation.coordinates.lat, HotelLocation.coordinates.lng)
                ]);
            }
        },
        function(error) {
            console.error('Live tracking error:', error);
            if (error.code === 1) {
                window.showNotification('Location permission denied', 'error');
                stopLiveTracking();
            }
        },
        { 
            enableHighAccuracy: true, 
            maximumAge: 5000, 
            timeout: 30000,
            distanceFilter: 5  // Update every 5 meters
        }
    );
}

function stopLiveTracking() {
    if (liveLocationWatchId) {
        navigator.geolocation.clearWatch(liveLocationWatchId);
        liveLocationWatchId = null;
    }
    isLiveTracking = false;
    
    $('#startLiveTrackingBtn').show();
    $('#stopLiveTrackingBtn').hide();
    $('#liveTrackingStatus').hide();
    
    window.showNotification('Live tracking stopped', 'info');
}

function addUserMarker(lat, lng) {
    if (userMarker) {
        hotelMap.removeLayer(userMarker);
    }
    
    const userIcon = L.divIcon({
        html: `<div style="
            background: ${isLiveTracking ? '#ef4444' : '#2d6a4f'};
            color: white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px ${isLiveTracking ? 'rgba(239, 68, 68, 0.5)' : 'rgba(45, 106, 79, 0.5)'};
            border: 3px solid white;
            animation: ${isLiveTracking ? 'livePulse 1.5s ease-in-out infinite' : 'none'};
        ">
            <i class="fas fa-location-dot"></i>
        </div>`,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
        popupAnchor: [0, -22],
        className: 'custom-div-icon'
    });
    
    userMarker = L.marker([lat, lng], { 
        icon: userIcon,
        zIndexOffset: 500
    })
        .addTo(hotelMap)
        .bindPopup('<b>📍 Your Location</b>')
        .openPopup();
}

function calculateRoute(startLat, startLng, endLat, endLng, endName = null) {
    if (routingControl) {
        hotelMap.removeControl(routingControl);
    }
    
    routingControl = L.Routing.control({
        waypoints: [
            L.latLng(startLat, startLng),
            L.latLng(endLat, endLng)
        ],
        routeWhileDragging: false,
        showAlternatives: true,
        altLineOptions: {
            styles: [
                { color: '#8b7355', opacity: 0.3, weight: 3 },
                { color: '#6b7280', opacity: 0.2, weight: 2 }
            ]
        },
        lineOptions: {
            styles: [{ color: '#c9a84c', weight: 5, opacity: 0.8 }],
            extendToWaypoints: false,
            missingRouteTolerance: 10
        },
        createMarker: function() { return null; },
        addWaypoints: false,
        fitSelectedRoutes: false,
        show: false
    }).addTo(hotelMap);
    
    routingControl.on('routesfound', function(e) {
        const route = e.routes[0];
        const distance = (route.summary.totalDistance / 1000).toFixed(1);
        const duration = Math.round(route.summary.totalTime / 60);
        const hours = Math.floor(duration / 60);
        const mins = duration % 60;
        const durationText = hours > 0 ? `${hours}h ${mins}m` : `${mins} mins`;
        
        // Calculate estimated arrival
        const now = new Date();
        const arrival = new Date(now.getTime() + route.summary.totalTime * 1000);
        const arrivalText = arrival.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' });
        
        // Update route info panel
        $('#routeDistance').text(distance + ' km');
        $('#routeDuration').text(durationText);
        $('#routeArrival').text(arrivalText);
        $('#routeInfoPanel').addClass('show');
        
        // Update directions
        let directionsHtml = '<h6 style="color: #1a2744; margin-bottom: 12px; font-weight: 700;">📍 Turn-by-Turn Directions</h6>';
        directionsHtml += '<ol style="padding-left: 20px; margin: 0;">';
        route.instructions.forEach(instruction => {
            const dist = (instruction.distance / 1000).toFixed(1);
            directionsHtml += `
                <li style="margin-bottom: 8px; font-size: 0.85rem; color: #4a4a68;">
                    <i class="fas fa-${getDirectionIcon(instruction.type)}" style="color: #c9a84c; margin-right: 6px;"></i>
                    ${instruction.text} 
                    <small style="color: #8b7355; font-weight: 600;">(${dist} km)</small>
                </li>
            `;
        });
        directionsHtml += '</ol>';
        
        $('#directionsSteps').html(directionsHtml).slideDown(300);
        
        window.showNotification(`Route found: ${distance} km (~${durationText})`, 'success');
    });
    
    routingControl.on('routingerror', function(e) {
        console.error('Routing error:', e);
        window.showNotification('Could not find a route. Try a different location.', 'warning');
    });
}

function getDirectionIcon(type) {
    const icons = {
        'Head': 'fa-arrow-up',
        'Straight': 'fa-arrow-up',
        'Continue': 'fa-arrow-up',
        'TurnRight': 'fa-arrow-right',
        'SharpRight': 'fa-corner-up-right',
        'TurnLeft': 'fa-arrow-left',
        'SharpLeft': 'fa-corner-up-left',
        'SlightRight': 'fa-arrow-trend-up',
        'SlightLeft': 'fa-arrow-trend-down',
        'Roundabout': 'fa-circle-notch',
        'DestinationReached': 'fa-flag-checkered',
        'Fork': 'fa-code-branch',
        'EndOfStreet': 'fa-stop'
    };
    return icons[type] || 'fa-location-dot';
}

function resetMapToHotel() {
    if (hotelMap) {
        stopLiveTracking();
        
        hotelMap.setView([HotelLocation.coordinates.lat, HotelLocation.coordinates.lng], MapConfig.defaultZoom);
        
        if (routingControl) {
            hotelMap.removeControl(routingControl);
            routingControl = null;
        }
        
        if (userMarker) {
            hotelMap.removeLayer(userMarker);
            userMarker = null;
        }
        
        $('#routeInfoPanel').removeClass('show');
        $('#directionsSteps').slideUp(300).html('');
        
        window.showNotification('Map reset to hotel location', 'info');
    }
}

function destroyMap() {
    stopLiveTracking();
    
    if (hotelMap) {
        hotelMap.remove();
        hotelMap = null;
    }
    hotelMarker = null;
    userMarker = null;
    routingControl = null;
    pulseCircle = null;
    nearbyMarkers = [];
}

// =====================================================
// COUPON VALIDATION
// =====================================================
window.validateCouponCode = function() {
    const couponCode = $('#couponCode').val().trim();
    if (!couponCode) {
        window.showNotification('Please enter a promotional code', 'warning');
        return;
    }
    
    const roomId = $('#roomSelect').val();
    const checkIn = $('input[name="check_in"]').val();
    const checkOut = $('input[name="check_out"]').val();
    
    if (!roomId || !checkIn || !checkOut) {
        window.showNotification('Please select a room and dates first', 'warning');
        return;
    }
    
    const nights = window.calculateNights ? window.calculateNights(checkIn, checkOut) : 1;
    const selectedOption = $('#roomSelect option:selected');
    const priceMatch = selectedOption.text().match(/₱([\d,]+)/);
    const roomPrice = priceMatch ? parseFloat(priceMatch[1].replace(/,/g, '')) : 100;
    const totalAmount = roomPrice * nights;
    
    $.ajax({
        url: '/api/coupons/validate',
        method: 'POST',
        data: { coupon_code: couponCode, total_amount: totalAmount },
        success: function(response) {
            const $message = $('#couponMessage');
            if (response.valid) {
                $message.html(`<span class="text-success"><i class="fas fa-check-circle me-1"></i> ${response.message}</span>`);
                window.showNotification(response.message, 'success');
            } else {
                $message.html(`<span class="text-danger"><i class="fas fa-times-circle me-1"></i> ${response.message}</span>`);
                window.showNotification(response.message, 'warning');
            }
        },
        error: function() {
            window.showNotification('Unable to validate code. Please try again.', 'error');
        }
    });
};

// =====================================================
// FORM SUBMISSION HANDLERS
// =====================================================

window.submitBookingReservation = function() {
    const form = document.getElementById('bookingForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const formData = $('#bookingForm').serialize();
    const $btn = $('#bookingModal .btn-primary');
    const originalHtml = window.showLoading ? window.showLoading($btn, 'Processing...') : $btn.html();
    
    $.ajax({
        url: '/api/bookings/create',
        method: 'POST',
        data: formData,
        timeout: 30000,
        success: function(response) {
            if (window.hideLoading) window.hideLoading($btn);
            if (response.success) {
                window.showNotification(response.message || 'Reservation created!', 'success');
                $('#bookingModal').modal('hide');
                
                if (response.redirect) {
                    setTimeout(() => { window.location.href = response.redirect; }, 500);
                } else if (response.booking_id) {
                    setTimeout(() => { window.location.href = '/api/payments/checkout/' + response.booking_id; }, 500);
                } else {
                    setTimeout(() => { location.reload(); }, 800);
                }
            } else {
                window.showNotification(response.message || 'Unable to create reservation', 'error');
                $btn.prop('disabled', false).html(originalHtml);
            }
        },
        error: function(xhr) {
            if (window.hideLoading) window.hideLoading($btn);
            let errorMessage = 'Server error. Please try again.';
            if (xhr.responseJSON && xhr.responseJSON.message) errorMessage = xhr.responseJSON.message;
            window.showNotification(errorMessage, 'error');
        }
    });
};

window.submitAmenityForm = function() {
    const formData = $('#amenityForm').serialize();
    $.ajax({
        url: '/api/amenities/save',
        method: 'POST',
        data: formData,
        success: function(response) {
            if (response.success) {
                window.showNotification('Amenity saved!', 'success');
                $('#amenityModal').modal('hide');
                if (typeof loadAmenities === 'function') loadAmenities();
            } else {
                window.showNotification(response.message || 'Error saving amenity', 'error');
            }
        },
        error: function() { window.showNotification('Error saving amenity', 'error'); }
    });
};

window.submitRoomTypeForm = function() {
    const formData = $('#roomTypeForm').serialize();
    $.ajax({
        url: '/api/rooms/types/save',
        method: 'POST',
        data: formData,
        success: function(response) {
            if (response.success) {
                window.showNotification('Room category saved!', 'success');
                $('#roomTypeModal').modal('hide');
                if (typeof loadRoomTypes === 'function') loadRoomTypes();
            } else {
                window.showNotification(response.message || 'Error saving room category', 'error');
            }
        },
        error: function() { window.showNotification('Error saving room category', 'error'); }
    });
};

window.submitGuestReview = function() {
    const rating = $('#ratingValue').val();
    const comment = $('textarea[name="comment"]').val().trim();
    
    if (!rating) { $('#ratingError').slideDown(200); return; }
    if (!comment) { window.showNotification('Please write a review', 'warning'); return; }
    
    const formData = new FormData($('#commentForm')[0]);
    $.ajax({
        url: '/api/comments/add',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                window.showNotification('Thank you for your review! 🌟', 'success');
                $('#commentModal').modal('hide');
                setTimeout(() => location.reload(), 800);
            } else {
                window.showNotification(response.message || 'Error submitting review', 'error');
            }
        },
        error: function() { window.showNotification('Error submitting review', 'error'); }
    });
};

window.submitCouponForm = function() {
    const couponId = $('#couponId').val();
    const url = couponId ? `/api/coupons/update/${couponId}` : '/api/coupons/create';
    let formData = $('#couponForm').serialize();
    formData += '&is_active=' + $('#isActive').is(':checked');
    
    const $btn = $('#couponModal .btn-primary');
    if (window.showLoading) window.showLoading($btn, 'Saving...');
    
    $.ajax({
        url: url,
        method: 'POST',
        data: formData,
        success: function(response) {
            if (window.hideLoading) window.hideLoading($btn);
            if (response.success) {
                window.showNotification(response.message || 'Promotion saved!', 'success');
                $('#couponModal').modal('hide');
                if (typeof loadCoupons === 'function') loadCoupons();
            } else {
                window.showNotification(response.message || 'Error saving promotion', 'error');
            }
        },
        error: function() {
            if (window.hideLoading) window.hideLoading($btn);
            window.showNotification('Error saving promotion', 'error');
        }
    });
};

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// =====================================================
// INITIALIZATION
// =====================================================
console.log('%c🏨 ABC hotels Modal System v3.0 %cInitialized', 'color:#c9a84c;font-weight:bold;', 'color:#8b7355;');
console.log('%c📍 Location: %c' + HotelLocation.name, 'color:#c9a84c;', 'color:#1a2744;');
console.log('%c🗺️ Live Map %c✓ Ready', 'color:#2d6a4f;', 'color:#6b7280;');
console.log('%c🛰️ GPS Tracking %c✓ Available', 'color:#2d6a4f;', 'color:#6b7280;');