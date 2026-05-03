// =====================================================
// GRAND HOTEL — LUXURY MODAL MANAGEMENT SYSTEM
// 60-30-10 Design: Gold Accents, Navy Depth, Cream Base
// =====================================================

'use strict';

// =====================================================
// HOTEL CONFIGURATION
// =====================================================
const HotelLocation = {
    name: 'Grand Hotel & Resort',
    address: '123 Luxury Avenue, Prestige District, Metropolitan City',
    phone: '+1-234-567-8900',
    email: 'concierge@grandhotel.com',
    coordinates: {
        lat: 14.5995,
        lng: 120.9842
    },
    rating: 5,
    starDisplay: '★★★★★'
};

// =====================================================
// ELEGANT MODAL STYLES INJECTION
// =====================================================
$('head').append(`
    <style>
        /* Luxury Modal Base Styles */
        .grand-modal .modal-content {
            border: none;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(26, 39, 68, 0.15), 0 4px 16px rgba(201, 168, 76, 0.08);
            overflow: hidden;
        }
        
        .grand-modal .modal-header {
            background: linear-gradient(135deg, var(--navy-900, #1a2744) 0%, var(--navy-800, #243356) 100%);
            color: white;
            border-bottom: 2px solid var(--gold-500, #c9a84c);
            padding: 20px 24px;
        }
        
        .grand-modal .modal-header .modal-title {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-weight: 600;
            letter-spacing: 0.5px;
            font-size: 1.3rem;
        }
        
        .grand-modal .btn-close {
            filter: brightness(0) invert(1);
            opacity: 0.8;
            transition: opacity 0.2s ease;
        }
        
        .grand-modal .btn-close:hover {
            opacity: 1;
        }
        
        .grand-modal .modal-body {
            padding: 24px;
            background: var(--warm-white, #fdfcf9);
        }
        
        .grand-modal .modal-footer {
            background: var(--cream, #f5f0e8);
            border-top: 1px solid rgba(201, 168, 76, 0.2);
            padding: 16px 24px;
        }
        
        .grand-modal .form-label {
            font-weight: 600;
            color: var(--navy-900, #1a2744);
            font-size: 0.85rem;
            letter-spacing: 0.3px;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        
        .grand-modal .form-control,
        .grand-modal .form-select {
            border: 2px solid var(--taupe, #e8e0d5);
            border-radius: 10px;
            padding: 10px 14px;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            background: white;
        }
        
        .grand-modal .form-control:focus,
        .grand-modal .form-select:focus {
            border-color: var(--gold-500, #c9a84c);
            box-shadow: 0 0 0 4px rgba(201, 168, 76, 0.1);
            outline: none;
        }
        
        .grand-modal .btn-primary {
            background: linear-gradient(135deg, var(--gold-500, #c9a84c) 0%, var(--gold-600, #a88838) 100%);
            border: none;
            padding: 10px 24px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            font-size: 0.85rem;
            border-radius: 8px;
            color: white;
            transition: all 0.3s ease;
        }
        
        .grand-modal .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(201, 168, 76, 0.3);
        }
        
        .grand-modal .btn-secondary {
            background: transparent;
            border: 2px solid var(--navy-900, #1a2744);
            color: var(--navy-900, #1a2744);
            padding: 10px 24px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            font-size: 0.85rem;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .grand-modal .btn-secondary:hover {
            background: var(--navy-900, #1a2744);
            color: white;
        }
        
        /* Map Styles */
        .map-container {
            border-radius: 12px;
            overflow: hidden;
            border: 2px solid var(--taupe, #e8e0d5);
        }
        
        .custom-div-icon {
            border: none !important;
            background: none !important;
        }
        
        /* Tab Styles */
        .luxury-tabs .nav-link {
            color: var(--bronze-500, #a89269);
            font-weight: 600;
            border: none;
            border-bottom: 3px solid transparent;
            padding: 12px 20px;
            transition: all 0.3s ease;
        }
        
        .luxury-tabs .nav-link:hover {
            color: var(--gold-600, #a88838);
            border-bottom-color: rgba(201, 168, 76, 0.3);
        }
        
        .luxury-tabs .nav-link.active {
            color: var(--gold-600, #a88838);
            border-bottom-color: var(--gold-500, #c9a84c);
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
            color: var(--gold-500, #c9a84c);
            transform: scale(1.1);
        }
        
        /* Dark Mode */
        .dark-mode .grand-modal .modal-body {
            background: var(--dark-surface, #1e1e30);
        }
        
        .dark-mode .grand-modal .modal-footer {
            background: #252540;
            border-top-color: rgba(201, 168, 76, 0.15);
        }
        
        .dark-mode .grand-modal .form-control,
        .dark-mode .grand-modal .form-select {
            background: #2a2a3e;
            border-color: rgba(201, 168, 76, 0.2);
            color: var(--taupe, #e8e0d5);
        }
        
        .dark-mode .grand-modal .form-label {
            color: var(--bronze-400, #c4b393);
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
            background: var(--gold-500, #c9a84c);
        }
        
        .luxury-switch input:checked + .slider:before {
            transform: translateX(22px);
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
            timeout: GrandHotel.config.apiTimeout,
            success: function(rooms) {
                let roomOptions = '<option value="">Select a luxurious room</option>';
                
                if (rooms && rooms.length > 0) {
                    rooms.forEach(room => {
                        const price = window.formatCurrency(room.base_price);
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
                                        <i class="fas fa-calendar-plus me-2" style="color: var(--gold-400, #dfc278);"></i>
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
                                                <i class="fas fa-map-location-dot me-2"></i>Location & Directions
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
                                                            <i class="fas fa-user me-1" style="color: var(--gold-500);"></i>
                                                            Guest Name *
                                                        </label>
                                                        <input type="text" class="form-control" name="guest_name" 
                                                               placeholder="Enter full name" required>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-envelope me-1" style="color: var(--gold-500);"></i>
                                                            Email Address *
                                                        </label>
                                                        <input type="email" class="form-control" name="guest_email" 
                                                               placeholder="guest@example.com" required>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-phone me-1" style="color: var(--gold-500);"></i>
                                                            Phone Number *
                                                        </label>
                                                        <input type="tel" class="form-control" name="guest_phone" 
                                                               placeholder="+1 (234) 567-8900" required>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-door-open me-1" style="color: var(--gold-500);"></i>
                                                            Select Room
                                                        </label>
                                                        <select class="form-select" name="room_id" id="roomSelect">
                                                            ${roomOptions}
                                                        </select>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-calendar-check me-1" style="color: var(--gold-500);"></i>
                                                            Check-in Date *
                                                        </label>
                                                        <input type="date" class="form-control" name="check_in" 
                                                               min="${new Date().toISOString().split('T')[0]}" required>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-calendar-times me-1" style="color: var(--gold-500);"></i>
                                                            Check-out Date *
                                                        </label>
                                                        <input type="date" class="form-control" name="check_out" required>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-user-friends me-1" style="color: var(--gold-500);"></i>
                                                            Adults
                                                        </label>
                                                        <input type="number" class="form-control" name="adults" 
                                                               value="1" min="1" max="10">
                                                    </div>
                                                    <div class="col-md-6">
                                                        <label class="form-label">
                                                            <i class="fas fa-child me-1" style="color: var(--gold-500);"></i>
                                                            Children
                                                        </label>
                                                        <input type="number" class="form-control" name="children" 
                                                               value="0" min="0" max="10">
                                                    </div>
                                                    <div class="col-12">
                                                        <label class="form-label">
                                                            <i class="fas fa-ticket-alt me-1" style="color: var(--gold-500);"></i>
                                                            Promotional Code
                                                        </label>
                                                        <div class="input-group">
                                                            <input type="text" class="form-control" name="coupon_code" 
                                                                   id="couponCode" placeholder="Enter code (optional)"
                                                                   style="text-transform: uppercase;">
                                                            <button class="btn btn-outline-gold" type="button" 
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
                                            <div class="alert alert-luxury mb-3">
                                                <i class="fas fa-hotel me-2" style="color: var(--gold-500);"></i>
                                                <strong>${HotelLocation.name}</strong><br>
                                                <small>${HotelLocation.address}</small>
                                            </div>
                                            <div class="map-container mb-3">
                                                <div id="hotelMap" style="height: 400px; width: 100%;"></div>
                                            </div>
                                            <div class="d-flex gap-2">
                                                <button class="btn btn-gold btn-sm" id="getDirectionsBtn">
                                                    <i class="fas fa-location-dot me-1"></i> Get Directions
                                                </button>
                                                <button class="btn btn-outline-gold btn-sm" id="resetMapBtn">
                                                    <i class="fas fa-undo me-1"></i> Reset Map
                                                </button>
                                            </div>
                                            <div id="directionsInfo" class="mt-3" style="display: none;">
                                                <div class="route-summary"></div>
                                                <div id="directionsSteps" class="route-steps"></div>
                                            </div>
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
                
                // Initialize map when modal is shown
                $('#bookingModal').on('shown.bs.modal', function() {
                    setTimeout(() => initializeHotelMap(), 200);
                });
                
                // Map button handlers
                $('#getDirectionsBtn').on('click', getUserLocationAndRoute);
                $('#resetMapBtn').on('click', resetMapToHotel);
                
                // Date validation
                $('input[name="check_in"]').on('change', function() {
                    const checkIn = $(this).val();
                    $('input[name="check_out"]').attr('min', checkIn);
                });
                
                // Pre-select room if provided
                if (roomId) {
                    $('#roomSelect').val(roomId);
                }
                
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
                                <i class="fas fa-spa me-2" style="color: var(--gold-400);"></i>
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
                                        <i class="fas fa-dollar-sign me-1"></i> Price per Day
                                    </label>
                                    <div class="input-group">
                                        <span class="input-group-text" style="background: var(--cream); border-color: var(--taupe);">$</span>
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
        $('#amenityModal').modal('show');
    },
    
    // ==========================================
    // USER MODAL
    // ==========================================
    showUserModal: function(user = null) {
        const isEdit = user !== null;
        
        const modalHtml = `
            <div class="modal fade grand-modal" id="userModal" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-user-plus me-2" style="color: var(--gold-400);"></i>
                                ${isEdit ? 'Edit' : 'Add'} Guest Profile
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="userForm">
                                <input type="hidden" name="user_id" id="userId" value="${isEdit ? user.user_id : ''}">
                                <div class="mb-3">
                                    <label class="form-label" for="username">
                                        <i class="fas fa-user me-1"></i> Username *
                                    </label>
                                    <input type="text" class="form-control" name="username" id="username" 
                                           value="${isEdit ? escapeHtml(user.username) : ''}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label" for="password">
                                        <i class="fas fa-lock me-1"></i> 
                                        Password ${isEdit ? '(leave blank to keep current)' : '*'}
                                    </label>
                                    <input type="password" class="form-control" name="password" id="password" 
                                           ${isEdit ? '' : 'required'} 
                                           placeholder="${isEdit ? '••••••••' : 'Enter secure password'}">
                                </div>
                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <label class="form-label" for="email">
                                            <i class="fas fa-envelope me-1"></i> Email
                                        </label>
                                        <input type="email" class="form-control" name="email" id="email" 
                                               value="${isEdit ? escapeHtml(user.email || '') : ''}">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label" for="phone">
                                            <i class="fas fa-phone me-1"></i> Phone
                                        </label>
                                        <input type="tel" class="form-control" name="phone" id="phone" 
                                               value="${isEdit ? escapeHtml(user.phone || '') : ''}">
                                    </div>
                                </div>
                                <div class="mb-3 mt-3">
                                    <label class="form-label" for="role">
                                        <i class="fas fa-shield-halved me-1"></i> Role
                                    </label>
                                    <select class="form-select" name="role" id="role">
                                        <option value="admin" ${isEdit && user.role === 'admin' ? 'selected' : ''}>
                                            👑 Administrator
                                        </option>
                                        <option value="manager" ${isEdit && user.role === 'manager' ? 'selected' : ''}>
                                            📊 Manager
                                        </option>
                                        <option value="receptionist" ${isEdit && user.role === 'receptionist' ? 'selected' : ''}>
                                            🛎️ Receptionist
                                        </option>
                                        <option value="guest" ${isEdit && user.role === 'guest' ? 'selected' : ''}>
                                            🏨 Guest
                                        </option>
                                    </select>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="submitUserForm()">
                                <i class="fas fa-user-check me-1"></i> Save Profile
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#modals-container').html(modalHtml);
        $('#userModal').modal('show');
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
                                <i class="fas fa-star me-2" style="color: var(--gold-400);"></i>
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
        
        // Star rating hover effect
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
        
        $('#commentModal').modal('show');
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
                                <i class="fas fa-door-open me-2" style="color: var(--gold-400);"></i>
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
                                            <i class="fas fa-dollar-sign me-1"></i> Base Price *
                                        </label>
                                        <div class="input-group">
                                            <span class="input-group-text" style="background: var(--cream);">$</span>
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
                                <i class="fas fa-ticket-alt me-2" style="color: var(--gold-400);"></i>
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
                                                Fixed Amount ($)
                                            </option>
                                        </select>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label" for="discountValue">
                                            <i class="fas fa-dollar-sign me-1"></i> Discount Value *
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
                                    <div class="input-group">
                                        <span class="input-group-text" style="background: var(--cream);">$</span>
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
                                
                                <div class="p-3 rounded" style="background: rgba(201, 168, 76, 0.05); border: 1px solid var(--taupe);">
                                    <label class="luxury-switch mb-0">
                                        <input type="checkbox" name="is_active" id="isActive" 
                                               ${isEdit && (coupon.is_active === 1 || coupon.is_active === true) ? 'checked' : 'checked'}>
                                        <span class="slider"></span>
                                    </label>
                                    <span class="ms-3 fw-semibold" style="color: var(--navy-900);">
                                        <i class="fas fa-circle-check me-1" style="color: var(--success);"></i>
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
        $('#couponModal').modal('show');
    }
};

