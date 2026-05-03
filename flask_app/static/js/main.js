// =====================================================
// GRAND HOTEL MANAGEMENT SYSTEM — CORE JAVASCRIPT
// Luxury Hotel 60-30-10 Design System Integration
// =====================================================

'use strict';

// =====================================================
// GLOBAL CONFIGURATION
// =====================================================
const GrandHotel = {
    config: {
        animationDuration: 300,
        notificationDuration: 4000,
        apiTimeout: 15000,
        dateLocale: 'en-US',
        currency: 'USD',
        currencyLocale: 'en-US'
    },
    
    // Luxury color palette for dynamic elements
    colors: {
        gold: '#c9a84c',
        goldDark: '#a88838',
        goldLight: '#dfc278',
        navy: '#1a2744',
        navyLight: '#2c3e6b',
        bronze: '#8b7355',
        cream: '#f5f0e8',
        warmWhite: '#fdfcf9',
        success: '#2d6a4f',
        danger: '#8b3a3a',
        warning: '#b8860b',
        info: '#4a7c96'
    }
};

// =====================================================
// ELEGANT NOTIFICATION SYSTEM
// =====================================================
window.showNotification = function(message, type = 'info', duration = GrandHotel.config.notificationDuration) {
    // Remove existing notifications with fade
    $('.grand-notification').addClass('notification-exit');
    setTimeout(() => $('.grand-notification').remove(), 400);
    
    const iconMap = {
        success: { icon: 'fa-circle-check', border: GrandHotel.colors.success },
        error: { icon: 'fa-circle-exclamation', border: GrandHotel.colors.danger },
        warning: { icon: 'fa-triangle-exclamation', border: GrandHotel.colors.warning },
        info: { icon: 'fa-circle-info', border: GrandHotel.colors.navy }
    };
    
    const config = iconMap[type] || iconMap.info;
    
    const notification = $(`
        <div class="grand-notification" role="alert" aria-live="polite">
            <div class="notification-content">
                <div class="notification-icon">
                    <i class="fas ${config.icon}"></i>
                </div>
                <div class="notification-body">
                    <p class="notification-message">${escapeHtml(message)}</p>
                </div>
                <button class="notification-close" aria-label="Close notification">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="notification-progress" style="background: ${config.border};"></div>
        </div>
    `);
    
    $('body').append(notification);
    
    // Animate progress bar
    setTimeout(() => {
        notification.find('.notification-progress').css('width', '0%');
    }, 100);
    
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
        notification.find('.notification-progress').css('animation-play-state', 'paused');
    });
    
    notification.on('mouseleave', function() {
        const newTimer = setTimeout(() => {
            dismissNotification(notification);
        }, 2000);
        notification.data('timer', newTimer);
        notification.find('.notification-progress').css('animation-play-state', 'running');
    });
};

function dismissNotification(notification) {
    notification.addClass('notification-exit');
    setTimeout(() => notification.remove(), 400);
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
        time: { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' },
        monthYear: { year: 'numeric', month: 'long' }
    };
    
    return date.toLocaleDateString(GrandHotel.config.dateLocale, options[format] || options.long);
};

// Luxury Currency Formatter
window.formatCurrency = function(amount, currency = GrandHotel.config.currency) {
    if (amount === null || amount === undefined) return '$0.00';
    
    return new Intl.NumberFormat(GrandHotel.config.currencyLocale, {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
};

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

// =====================================================
// ELEGANT LOADING STATE MANAGEMENT
// =====================================================
window.showLoading = function(button, message = 'Processing...') {
    const $btn = $(button);
    const originalHtml = $btn.html();
    const originalWidth = $btn.width();
    
    $btn.data('original-html', originalHtml);
    $btn.html(`
        <span class="spinner-gold">
            <i class="fas fa-spinner fa-pulse"></i>
        </span>
        <span class="loading-text">${message}</span>
    `);
    $btn.prop('disabled', true);
    $btn.css('min-width', originalWidth + 'px');
    
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
// LAZY LOADING FOR IMAGES
// =====================================================
window.initLazyLoading = function() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy-image');
                    img.classList.add('lazy-loaded');
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.01
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for older browsers
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.src = img.dataset.src;
            img.classList.remove('lazy-image');
        });
    }
};

