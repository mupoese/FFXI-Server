// Main JavaScript functionality for FFXI Server website

// Global configuration
const APP_CONFIG = {
    apiBase: '/api',
    refreshInterval: 30000,
    itemsPerPage: 20,
    debounceDelay: 300
};

// Utility functions
class Utils {
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    static formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    static formatGil(gil) {
        return this.formatNumber(gil) + ' gil';
    }

    static formatTime(timestamp) {
        if (!timestamp) return 'Unknown';
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffDays > 0) {
            return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        } else if (diffHours > 0) {
            return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        } else {
            return 'Recently';
        }
    }

    static showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: var(--accent-color);
            color: white;
            border-radius: 8px;
            z-index: 1000;
            animation: slideInRight 0.3s ease;
            max-width: 400px;
            box-shadow: var(--shadow);
        `;

        if (type === 'error') {
            notification.style.background = 'var(--danger-color)';
        } else if (type === 'warning') {
            notification.style.background = 'var(--warning-color)';
        } else if (type === 'info') {
            notification.style.background = 'var(--info-color)';
        }
        
        document.body.appendChild(notification);
        
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }
    }

    static async apiRequest(endpoint, options = {}) {
        const url = `${APP_CONFIG.apiBase}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }
}

// Search functionality
class SearchManager {
    constructor() {
        this.searchHistory = this.loadSearchHistory();
        this.setupSearchShortcuts();
    }

    loadSearchHistory() {
        try {
            return JSON.parse(localStorage.getItem('ffxi_search_history') || '[]');
        } catch {
            return [];
        }
    }

    saveSearchHistory() {
        try {
            localStorage.setItem('ffxi_search_history', JSON.stringify(this.searchHistory));
        } catch (error) {
            console.warn('Failed to save search history:', error);
        }
    }

    addToHistory(query, type = 'general') {
        if (!query || query.length < 2) return;
        
        const entry = {
            query: query.trim(),
            type,
            timestamp: Date.now()
        };

        // Remove existing entry if it exists
        this.searchHistory = this.searchHistory.filter(item => 
            !(item.query === entry.query && item.type === entry.type)
        );

        // Add to beginning and limit to 10 entries
        this.searchHistory.unshift(entry);
        this.searchHistory = this.searchHistory.slice(0, 10);
        
        this.saveSearchHistory();
    }

    getHistory(type = null) {
        if (type) {
            return this.searchHistory.filter(item => item.type === type);
        }
        return this.searchHistory;
    }

    setupSearchShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('.search-input');
                if (searchInput) {
                    searchInput.focus();
                }
            }
        });
    }
}

// Real-time data manager
class DataManager {
    constructor() {
        this.cache = new Map();
        this.cacheTimeout = 60000; // 1 minute
        this.updateInterval = null;
    }

    async getCachedData(key, fetchFunction, forceRefresh = false) {
        const cached = this.cache.get(key);
        const now = Date.now();

        if (!forceRefresh && cached && (now - cached.timestamp) < this.cacheTimeout) {
            return cached.data;
        }

        try {
            const data = await fetchFunction();
            this.cache.set(key, {
                data,
                timestamp: now
            });
            return data;
        } catch (error) {
            // Return cached data if fetch fails and we have it
            if (cached) {
                console.warn(`Failed to fetch ${key}, using cached data:`, error);
                return cached.data;
            }
            throw error;
        }
    }

    clearCache() {
        this.cache.clear();
    }

    startAutoRefresh(callback, interval = APP_CONFIG.refreshInterval) {
        this.stopAutoRefresh();
        this.updateInterval = setInterval(callback, interval);
    }

    stopAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
}