// =====================================================
// MAP FUNCTIONS
// =====================================================
let hotelMap = null;
let routingControl = null;
let hotelMarker = null;

function initializeHotelMap() {
    const mapContainer = document.getElementById('hotelMap');
    if (!mapContainer) return;
    
    if (hotelMap) {
        hotelMap.invalidateSize();
        return;
    }
    
    // Initialize map with luxury styling
    hotelMap = L.map('hotelMap').setView([HotelLocation.coordinates.lat, HotelLocation.coordinates.lng], 15);
    
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19,
        minZoom: 3
    }).addTo(hotelMap);
    
    // Gold hotel marker
    const hotelIconHtml = `
        <div style="background: linear-gradient(135deg, #c9a84c, #a88838); color: white; border-radius: 50%; 
                    width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; 
                    font-size: 20px; box-shadow: 0 4px 12px rgba(201, 168, 76, 0.4); 
                    border: 3px solid white;">
            <i class="fas fa-crown"></i>
        </div>
    `;
    
    const hotelIcon = L.divIcon({
        html: hotelIconHtml,
        iconSize: [44, 44],
        className: 'custom-div-icon'
    });
    
    hotelMarker = L.marker([HotelLocation.coordinates.lat, HotelLocation.coordinates.lng], { icon: hotelIcon })
        .addTo(hotelMap)
        .bindPopup(`
            <div style="font-family: 'Segoe UI', sans-serif; padding: 5px;">
                <h6 style="color: #1a2744; margin: 0 0 5px 0;">
                    ${HotelLocation.starDisplay} ${HotelLocation.name}
                </h6>
                <p style="margin: 3px 0; font-size: 0.85rem;">${HotelLocation.address}</p>
                <p style="margin: 3px 0; font-size: 0.85rem;">📞 ${HotelLocation.phone}</p>
            </div>
        `)
        .openPopup();
    
    // Add nearby points of interest
    addNearbyPlaces();
}

