// Utility Functions
const utils = {
    // Form validation
    validateForm: (formData) => {
        const errors = {};
        for (const [key, value] of formData.entries()) {
            if (!value.trim()) {
                errors[key] = `${key.charAt(0).toUpperCase() + key.slice(1)} is required`;
            }
        }
        return errors;
    },

    // Show notification
    showNotification: (message, type = 'success') => {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    },

    // Format date
    formatDate: (date) => {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    // Debounce function
    debounce: (func, wait) => {
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
};

// API Service
const api = {
    // Base URL for API endpoints
    baseUrl: '/api',

    // Generic fetch function
    async fetch(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // Auth endpoints
    auth: {
        login: async (credentials) => {
            return await api.fetch('/auth/login', {
                method: 'POST',
                body: JSON.stringify(credentials)
            });
        },
        register: async (userData) => {
            return await api.fetch('/auth/register', {
                method: 'POST',
                body: JSON.stringify(userData)
            });
        },
        logout: async () => {
            return await api.fetch('/auth/logout', {
                method: 'POST'
            });
        }
    },

    // Customer endpoints
    customers: {
        getAll: async (params = {}) => {
            const queryString = new URLSearchParams(params).toString();
            return await api.fetch(`/customers?${queryString}`);
        },
        getById: async (id) => {
            return await api.fetch(`/customers/${id}`);
        },
        create: async (data) => {
            return await api.fetch('/customers', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },
        update: async (id, data) => {
            return await api.fetch(`/customers/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },
        delete: async (id) => {
            return await api.fetch(`/customers/${id}`, {
                method: 'DELETE'
            });
        }
    }
};

// UI Components
const components = {
    // Loading spinner
    createSpinner: () => {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.innerHTML = `
            <div class="spinner-inner">
                <div class="spinner-circle"></div>
            </div>
        `;
        return spinner;
    },

    // Modal dialog
    createModal: (title, content) => {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        return modal;
    },

    // Form builder
    createForm: (fields, onSubmit) => {
        const form = document.createElement('form');
        form.className = 'dynamic-form';
        
        fields.forEach(field => {
            const div = document.createElement('div');
            div.className = 'form-group';
            
            const label = document.createElement('label');
            label.textContent = field.label;
            label.htmlFor = field.id;
            
            const input = document.createElement('input');
            input.type = field.type || 'text';
            input.id = field.id;
            input.name = field.id;
            input.required = field.required || false;
            
            if (field.placeholder) {
                input.placeholder = field.placeholder;
            }
            
            div.appendChild(label);
            div.appendChild(input);
            form.appendChild(div);
        });
        
        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.textContent = 'Submit';
        form.appendChild(submitButton);
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            await onSubmit(data);
        });
        
        return form;
    }
};


// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme
    theme.init();
    
});

// Export modules
window.app = {
    utils,
    api,
    components,
}; 