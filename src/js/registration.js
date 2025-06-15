// Store form data in sessionStorage
function saveFormData(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        // Skip empty values for registration3-form
        if (formId === 'registration3-form' && !value) {
            continue;
        }
        
        if (key.endsWith('[]')) {
            // Handle array inputs
            const baseKey = key.slice(0, -2);
            if (!data[baseKey]) {
                data[baseKey] = [];
            }
            data[baseKey].push(value);
        } else {
            data[key] = value;
        }
    }
    
    sessionStorage.setItem(formId, JSON.stringify(data));
}

// Load form data from sessionStorage
function loadFormData(formId) {
    const savedData = sessionStorage.getItem(formId);
    if (savedData) {
        const data = JSON.parse(savedData);
        const form = document.getElementById(formId);
        
        for (let key in data) {
            const elements = form.elements[key];
            if (Array.isArray(data[key])) {
                // Handle array inputs
                data[key].forEach((value, index) => {
                    if (elements[index]) {
                        elements[index].value = value;
                    }
                });
            } else if (elements) {
                elements.value = data[key];
            }
        }
    }
}

// Handle form submission and navigation
function handleFormSubmit(event, nextPage) {
    event.preventDefault();
    const form = event.target;
    
    // For registration3-form, allow submission even if empty
    if (form.id === 'registration3-form') {
        saveFormData(form.id);
        window.location.href = 'registrationPrint.html';
        return;
    }
    
    // For registrationPrint-form, proceed to success page
    if (form.id === 'registrationPrint-form') {
        if (document.getElementById('termsCheck').checked) {
            window.location.href = 'registrationSuccess.html';
            return;
        } else {
            alert('Please accept the terms and conditions to proceed.');
            return;
        }
    }
    
    // For other forms, proceed with normal validation
    saveFormData(form.id);
    window.location.href = nextPage;
}

// Handle back button navigation
function handleBack() {
    const currentPage = window.location.pathname.split('/').pop();
    const backPages = {
        'registration2.html': 'registration1.html',
        'registration3.html': 'registration2.html',
        'registrationPrint.html': 'registration3.html'
    };
    
    if (backPages[currentPage]) {
        window.location.href = backPages[currentPage];
    }
}

// Handle cancel button
function handleCancel() {
    if (confirm('Are you sure you want to cancel? All entered data will be lost.')) {
        sessionStorage.clear();
        window.location.href = 'landing.html';
    }
}

// Initialize forms
document.addEventListener('DOMContentLoaded', function() {
    // Set up form IDs and navigation
    const forms = {
        'registration1-form': 'registration2.html',
        'registration2-form': 'registration3.html',
        'registration3-form': 'registrationPrint.html',
        'registrationPrint-form': 'registrationSuccess.html'
    };

    // Initialize each form
    for (let formId in forms) {
        const form = document.getElementById(formId);
        if (form) {
            // Load saved data
            loadFormData(formId);
            
            // Set up form submission
            form.addEventListener('submit', function(event) {
                handleFormSubmit(event, forms[formId]);
            });
            
            // Set up cancel button
            const cancelBtn = form.querySelector('.cancel-btn');
            if (cancelBtn) {
                cancelBtn.addEventListener('click', handleCancel);
            }

            // Set up back button
            const backBtn = form.querySelector('.back-btn');
            if (backBtn) {
                backBtn.addEventListener('click', handleBack);
            }
        }
    }
}); 