// Loading manager
class LoadingManager {
    static show(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Loading...</p>
                </div>
            `;
        }
    }

    static hide(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            const loading = element.querySelector('.loading');
            if (loading) {
                loading.remove();
            }
        }
    }

    static showInline(container) {
        const spinner = document.createElement('div');
        spinner.className = 'inline-spinner';
        spinner.innerHTML = '<div class="spinner"></div>';
        container.appendChild(spinner);
        return spinner;
    }
}

// Modal manager
class ModalManager {
    static create(title, content, options = {}) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-container">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" onclick="ModalManager.close(this)">&times;</button>
                </div>
                <div class="modal-content">
                    ${content}
                </div>
                ${options.showFooter !== false ? `
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="ModalManager.close(this)">Close</button>
                        ${options.primaryButton ? `<button class="btn btn-primary" onclick="${options.primaryAction}">${options.primaryButton}</button>` : ''}
                    </div>
                ` : ''}
            </div>
        `;

        // Add styles if not already present
        if (!document.querySelector('#modal-styles')) {
            const styles = document.createElement('style');
            styles.id = 'modal-styles';
            styles.textContent = `
                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0,0,0,0.8);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                    animation: fadeIn 0.3s ease;
                }
                .modal-container {
                    background: var(--bg-medium);
                    border-radius: 12px;
                    border: 1px solid var(--border-color);
                    max-width: 600px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                    animation: slideInUp 0.3s ease;
                }
                .modal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1.5rem;
                    border-bottom: 1px solid var(--border-color);
                }
                .modal-header h3 {
                    color: var(--primary-color);
                    margin: 0;
                }
                .modal-close {
                    background: none;
                    border: none;
                    font-size: 1.5rem;
                    color: var(--text-muted);
                    cursor: pointer;
                    padding: 0;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .modal-close:hover {
                    color: var(--text-light);
                }
                .modal-content {
                    padding: 1.5rem;
                    color: var(--text-light);
                }
                .modal-footer {
                    padding: 1.5rem;
                    border-top: 1px solid var(--border-color);
                    display: flex;
                    justify-content: flex-end;
                    gap: 1rem;
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes slideInUp {
                    from { transform: translateY(50px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }

        document.body.appendChild(modal);

        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                ModalManager.close(modal);
            }
        });

        // Close on escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                ModalManager.close(modal);
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);

        return modal;
    }

    static close(element) {
        const modal = element.closest ? element.closest('.modal-overlay') : element;
        if (modal && modal.parentElement) {
            modal.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                if (modal.parentElement) {
                    modal.remove();
                }
            }, 300);
        }
    }
}

// Form validation
class FormValidator {
    static validateRequired(value, fieldName) {
        if (!value || value.trim() === '') {
            throw new Error(`${fieldName} is required`);
        }
        return true;
    }

    static validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            throw new Error('Invalid email format');
        }
        return true;
    }

    static validateLength(value, min, max, fieldName) {
        if (value.length < min) {
            throw new Error(`${fieldName} must be at least ${min} characters`);
        }
        if (max && value.length > max) {
            throw new Error(`${fieldName} must be no more than ${max} characters`);
        }
        return true;
    }

    static validateForm(formElement, rules) {
        const errors = [];
        const formData = new FormData(formElement);

        for (const [fieldName, validators] of Object.entries(rules)) {
            const value = formData.get(fieldName);
            
            for (const validator of validators) {
                try {
                    validator(value, fieldName);
                } catch (error) {
                    errors.push(error.message);
                    break; // Stop at first error for this field
                }
            }
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }
}

// Global instances
const utils = new Utils();
const searchManager = new SearchManager();
const dataManager = new DataManager();

// Global functions for backwards compatibility
window.Utils = Utils;
window.SearchManager = SearchManager;
window.DataManager = DataManager;
window.LoadingManager = LoadingManager;
window.ModalManager = ModalManager;
window.FormValidator = FormValidator;

// Export instances
window.utils = utils;
window.searchManager = searchManager;
window.dataManager = dataManager;

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('FFXI Server website initialized');
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading states to all buttons
    document.querySelectorAll('.btn').forEach(button => {
        const originalText = button.innerHTML;
        
        button.addEventListener('click', function() {
            if (this.classList.contains('loading')) return;
            
            // Add loading state for async operations
            if (this.getAttribute('data-async') === 'true') {
                this.classList.add('loading');
                this.innerHTML = '<div class="spinner"></div> Loading...';
                
                // Remove loading state after 3 seconds (fallback)
                setTimeout(() => {
                    this.classList.remove('loading');
                    this.innerHTML = originalText;
                }, 3000);
            }
        });
    });

    // Add form validation highlighting
    document.querySelectorAll('input, select, textarea').forEach(field => {
        field.addEventListener('invalid', function() {
            this.style.borderColor = 'var(--danger-color)';
        });
        
        field.addEventListener('input', function() {
            if (this.checkValidity()) {
                this.style.borderColor = 'var(--border-color)';
            }
        });
    });
});

// Page visibility API for pausing updates when tab is hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        dataManager.stopAutoRefresh();
    } else {
        // Resume auto-refresh when page becomes visible
        if (window.currentPage && window.currentPage.resumeUpdates) {
            window.currentPage.resumeUpdates();
        }
    }
});

// Error handling for unhandled promises
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    Utils.showNotification('An unexpected error occurred. Please try again.', 'error');
});

// Network status monitoring
window.addEventListener('online', () => {
    Utils.showNotification('Connection restored', 'success', 2000);
});

window.addEventListener('offline', () => {
    Utils.showNotification('Connection lost. Some features may not work.', 'warning', 5000);
});

// Export for use in other modules
export { Utils, SearchManager, DataManager, LoadingManager, ModalManager, FormValidator };