// =====================================================
// INJECT LUXURY ANIMATION STYLES
// =====================================================
$('head').append(`
    <style>
        /* Luxury Notification Styles */
        @keyframes notificationSlideIn {
            from {
                transform: translateX(120%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes notificationSlideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(120%);
                opacity: 0;
            }
        }
        
        @keyframes progressShrink {
            from { width: 100%; }
            to { width: 0%; }
        }
        
        @keyframes goldPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .grand-notification {
            position: fixed;
            top: 24px;
            right: 24px;
            z-index: 9999;
            min-width: 360px;
            max-width: 480px;
            background: var(--warm-white, #fdfcf9);
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(26, 39, 68, 0.12), 0 2px 8px rgba(201, 168, 76, 0.08);
            overflow: hidden;
            animation: notificationSlideIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            border-left: 4px solid var(--gold-500, #c9a84c);
        }
        
        .grand-notification.notification-exit {
            animation: notificationSlideOut 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }
        
        .notification-content {
            display: flex;
            align-items: flex-start;
            padding: 16px 20px;
            gap: 14px;
        }
        
        .notification-icon {
            flex-shrink: 0;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
        }
        
        .notification-icon .fa-circle-check { color: var(--success, #2d6a4f); }
        .notification-icon .fa-circle-exclamation { color: var(--danger, #8b3a3a); }
        .notification-icon .fa-triangle-exclamation { color: var(--warning, #b8860b); }
        .notification-icon .fa-circle-info { color: var(--navy-900, #1a2744); }
        
        .notification-body {
            flex: 1;
            min-width: 0;
        }
        
        .notification-message {
            margin: 0;
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--navy-900, #1a2744);
            line-height: 1.5;
        }
        
        .notification-close {
            flex-shrink: 0;
            background: none;
            border: none;
            color: var(--bronze-500, #a89269);
            cursor: pointer;
            padding: 4px;
            border-radius: 50%;
            transition: all 0.2s ease;
            font-size: 0.85rem;
        }
        
        .notification-close:hover {
            color: var(--navy-900, #1a2744);
            background: rgba(0, 0, 0, 0.05);
        }
        
        .notification-progress {
            height: 3px;
            width: 100%;
            animation: progressShrink 4s linear forwards;
        }
        
        /* Dark Mode Notifications */
        .dark-mode .grand-notification {
            background: var(--dark-surface, #1e1e30);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .dark-mode .notification-message {
            color: var(--taupe, #e8e0d5);
        }
        
        .dark-mode .notification-close {
            color: var(--bronze-400, #c4b393);
        }
        
        /* Gold Spinner */
        .spinner-gold {
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }
        
        .spinner-gold i {
            color: var(--gold-500, #c9a84c);
            animation: goldPulse 1.5s ease-in-out infinite;
        }
        
        .loading-text {
            margin-left: 8px;
            font-weight: 500;
            color: inherit;
        }
        
        /* Lazy Loading Images */
        .lazy-image {
            opacity: 0;
            transition: opacity 0.5s ease;
        }
        
        .lazy-loaded {
            opacity: 1;
        }
        
        /* Responsive Notifications */
        @media (max-width: 576px) {
            .grand-notification {
                min-width: auto;
                max-width: calc(100vw - 32px);
                left: 16px;
                right: 16px;
                top: 16px;
            }
        }
    </style>
`);

// =====================================================
// INITIALIZATION
// =====================================================
$(document).ready(function() {
    console.log('🏨 Grand Hotel Core System — Initialized');
    console.log('✨ Luxury Design System v2.0 Active');
    
    // Initialize lazy loading for images
    window.initLazyLoading();
    
    // Global AJAX error handler
    $(document).ajaxError(function(event, jqXHR, settings, error) {
        if (jqXHR.status === 401) {
            window.showNotification('Session expired. Redirecting to login...', 'warning', 3000);
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else if (jqXHR.status === 403) {
            window.showNotification('Access denied. Insufficient permissions.', 'error');
        } else if (jqXHR.status >= 500) {
            window.showNotification('Server error. Please try again later.', 'error');
        }
        
        console.error('AJAX Error:', {
            url: settings.url,
            status: jqXHR.status,
            error: error
        });
    });
    
    // Global AJAX complete handler to hide any lingering loading states
    $(document).ajaxComplete(function() {
        $('.btn:disabled').each(function() {
            const $btn = $(this);
            const originalHtml = $btn.data('original-html');
            if (originalHtml) {
                window.hideLoading($btn);
            }
        });
    });
});

console.log('✅ main.js loaded — Grand Hotel Luxury Management System');