// Ticket booking JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Check for pending booking on page load
    checkForPendingBooking();
    
    // Initialize ticket counters
    initTicketCounters();
    
    // Initialize form validation
    initFormValidation();
    
    // Initialize availability checking
    initAvailabilityChecking();
});

function initTicketCounters() {
    const plusButtons = document.querySelectorAll('.btn-counter.plus');
    const minusButtons = document.querySelectorAll('.btn-counter.minus');
    const adultInput = document.getElementById('adult_tickets');
    const studentInput = document.getElementById('student_tickets');
    const totalDisplay = document.getElementById('total-amount');
    const nextBtn = document.getElementById('next-btn');
    
    if (!adultInput || !studentInput) return;
    
    // Adult ticket price (from settings, fallback to 200)
    const adultPrice = window.bookingPrices ? window.bookingPrices.adult : 200;
    const studentPrice = window.bookingPrices ? window.bookingPrices.student : 100;
    
    function updateTotal() {
        const adultTickets = parseInt(adultInput.value) || 0;
        const studentTickets = parseInt(studentInput.value) || 0;
        const total = (adultTickets * adultPrice) + (studentTickets * studentPrice);
        
        if (totalDisplay) {
            totalDisplay.textContent = total;
        }
        
        // Enable/disable next button
        if (nextBtn) {
            nextBtn.disabled = total === 0;
        }
        
        // Update max values based on total tickets
        const totalTickets = adultTickets + studentTickets;
        const maxTickets = 4;
        
        if (totalTickets >= maxTickets) {
            plusButtons.forEach(btn => btn.disabled = true);
        } else {
            plusButtons.forEach(btn => btn.disabled = false);
        }
        
        // Disable minus buttons when at 0
        minusButtons.forEach(btn => {
            const type = btn.dataset.type;
            const input = type === 'adult' ? adultInput : studentInput;
            btn.disabled = parseInt(input.value) <= 0;
        });
    }
    
    // Add event listeners
    plusButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.dataset.type;
            const input = type === 'adult' ? adultInput : studentInput;
            const currentValue = parseInt(input.value) || 0;
            const totalTickets = (parseInt(adultInput.value) || 0) + (parseInt(studentInput.value) || 0);
            
            if (totalTickets < 4) {
                input.value = currentValue + 1;
                updateTotal();
            }
        });
    });
    
    minusButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.dataset.type;
            const input = type === 'adult' ? adultInput : studentInput;
            const currentValue = parseInt(input.value) || 0;
            
            if (currentValue > 0) {
                input.value = currentValue - 1;
                updateTotal();
            }
        });
    });
    
    // Initial update
    updateTotal();
}

