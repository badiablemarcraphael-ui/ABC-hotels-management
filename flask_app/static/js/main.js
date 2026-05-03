// =====================================================
// ABC hotels MANAGEMENT SYSTEM — CORE JAVASCRIPT
// Luxury Hotel 60-30-10 Design System Integration
// Philippine Peso Currency | Enhanced Animations
// =====================================================

'use strict';

// =====================================================
// GLOBAL CONFIGURATION
// =====================================================
const GrandHotelConfig = {
    animationDuration: 300,
    notificationDuration: 4500,
    apiTimeout: 15000,
    dateLocale: 'en-PH',
    currency: 'PHP',
    currencyLocale: 'en-PH',
    currencySymbol: '₱'
};

// =====================================================
// ELEGANT NOTIFICATION SYSTEM
// =====================================================
window.showNotification = function(message, type = 'info', duration = GrandHotelConfig.notificationDuration) {
    // Remove existing notifications with fade
    $('.grand-notification').addClass('notification-exit');
    setTimeout(() => $('.grand-notification').remove(), 400);
    
    const iconMap = {
        success: { icon: 'fa-circle-check', gradient: 'linear-gradient(135deg, #2d6a4f, #3d8b6a)' },
        error: { icon: 'fa-circle-exclamation', gradient: 'linear-gradient(135deg, #8b3a3a, #a84848)' },
        warning: { icon: 'fa-triangle-exclamation', gradient: 'linear-gradient(135deg, #b8860b, #d4a020)' },
        info: { icon: 'fa-circle-info', gradient: 'linear-gradient(135deg, #1a2744, #2c3e6b)' }
    };
    
    const config = iconMap[type] || iconMap.info;
    
    const notification = $(`
        <div class="grand-notification" role="alert" aria-live="polite">
            <div class="notification-glow" style="background: ${config.gradient};"></div>
            <div class="notification-content">
                <div class="notification-icon-wrapper" style="background: ${config.gradient};">
                    <i class="fas ${config.icon}"></i>
                </div>
                <div class="notification-body">
                    <p class="notification-message">${escapeHtml(message)}</p>
                </div>
                <button class="notification-close" aria-label="Close notification">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="notification-progress-bar">
                <div class="notification-progress-fill" style="background: ${config.gradient};"></div>
            </div>
        </div>
    `);
    
    $('body').append(notification);
    
    // Animate progress bar
    requestAnimationFrame(() => {
        notification.find('.notification-progress-fill').css('animation', 
            `notificationShrink ${duration}ms linear forwards`);
    });
    
    // Auto dismiss
    const timer = setTimeout(() => {
        dismissNotification(notification);
    }, duration);
    
    // Store timer reference
    notification.data('timer', timer);
    
    // Close button handler
    notification.find('.notification-close').on('click', function(e) {
        e.stopPropagation();
        clearTimeout(notification.data('timer'));
        dismissNotification(notification);
    });
    
    // Pause timer on hover
    notification.on('mouseenter', function() {
        clearTimeout(notification.data('timer'));
        notification.find('.notification-progress-fill').css('animation-play-state', 'paused');
    });
    
    notification.on('mouseleave', function() {
        const remainingDuration = 2000;
        const progressFill = notification.find('.notification-progress-fill');
        const currentWidth = parseFloat(progressFill.css('width')) || 100;
        const newDuration = (remainingDuration * currentWidth) / 100;
        
        progressFill.css('animation', `notificationShrink ${newDuration}ms linear forwards`);
        
        const newTimer = setTimeout(() => {
            dismissNotification(notification);
        }, newDuration);
        notification.data('timer', newTimer);
        progressFill.css('animation-play-state', 'running');
    });
};

function dismissNotification(notification) {
    notification.addClass('notification-exit');
    setTimeout(() => notification.remove(), 500);
}

// =====================================================
// UTILITY FUNCTIONS
// =====================================================

// Elegant Date Formatter
window.formatDate = function(dateString, format = 'long') {
    if (!dateString) return '—';
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Invalid Date';
    
    const options = {
        long: { year: 'numeric', month: 'long', day: 'numeric' },
        short: { year: 'numeric', month: 'short', day: 'numeric' },
        time: { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true },
        monthYear: { year: 'numeric', month: 'long' },
        iso: { year: 'numeric', month: '2-digit', day: '2-digit' }
    };
    
    return date.toLocaleDateString('en-PH', options[format] || options.long);
};