function addNearbyPlaces() {
    const places = [
        { name: 'Airport', lat: HotelLocation.coordinates.lat - 0.008, lng: HotelLocation.coordinates.lng - 0.005, 
          icon: '✈️', type: 'Transportation' },
        { name: 'Shopping District', lat: HotelLocation.coordinates.lat + 0.002, lng: HotelLocation.coordinates.lng + 0.003, 
          icon: '🛍️', type: 'Shopping' },
        { name: 'Fine Dining', lat: HotelLocation.coordinates.lat + 0.001, lng: HotelLocation.coordinates.lng - 0.004, 
          icon: '🍽️', type: 'Restaurant' },
        { name: 'Central Park', lat: HotelLocation.coordinates.lat + 0.003, lng: HotelLocation.coordinates.lng + 0.002, 
          icon: '🌳', type: 'Park' }
    ];
    
    places.forEach(place => {
        const placeIcon = L.divIcon({
            html: `<div style="background: white; border-radius: 50%; width: 32px; height: 32px; 
                          display: flex; align-items: center; justify-content: center; font-size: 16px; 
                          box-shadow: 0 2px 8px rgba(0,0,0,0.15); border: 2px solid #8b7355;">
                        ${place.icon}
                   </div>`,
            iconSize: [32, 32],
            className: 'custom-div-icon'
        });
        
        L.marker([place.lat, place.lng], { icon: placeIcon })
            .addTo(hotelMap)
            .bindPopup(`<b>${place.name}</b><br><small>${place.type}</small>`);
    });
}

