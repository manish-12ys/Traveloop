// Traveloop App Utilities

// API Configuration
const API_BASE_URL = window.location.origin + '/api';

// API Helper Functions
const API = {
    _getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    },

    async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    },

    async post(endpoint, data) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this._getCsrfToken()
                },
                body: JSON.stringify(data),
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            throw error;
        }
    },

    async put(endpoint, data) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this._getCsrfToken()
                },
                body: JSON.stringify(data),
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('API PUT Error:', error);
            throw error;
        }
    },

    async delete(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this._getCsrfToken()
                },
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('API DELETE Error:', error);
            throw error;
        }
    }
};

// Notification Helper
const Notify = {
    success(message) {
        this._show(message, 'success');
    },
    
    error(message) {
        this._show(message, 'error');
    },
    
    info(message) {
        this._show(message, 'info');
    },
    
    _show(message, type) {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 animate-slideIn ${
            type === 'success' ? 'bg-green-100 border-green-400 text-green-700' :
            type === 'error' ? 'bg-red-100 border-red-400 text-red-700' :
            'bg-blue-100 border-blue-400 text-blue-700'
        } border px-4 py-3 rounded-lg flex items-center gap-2`;
        
        const icon = type === 'success' ? 'check-circle' :
                    type === 'error' ? 'exclamation-circle' :
                    'info-circle';
        
        notification.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()" class="ml-2 opacity-70 hover:opacity-100">×</button>
        `;
        
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }
};

// Loading State Helper
const Loading = {
    show(message = 'Loading...') {
        const loader = document.createElement('div');
        loader.id = 'app-loader';
        loader.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        loader.innerHTML = `
            <div class="bg-white dark:bg-gray-900 rounded-lg p-8 text-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-violet-600 mx-auto mb-4"></div>
                <p class="text-gray-700 dark:text-gray-300">${message}</p>
            </div>
        `;
        document.body.appendChild(loader);
    },
    
    hide() {
        const loader = document.getElementById('app-loader');
        if (loader) loader.remove();
    }
};

// Form Validation
const FormValidator = {
    email(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },
    
    password(password) {
        return password.length >= 8;
    },
    
    username(username) {
        return /^[a-zA-Z0-9_-]{3,20}$/.test(username);
    },
    
    required(value) {
        return value && value.trim().length > 0;
    }
};

// Storage Helper
const Storage = {
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Storage error:', error);
        }
    },
    
    get(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error('Storage error:', error);
            return null;
        }
    },
    
    remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Storage error:', error);
        }
    },
    
    clear() {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('Storage error:', error);
        }
    }
};

// Date Helper
const DateHelper = {
    /**
     * Parse date parts safely from an ISO string (YYYY-MM-DD or full ISO).
     * Uses string splitting to avoid UTC→local timezone shift bugs.
     */
    _parse(date) {
        if (!date) return null;
        const str = String(date);
        // If it's a date-only string like "2026-05-10", split directly — no Date object
        if (/^\d{4}-\d{2}-\d{2}$/.test(str)) {
            const [year, month, day] = str.split('-');
            return { day, month, year };
        }
        // For full datetime strings, use Date but extract UTC parts to stay consistent
        const d = new Date(str);
        if (isNaN(d)) return null;
        return {
            day: String(d.getUTCDate()).padStart(2, '0'),
            month: String(d.getUTCMonth() + 1).padStart(2, '0'),
            year: d.getUTCFullYear()
        };
    },

    format(date) {
        const p = this._parse(date);
        if (!p) return 'Invalid date';
        return `${p.day}/${p.month}/${p.year}`;
    },

    formatDateTime(date) {
        if (!date) return '';
        const d = new Date(date);
        if (isNaN(d)) return '';
        const day = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const year = d.getFullYear();
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        return `${day}/${month}/${year} ${hours}:${minutes}`;
    },

    getRelativeTime(date) {
        const now = new Date();
        const past = new Date(date);
        const diff = Math.floor((now - past) / 1000); // seconds
        
        if (diff < 60) return 'just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
        
        return this.format(date);
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Traveloop App Initialized');
    
    // Remove loading indicator if present
    Loading.hide();

    // Auto-hide flash messages after a short delay.
    const flashMessages = document.querySelectorAll('.animate-slideIn');
    flashMessages.forEach((item) => {
        window.setTimeout(() => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(-6px)';
            item.style.transition = 'all 0.2s ease';
            window.setTimeout(() => item.remove(), 220);
        }, 4200);
    });

    // Add a simple loading state for forms marked with data-loading-form.
    const loadingForms = document.querySelectorAll('form[data-loading-form]');
    loadingForms.forEach((form) => {
        form.addEventListener('submit', () => {
            const button = form.querySelector('[data-loading-button]');
            if (!button) {
                return;
            }

            const textEl = button.querySelector('span');
            button.disabled = true;
            button.classList.add('opacity-80', 'cursor-not-allowed');

            if (textEl) {
                textEl.textContent = 'Please wait...';
            }
        });
    });
});

// Global error handler - only fires for uncaught synchronous errors
window.addEventListener('error', (event) => {
    // Only show toast for errors NOT from fetch/async operations (those have their own handling)
    if (event.error && !(event.error instanceof TypeError && event.error.message.includes('fetch'))) {
        console.error('Global error:', event.error);
    }
});

// Network error handler
window.addEventListener('online', () => {
    Notify.success('Back online!');
});

window.addEventListener('offline', () => {
    Notify.error('You are offline. Some features may not work.');
});
