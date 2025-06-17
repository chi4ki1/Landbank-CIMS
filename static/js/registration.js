// --- registration.js (fully updated with validation, debug, and navigation) ---

function saveFormData(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const data = {};

    for (let [key, value] of formData.entries()) {
        // Only include non-empty values for registration3-form to avoid sending empty fields
        // if (formId === 'registration3-form' && !value) continue; // Removed this for now, backend expects all fields

        // Handle multiple selections for array fields (e.g., checkboxes, multi-selects)
        if (key.endsWith('[]')) {
            const baseKey = key.slice(0, -2);
            if (!data[baseKey]) data[baseKey] = [];
            data[baseKey].push(value);
        } else {
            // Check for radio buttons, only save the checked one
            const element = form.elements[key];
            if (element && element.type === 'radio') {
                if (element.checked) {
                    data[key] = value;
                }
            } else if (element && element.type === 'checkbox') {
                 // For single checkboxes, if not checked, FormData doesn't include it.
                 // So we explicitly set it to false if it's a checkbox and not in data.
                 if (!data.hasOwnProperty(key)) { // Only if not already added by formData.entries for checked state
                     data[key] = false; // Default to false if unchecked
                 }
                 data[key] = value; // This will overwrite if it was checked
            } else {
                data[key] = value;
            }
        }
    }
    sessionStorage.setItem(formId, JSON.stringify(data));
    console.log(`Saved ${formId}:`, data); // DEBUG LOG
}

function loadFormData(formId) {
    const savedData = sessionStorage.getItem(formId);
    if (savedData) {
        const data = JSON.parse(savedData);
        const form = document.getElementById(formId);

        for (let key in data) {
            const elements = form.elements[key];
            if (!elements) continue; // Skip if element not found

            if (Array.isArray(data[key])) {
                // Handle multiple elements with the same name (e.g., checkboxes, dynamic inputs)
                data[key].forEach((value, index) => {
                    if (elements[index]) {
                        if (elements[index].type === 'checkbox') {
                            elements[index].checked = true; // Check if value exists (simple check for now)
                        } else {
                            elements[index].value = value;
                        }
                    } else {
                        // This might indicate dynamically added fields that don't exist yet on load
                        console.warn(`Element with index ${index} for key ${key} not found on load.`);
                    }
                });
            } else if (elements.length > 0 && (elements[0].type === 'radio' || elements[0].type === 'checkbox')) {
                // Handle radio buttons and grouped checkboxes
                for (let i = 0; i < elements.length; i++) {
                    if (elements[i].value === data[key]) {
                        elements[i].checked = true;
                    }
                }
            } else if (elements.type === 'checkbox') {
                elements.checked = data[key]; // For a single checkbox
            } else {
                elements.value = data[key];
            }
        }
    }
    console.log(`Loaded ${formId}:`, JSON.parse(sessionStorage.getItem(formId) || '{}')); // DEBUG LOG
}