function getUserLocationAndRoute() {
    if (!navigator.geolocation) {
        window.showNotification('Geolocation not supported by your browser', 'warning');
        return;
    }
    
    window.showNotification('Locating your position...', 'info');
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const userLat = position.coords.latitude;
            const userLng = position.coords.longitude;
            
            // Add user marker
            const userIcon = L.divIcon({
                html: `<div style="background: #2d6a4f; color: white; border-radius: 50%; width: 36px; height: 36px; 
                              display: flex; align-items: center; justify-content: center; 
                              box-shadow: 0 4px 12px rgba(45, 106, 79, 0.4); border: 3px solid white;">
                            <i class="fas fa-location-dot"></i>
                       </div>`,
                iconSize: [36, 36],
                className: 'custom-div-icon'
            });
            
            L.marker([userLat, userLng], { icon: userIcon })
                .addTo(hotelMap)
                .bindPopup('<b>Your Location</b>')
                .openPopup();
            
            // Fit bounds to show both points
            const bounds = L.latLngBounds(
                [userLat, userLng], 
                [HotelLocation.coordinates.lat, HotelLocation.coordinates.lng]
            );
            hotelMap.fitBounds(bounds, { padding: [60, 60] });
            
            // Calculate route
            calculateRoute(userLat, userLng);
        },
        function(error) {
            const messages = {
                1: 'Please enable location access to see directions',
                2: 'Unable to determine your location',
                3: 'Location request timed out'
            };
            window.showNotification(messages[error.code] || 'Could not get your location', 'warning');
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
}

