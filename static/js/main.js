// Show/hide loading overlay
function showLoading() {
    document.getElementById('loading-overlay').classList.remove('d-none');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.add('d-none');
}

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // Fetch all forms that need validation
    const forms = document.querySelectorAll('.needs-validation');

    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Add loading state to submit buttons
    const submitButtons = document.querySelectorAll('button[type="submit"][data-loading-text]');
    submitButtons.forEach(button => {
        const form = button.closest('form');
        if (form) {
            form.addEventListener('submit', () => {
                if (form.checkValidity()) {
                    const spinner = button.querySelector('.spinner-border');
                    const buttonText = button.querySelector('.button-text');
                    if (spinner && buttonText) {
                        button.disabled = true;
                        spinner.classList.remove('d-none');
                        buttonText.textContent = button.dataset.loadingText;
                    }
                }
            });
        }
    });

    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
});