// Philippine Peso Currency Formatter
window.formatPHP = function(amount) {
    if (amount === null || amount === undefined) return '₱0.00';
    
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount)) return '₱0.00';
    
    return '₱' + numAmount.toLocaleString('en-PH', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
};

// Alias for backward compatibility
window.formatCurrency = window.formatPHP;

// Calculate nights between two dates
window.calculateNights = function(checkIn, checkOut) {
    if (!checkIn || !checkOut) return 0;
    const start = new Date(checkIn);
    const end = new Date(checkOut);
    const diffTime = Math.abs(end - start);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

// HTML Escape Utility
window.escapeHtml = function(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
};

// Escape Regex Special Characters
window.escapeRegex = function(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
};

// Debounce function for search inputs
window.debounce = function(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Generate Star HTML
window.generateStars = function(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = (rating - fullStars) >= 0.5;
    let html = '';
    
    for (let i = 1; i <= 5; i++) {
        if (i <= fullStars) {
            html += '<i class="fas fa-star text-warning"></i>';
        } else if (i === fullStars + 1 && hasHalfStar) {
            html += '<i class="fas fa-star-half-alt text-warning"></i>';
        } else {
            html += '<i class="far fa-star text-warning opacity-50"></i>';
        }
    }
    
    return html;
};

// Get Initials from Name
window.getInitials = function(name) {
    if (!name) return 'G';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return parts[0].substring(0, 2).toUpperCase();
};

// =====================================================
// ELEGANT LOADING STATE MANAGEMENT
// =====================================================
window.showLoading = function(button, message = 'Processing...') {
    const $btn = $(button);
    const originalHtml = $btn.html();
    const originalWidth = $btn.outerWidth();
    
    $btn.data('original-html', originalHtml);
    $btn.html(`
        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        <span>${message}</span>
    `);
    $btn.prop('disabled', true);
    if (originalWidth) {
        $btn.css('min-width', originalWidth + 'px');
    }
    
    return originalHtml;
};

window.hideLoading = function(button) {
    const $btn = $(button);
    const originalHtml = $btn.data('original-html');
    
    if (originalHtml) {
        $btn.html(originalHtml);
        $btn.prop('disabled', false);
        $btn.css('min-width', '');
        $btn.data('original-html', null);
    }
};

// =====================================================
// INJECT LUXURY ANIMATION STYLES
// =====================================================
$('head').append(`
    <style>
        /* =============================================
           LUXURY NOTIFICATION STYLES
           ============================================= */
        @keyframes notificationSlideIn {
            from {
                transform: translateX(120%) scale(0.9);
                opacity: 0;
            }
            to {
                transform: translateX(0) scale(1);
                opacity: 1;
            }
        }
        
        @keyframes notificationSlideOut {
            from {
                transform: translateX(0) scale(1);
                opacity: 1;
            }
            to {
                transform: translateX(120%) scale(0.9);
                opacity: 0;
            }
        }
        
        @keyframes notificationShrink {
            from { width: 100%; }
            to { width: 0%; }
        }
        
        @keyframes notificationGlowPulse {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }
        
        .grand-notification {
            position: fixed;
            top: 80px;
            right: 24px;
            z-index: 9999;
            min-width: 360px;
            max-width: 500px;
            background: #fdfcf9;
            border-radius: 16px;
            box-shadow: 0 12px 48px rgba(10, 15, 26, 0.15), 0 4px 16px rgba(201, 168, 76, 0.1);
            overflow: hidden;
            animation: notificationSlideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
            border: 1px solid rgba(201, 168, 76, 0.15);
        }
        
        .grand-notification.notification-exit {
            animation: notificationSlideOut 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }
        
        .notification-glow {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            opacity: 0.8;
        }
        
        .notification-content {
            display: flex;
            align-items: flex-start;
            padding: 18px 20px;
            gap: 14px;
        }
        
        .notification-icon-wrapper {
            flex-shrink: 0;
            width: 40px;
            height: 40px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            color: white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .notification-body {
            flex: 1;
            min-width: 0;
            display: flex;
            align-items: center;
        }
        
        .notification-message {
            margin: 0;
            font-size: 0.92rem;
            font-weight: 500;
            color: #1a2744;
            line-height: 1.5;
        }
        
        .notification-close {
            flex-shrink: 0;
            background: none;
            border: none;
            color: #8b7355;
            cursor: pointer;
            padding: 6px;
            border-radius: 50%;
            transition: all 0.2s ease;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 30px;
            height: 30px;
        }
        
        .notification-close:hover {
            color: #1a2744;
            background: rgba(0, 0, 0, 0.05);
            transform: rotate(90deg);
        }
        
        .notification-progress-bar {
            height: 3px;
            background: rgba(0, 0, 0, 0.05);
        }
        
        .notification-progress-fill {
            height: 100%;
            width: 100%;
            transform-origin: left;
        }
        
        /* Dark Mode Notifications */
        .dark-mode .grand-notification {
            background: #1c2135;
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
            border-color: rgba(201, 168, 76, 0.08);
        }
        
        .dark-mode .notification-message {
            color: #d4cec4;
        }
        
        .dark-mode .notification-close {
            color: #8b8a95;
        }
        
        .dark-mode .notification-close:hover {
            color: #d4cec4;
            background: rgba(255, 255, 255, 0.05);
        }
        
        /* =============================================
           ENHANCED ANIMATIONS
           ============================================= */
        @keyframes fadeInScale {
            from {
                opacity: 0;
                transform: scale(0.95);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes pulseGlow {
            0%, 100% { box-shadow: 0 0 0 0 rgba(201, 168, 76, 0.4); }
            50% { box-shadow: 0 0 0 12px rgba(201, 168, 76, 0); }
        }
        
        .hover-lift {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .hover-lift:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 36px rgba(10, 15, 26, 0.12);
        }
        
        /* =============================================
           PHILIPPINE PESO STYLING
           ============================================= */
        .currency-peso::before {
            content: "₱";
            margin-right: 2px;
            font-weight: 700;
        }
        
        .currency-amount::before {
            content: "₱";
            margin-right: 2px;
            font-weight: 700;
        }
        
        /* =============================================
           RESPONSIVE NOTIFICATIONS
           ============================================= */
        @media (max-width: 576px) {
            .grand-notification {
                min-width: auto;
                max-width: calc(100vw - 32px);
                left: 16px;
                right: 16px;
                top: 70px;
            }
        }
    </style>
`);

// =====================================================
// INITIALIZATION
// =====================================================
$(document).ready(function() {
    console.log('%c🏨 ABC hotels Core System — Initialized',
        'color: #c9a84c; font-size: 1.1em; font-weight: bold;');
    console.log('%c✨ Luxury Design System v2.5 Active | Philippine Peso (₱) Mode',
        'color: #8b7355;');
    
    // Global AJAX error handler
    $(document).ajaxError(function(event, jqXHR, settings, error) {
        // Skip notification for aborted requests
        if (jqXHR.statusText === 'abort') return;
        
        if (jqXHR.status === 401) {
            window.showNotification('Session expired. Redirecting to login...', 'warning', 3000);
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else if (jqXHR.status === 403) {
            window.showNotification('Access denied. Insufficient permissions.', 'error');
        } else if (jqXHR.status === 404) {
            window.showNotification('Resource not found. Please try again.', 'error');
        } else if (jqXHR.status === 0) {
            window.showNotification('Network error. Please check your connection.', 'error');
        } else if (jqXHR.status >= 500) {
            window.showNotification('Server error. Please try again later.', 'error');
        }
        
        console.error('AJAX Error:', {
            url: settings.url,
            method: settings.type,
            status: jqXHR.status,
            statusText: jqXHR.statusText,
            error: error
        });
    });
    
    // Global AJAX complete handler
    $(document).ajaxComplete(function() {
        // Restore any buttons that might be stuck in loading state
        $('.btn:disabled').each(function() {
            const $btn = $(this);
            const originalHtml = $btn.data('original-html');
            if (originalHtml && $btn.find('.spinner-border').length) {
                window.hideLoading($btn);
            }
        });
    });
    
    // Prevent double form submissions
    $('form').on('submit', function() {
        const $submitBtn = $(this).find('button[type="submit"]');
        if ($submitBtn.prop('disabled')) {
            return false;
        }
    });
});

console.log('✅ main.js loaded — ABC hotels Luxury Management System (PHP Mode)');