function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Basic validation
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#dc2626';
                } else {
                    field.style.borderColor = '#e5e7eb';
                }
            });
            
            // Email validation
            const emailField = form.querySelector('input[type="email"]');
            if (emailField && emailField.value) {
                const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
                if (!emailPattern.test(emailField.value)) {
                    isValid = false;
                    emailField.style.borderColor = '#dc2626';
                    showError('Ange en giltig e-postadress.');
                }
            }
            
            // Phone validation (Swedish format)
            const phoneField = form.querySelector('input[type="tel"]');
            if (phoneField && phoneField.value) {
                const phonePattern = /^(\+46|0)[0-9\s-]{8,12}$/;
                if (!phonePattern.test(phoneField.value.replace(/\s/g, ''))) {
                    isValid = false;
                    phoneField.style.borderColor = '#dc2626';
                    showError('Ange ett giltigt telefonnummer.');
                }
            }
            
            // GDPR checkbox validation
            const gdprCheckbox = form.querySelector('input[name="gdpr_consent"]');
            if (gdprCheckbox && !gdprCheckbox.checked) {
                isValid = false;
                showError('Du måste godkänna att informationen sparas.');
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

function initAvailabilityChecking() {
    // Check availability when time selection changes
    const timeInputs = document.querySelectorAll('input[name="show_id"]');
    
    timeInputs.forEach(input => {
        input.addEventListener('change', function() {
            const showId = this.value;
            checkAvailability(showId);
        });
    });
}

function checkAvailability(showId) {
    fetch(`/api/check-availability?show_id=${showId}`)
        .then(response => response.json())
        .then(data => {
            const timeOption = document.querySelector(`input[value="${showId}"]`).closest('.time-option');
            const availabilitySpan = timeOption.querySelector('.availability');
            
            if (data.sold_out) {
                availabilitySpan.innerHTML = '<span class="sold-out">Slutsåld</span>';
                timeOption.querySelector('input').disabled = true;
                timeOption.querySelector('.time-label').style.opacity = '0.5';
            } else {
                availabilitySpan.innerHTML = `<span class="available">${data.available} biljetter kvar</span>`;
                timeOption.querySelector('input').disabled = false;
                timeOption.querySelector('.time-label').style.opacity = '1';
            }
        })
        .catch(error => {
            console.error('Error checking availability:', error);
        });
}

function showError(message) {
    // Remove existing error messages
    const existingErrors = document.querySelectorAll('.error-message');
    existingErrors.forEach(error => error.remove());
    
    // Create new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'flash flash-error error-message';
    errorDiv.textContent = message;
    
    // Insert at the top of the main content
    const main = document.querySelector('.main');
    if (main) {
        main.insertBefore(errorDiv, main.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
}

// Back button functionality
function goBack() {
    // Clear current step data from session
    if (window.location.pathname.includes('/booking/contact')) {
        // Clear ticket selection
        sessionStorage.removeItem('adult_tickets');
        sessionStorage.removeItem('student_tickets');
    } else if (window.location.pathname.includes('/booking/tickets')) {
        // Clear time selection
        sessionStorage.removeItem('show_id');
    }
    
    window.history.back();
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('sv-SE', {
        style: 'currency',
        currency: 'SEK'
    }).format(amount);
}

function formatPhoneNumber(phone) {
    // Format Swedish phone numbers
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.startsWith('46')) {
        return '+' + cleaned;
    } else if (cleaned.startsWith('0')) {
        return cleaned;
    }
    return phone;
}

// Mobile-specific enhancements
if (window.innerWidth <= 768) {
    // Increase touch targets for mobile
    document.querySelectorAll('.btn-counter').forEach(btn => {
        btn.style.minWidth = '44px';
        btn.style.minHeight = '44px';
    });
    
    // Prevent zoom on input focus (iOS)
    document.querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('focus', function() {
            if (window.innerWidth <= 768) {
                const viewport = document.querySelector('meta[name="viewport"]');
                if (viewport) {
                    viewport.content = 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no';
                }
            }
        });
        
        input.addEventListener('blur', function() {
            const viewport = document.querySelector('meta[name="viewport"]');
            if (viewport) {
                viewport.content = 'width=device-width, initial-scale=1';
            }
        });
    });
}

// Session recovery functionality
function checkForPendingBooking() {
    const pendingBookingRef = localStorage.getItem('pendingBookingRef');
    const pendingBookingEmail = localStorage.getItem('pendingBookingEmail');
    
    if (pendingBookingRef && pendingBookingEmail && !window.location.pathname.includes('/booking/success/')) {
        // Show a notification about pending booking
        const notification = document.createElement('div');
        notification.className = 'pending-booking-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ffc107;
            color: #000;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
            max-width: 300px;
        `;
        
        notification.innerHTML = `
            <h4>Pågående bokning</h4>
            <p>Du har en pågående bokning som väntar på betalning.</p>
            <div style="margin-top: 10px;">
                <button onclick="resumeBooking('${pendingBookingRef}', '${pendingBookingEmail}')" 
                        style="background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; margin-right: 10px;">
                    Fortsätt betalning
                </button>
                <button onclick="dismissNotification(this)" 
                        style="background: #6c757d; color: white; border: none; padding: 8px 16px; border-radius: 4px;">
                    Stäng
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-dismiss after 30 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 30000);
    }
}

function resumeBooking(bookingRef, email) {
    // Redirect to booking success page with new URL format
    window.location.href = `/booking/success/${bookingRef}/${email}`;
}

function dismissNotification(button) {
    button.closest('.pending-booking-notification').remove();
}

// Clear pending booking when payment is confirmed
function clearPendingBooking() {
    localStorage.removeItem('pendingBookingRef');
    localStorage.removeItem('pendingBookingEmail');
}