function calculateRoute(startLat, startLng) {
    if (routingControl) {
        hotelMap.removeControl(routingControl);
    }
    
    routingControl = L.Routing.control({
        waypoints: [
            L.latLng(startLat, startLng),
            L.latLng(HotelLocation.coordinates.lat, HotelLocation.coordinates.lng)
        ],
        routeWhileDragging: false,
        showAlternatives: false,
        lineOptions: {
            styles: [{ color: '#c9a84c', weight: 5, opacity: 0.7 }]
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
        
        let directionsHtml = '<h6 style="color: #1a2744;">Turn-by-Turn Directions:</h6><ol class="ps-3">';
        route.instructions.forEach(instruction => {
            directionsHtml += `
                <li style="margin-bottom: 8px;">
                    ${instruction.text} 
                    <small class="text-muted">(${(instruction.distance / 1000).toFixed(1)} km)</small>
                </li>
            `;
        });
        directionsHtml += '</ol>';
        
        $('#directionsInfo').slideDown(300);
        $('.route-summary').html(`
            <div class="alert alert-luxury">
                <i class="fas fa-route me-2"></i>
                <strong>${distance} km</strong> · approximately <strong>${duration} minutes</strong>
            </div>
        `);
        $('#directionsSteps').html(directionsHtml);
        
        window.showNotification(`Route found: ${distance} km (~${duration} min)`, 'success');
    });
}

function resetMapToHotel() {
    if (hotelMap) {
        hotelMap.setView([HotelLocation.coordinates.lat, HotelLocation.coordinates.lng], 15);
        
        if (routingControl) {
            hotelMap.removeControl(routingControl);
            routingControl = null;
        }
        
        $('#directionsInfo').slideUp(300);
        
        // Remove user markers only
        hotelMap.eachLayer(function(layer) {
            if (layer instanceof L.Marker && layer !== hotelMarker) {
                const popup = layer.getPopup();
                if (popup && popup.getContent().includes('Your Location')) {
                    hotelMap.removeLayer(layer);
                }
            }
        });
        
        window.showNotification('Map reset to hotel location', 'info');
    }
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
    
    const nights = window.calculateNights(checkIn, checkOut);
    const selectedOption = $('#roomSelect option:selected');
    const priceMatch = selectedOption.text().match(/\$([\d,]+)/);
    const roomPrice = priceMatch ? parseFloat(priceMatch[1].replace(/,/g, '')) : 100;
    const totalAmount = roomPrice * nights;
    
    $.ajax({
        url: '/api/coupons/validate',
        method: 'POST',
        data: {
            coupon_code: couponCode,
            total_amount: totalAmount
        },
        success: function(response) {
            const $message = $('#couponMessage');
            if (response.valid) {
                $message.html(`
                    <span class="text-success">
                        <i class="fas fa-check-circle me-1"></i> ${response.message}
                    </span>
                `);
                window.showNotification(response.message, 'success');
            } else {
                $message.html(`
                    <span class="text-danger">
                        <i class="fas fa-times-circle me-1"></i> ${response.message}
                    </span>
                `);
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

// Booking Submission
window.submitBookingReservation = function() {
    const form = document.getElementById('bookingForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Get form data
    const formData = $('#bookingForm').serialize();
    const $btn = $('#bookingModal .btn-primary');
    const originalText = window.showLoading ? window.showLoading($btn, 'Processing Reservation...') : ($btn.html('<i class="fas fa-spinner fa-spin me-2"></i> Processing...'), $btn.html());
    
    // Show loading state
    $btn.prop('disabled', true);
    $btn.html('<i class="fas fa-spinner fa-spin me-2"></i> Processing Reservation...');
    
    $.ajax({
        url: '/api/bookings/create',
        method: 'POST',
        data: formData,
        timeout: 30000, // 30 seconds timeout
        success: function(response) {
            if (response.success) {
                // Show success notification
                if (window.showNotification) {
                    window.showNotification(response.message || 'Reservation created successfully!', 'success');
                } else {
                    alert(response.message || 'Reservation created successfully!');
                }
                
                // Log discount info if applied
                if (response.discount_applied && response.discount_applied > 0) {
                    console.log('Discount applied: $' + response.discount_applied);
                }
                
                // Hide modal
                $('#bookingModal').modal('hide');
                
                // Redirect to payment page
                if (response.redirect) {
                    setTimeout(function() {
                        window.location.href = response.redirect;
                    }, 500);
                } else if (response.booking_id) {
                    // Fallback redirect
                    setTimeout(function() {
                        window.location.href = '/api/payments/checkout/' + response.booking_id;
                    }, 500);
                } else {
                    setTimeout(function() {
                        location.reload();
                    }, 800);
                }
            } else {
                // Show error message
                if (window.showNotification) {
                    window.showNotification(response.message || 'Unable to create reservation', 'error');
                } else {
                    alert(response.message || 'Unable to create reservation');
                }
                // Reset button
                $btn.prop('disabled', false);
                $btn.html(originalText || 'Proceed to Payment');
            }
        },
        error: function(xhr) {
            console.error('Booking error:', xhr);
            let errorMessage = 'Server error. Please try again.';
            
            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMessage = xhr.responseJSON.message;
            } else if (xhr.status === 0) {
                errorMessage = 'Network error. Please check your connection.';
            } else if (xhr.status === 500) {
                errorMessage = 'Server error. Please try again later.';
            }
            
            if (window.showNotification) {
                window.showNotification(errorMessage, 'error');
            } else {
                alert(errorMessage);
            }
            
            // Reset button
            $btn.prop('disabled', false);
            $btn.html(originalText || 'Proceed to Payment');
        }
    });
};

// Amenity Submission
window.submitAmenityForm = function() {
    const formData = $('#amenityForm').serialize();
    
    $.ajax({
        url: '/api/amenities/save',
        method: 'POST',
        data: formData,
        success: function(response) {
            if (response.success) {
                window.showNotification('Amenity saved successfully!', 'success');
                $('#amenityModal').modal('hide');
                setTimeout(() => location.reload(), 600);
            } else {
                window.showNotification(response.message || 'Error saving amenity', 'error');
            }
        },
        error: function() {
            window.showNotification('Error saving amenity', 'error');
        }
    });
};

// User Submission
window.submitUserForm = function() {
    const userId = $('#userId').val();
    const username = $('#username').val().trim();
    const password = $('#password').val();
    
    if (!username) {
        window.showNotification('Username is required', 'error');
        return;
    }
    
    if (!userId && !password) {
        window.showNotification('Password is required for new users', 'error');
        return;
    }
    
    const formData = new FormData($('#userForm')[0]);
    const $btn = $('#userModal .btn-primary');
    const originalText = window.showLoading($btn, 'Saving Profile...');
    
    $.ajax({
        url: '/api/users/save',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            window.hideLoading($btn);
            if (response.success) {
                window.showNotification(userId ? 'Profile updated successfully!' : 'User created successfully!', 'success');
                $('#userModal').modal('hide');
                setTimeout(() => location.reload(), 600);
            } else {
                window.showNotification(response.message || 'Error saving user', 'error');
            }
        },
        error: function() {
            window.hideLoading($btn);
            window.showNotification('Error saving user profile', 'error');
        }
    });
};

// Review Submission
window.submitGuestReview = function() {
    const rating = $('#ratingValue').val();
    const comment = $('textarea[name="comment"]').val().trim();
    
    if (!rating) {
        $('#ratingError').slideDown(200);
        return;
    }
    
    if (!comment) {
        window.showNotification('Please write a review', 'warning');
        return;
    }
    
    const formData = new FormData($('#commentForm')[0]);
    const $btn = $('#commentModal .btn-primary');
    const originalText = window.showLoading($btn, 'Submitting Review...');
    
    $.ajax({
        url: '/api/comments/add',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            window.hideLoading($btn);
            if (response.success) {
                window.showNotification('Thank you for your review! 🌟', 'success');
                $('#commentModal').modal('hide');
                setTimeout(() => location.reload(), 800);
            } else {
                window.showNotification(response.message || 'Error submitting review', 'error');
            }
        },
        error: function() {
            window.hideLoading($btn);
            window.showNotification('Error submitting review', 'error');
        }
    });
};

// Room Type Submission
window.submitRoomTypeForm = function() {
    const formData = $('#roomTypeForm').serialize();
    
    $.ajax({
        url: '/api/rooms/types/save',
        method: 'POST',
        data: formData,
        success: function(response) {
            if (response.success) {
                window.showNotification('Room category saved successfully!', 'success');
                $('#roomTypeModal').modal('hide');
                setTimeout(() => location.reload(), 600);
            } else {
                window.showNotification(response.message || 'Error saving room category', 'error');
            }
        },
        error: function() {
            window.showNotification('Error saving room category', 'error');
        }
    });
};

// Coupon Submission
window.submitCouponForm = function() {
    const couponId = $('#couponId').val();
    const url = couponId ? `/api/coupons/update/${couponId}` : '/api/coupons/create';
    let formData = $('#couponForm').serialize();
    formData += '&is_active=' + $('#isActive').is(':checked');
    
    const $btn = $('#couponModal .btn-primary');
    const originalText = window.showLoading($btn, 'Saving Promotion...');
    
    $.ajax({
        url: url,
        method: 'POST',
        data: formData,
        success: function(response) {
            window.hideLoading($btn);
            if (response.success) {
                window.showNotification(response.message || 'Promotion saved!', 'success');
                $('#couponModal').modal('hide');
                if (typeof loadCoupons === 'function') {
                    loadCoupons();
                } else {
                    setTimeout(() => location.reload(), 600);
                }
            } else {
                window.showNotification(response.message || 'Error saving promotion', 'error');
            }
        },
        error: function() {
            window.hideLoading($btn);
            window.showNotification('Error saving promotion', 'error');
        }
    });
};

// =====================================================
// DELETE FUNCTIONS
// =====================================================
window.deleteAmenity = function(amenityId) {
    if (confirm('Are you sure you want to remove this amenity?')) {
        $.ajax({
            url: `/api/amenities/delete/${amenityId}`,
            method: 'DELETE',
            success: function(response) {
                if (response.success) {
                    window.showNotification('Amenity removed successfully', 'success');
                    setTimeout(() => location.reload(), 500);
                }
            },
            error: function() {
                window.showNotification('Error removing amenity', 'error');
            }
        });
    }
};

window.deleteUser = function(userId) {
    if (confirm('Are you sure you want to remove this user profile?')) {
        $.ajax({
            url: `/api/users/delete/${userId}`,
            method: 'DELETE',
            success: function(response) {
                if (response.success) {
                    window.showNotification('User profile removed', 'success');
                    setTimeout(() => location.reload(), 500);
                }
            },
            error: function() {
                window.showNotification('Error removing user', 'error');
            }
        });
    }
};

// =====================================================
// INITIALIZATION
// =====================================================
console.log('🏨 Grand Hotel Modal System — Initialized');
console.log('📍 Location:', HotelLocation.name);
console.log('🗺️ Map integration ready');