function handleFormSubmit(event, nextPage) {
    event.preventDefault(); // Prevent default form submission
    const form = event.target;

    console.log("Form submission triggered:", form.id); // DEBUG LOG

    // Save data for the current form step
    saveFormData(form.id);

    // Specific logic for the final submission from registrationPrint
    if (form.id === 'registrationPrint-form') {
        console.log("Handling registrationPrint-form submission for final API call");

        const r1 = JSON.parse(sessionStorage.getItem('registration1-form') || '{}');
        const r2 = JSON.parse(sessionStorage.getItem('registration2-form') || '{}');
        const r3 = JSON.parse(sessionStorage.getItem('registration3-form') || '{}');

        const errors = [];

        // Basic validation for required fields
        if (!r1.firstName || !r1.lastName || !r1.dob || !r1.nationality || !r1.address || !r1.email) {
            errors.push("Personal Information (Step 1) is incomplete. Please ensure all required fields are filled.");
        }

        if (!r2.occupation || !r2.natureOfBusiness || !r2.monthlyIncome || !r2.annualIncome) {
            errors.push("Employment and Financial Information (Step 2) is incomplete. Please ensure all required fields are filled.");
        }

        // Check if at least one bank account is added
        // Note: r3.bank might be a single string if only one item, or an array if multiple
        const bankAccountsAdded = (r3.bank && (Array.isArray(r3.bank) ? r3.bank.some(b => b.trim() !== '') : r3.bank.trim() !== ''));
        if (!bankAccountsAdded) {
            errors.push("Additional Information (Step 3): Please add at least one bank account.");
        }
        
        if (errors.length > 0) {
            alert(errors.join('\n\n'));
            return;
        }

        // Terms and conditions check
        const termsCheck = document.getElementById('termsCheck');
        if (termsCheck && !termsCheck.checked) {
            alert('Please accept the terms and conditions to proceed.');
            return;
        }

        // Consolidate all data for sending
        const data = {
            registration1: r1,
            registration2: r2,
            registration3: r3
        };

        console.log("Sending data to backend:", data); // DEBUG LOG

        // Send data to Flask backend
        fetch('/submitRegistration', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (response.ok) {
                console.log("Submission successful");
                sessionStorage.clear(); // Clear all saved data on successful submission
                window.location.href = 'registrationSuccess';
            } else {
                // If response is not OK, try to read error message from backend
                response.text().then(errorMessage => {
                    alert(`Submission failed: ${errorMessage || response.statusText}. Please try again.`);
                    console.error("Submission error response:", response.status, errorMessage);
                }).catch(() => {
                    alert(`Submission failed with status: ${response.status}. Please try again.`);
                    console.error("Submission error: Could not parse error message.");
                });
            }
        })
        .catch(err => {
            console.error("Submission network error:", err);
            alert("Submission failed due to network or server error. Please check your connection and try again.");
        });

        return; // Exit function after handling final submission
    }

    // For intermediate steps, just navigate to the next page
    window.location.href = nextPage;
}

function handleBack() {
    const currentPage = window.location.pathname.split('/').pop();
    const backPages = {
        'registration2.html': 'registration1', // Specific HTML files for clarity
        'registration3.html': 'registration2',
        'registrationPrint.html': 'registration3'
    };

    // If currentPage is just "registration2" etc., add .html for lookup
    const lookupPage = currentPage.endsWith('.html') ? currentPage : currentPage + '.html';

    if (backPages[lookupPage]) {
        window.location.href = backPages[lookupPage];
    } else if (currentPage === 'registration1.html' || currentPage === 'register.html') {
        // If on the first registration step, go back to the landing page
        window.location.href = '/';
    }
}

function handleCancel() {
    // Replaced alert with custom modal logic if needed, but for now, using confirm for simplicity as per user's original code
    if (confirm('Are you sure you want to cancel? All entered data will be lost.')) {
        sessionStorage.clear(); // Clear all stored data
        window.location.href = '/'; // Redirect to landing page
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const forms = {
        'registration1-form': 'registration2',
        'registration2-form': 'registration3',
        'registration3-form': 'registrationPrint',
        'registrationPrint-form': 'registrationSuccess' // This won't be directly navigated, but used for logic
    };

    for (let formId in forms) {
        const form = document.getElementById(formId);
        if (form) {
            console.log(`Initializing form event listeners for: ${formId}`);

            // Load data when the form page loads
            loadFormData(formId);

            // Add submit listener for the form
            form.addEventListener('submit', function(event) {
                handleFormSubmit(event, forms[formId]);
            });

            // Add event listeners for back and cancel buttons if they exist
            const cancelBtn = form.querySelector('.cancel-btn');
            if (cancelBtn) {
                cancelBtn.addEventListener('click', handleCancel);
            }

            const backBtn = form.querySelector('.back-btn');
            if (backBtn) {
                backBtn.addEventListener('click', handleBack);
            }
        }
    }
});
