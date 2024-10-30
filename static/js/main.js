// Add any client-side interactivity if needed
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Handle image previews
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const previewId = this.dataset.preview;
            if (previewId) {
                const preview = document.getElementById(previewId);
                preview.innerHTML = '';
                
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.innerHTML = `<img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px;">`;
                    }
                    reader.readAsDataURL(this.files[0]);
                }
            }
        });
    });

    // Handle form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
            
            // Disable submit button to prevent double submission
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                if (submitBtn.dataset.loadingText) {
                    submitBtn.dataset.originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = submitBtn.dataset.loadingText;
                }
            }
        });
    });

    // Handle dynamic content loading
    const dynamicContainers = document.querySelectorAll('[data-dynamic-content]');
    dynamicContainers.forEach(container => {
        const url = container.dataset.dynamicContent;
        if (url) {
            fetch(url)
                .then(response => response.text())
                .then(html => {
                    container.innerHTML = html;
                })
                .catch(error => {
                    console.error('Error loading dynamic content:', error);
                    container.innerHTML = '<div class="alert alert-danger">Error loading content</div>';
                });
        }
    });
});

// Utility function to show loading state
function showLoading(button, message = 'Loading...') {
    if (button) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${message}`;
    }
}

// Utility function to hide loading state
function hideLoading(button) {
    if (button && button.dataset.originalText) {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText;
    }
}
