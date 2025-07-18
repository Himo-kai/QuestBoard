/**
 * QuestBoard - Main JavaScript File
 * Version: 1.0.0
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initTooltips();
    initPopovers();
    initFormValidation();
    initPasswordToggle();
    initFilePreview();
    initTagsInput();
    initModals();
    initBackToTop();
    initThemeSwitcher();
    setupAjaxCsrf();
    initComponents();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltips = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltips.map(el => new bootstrap.Tooltip(el));
}

/**
 * Initialize Bootstrap popovers
 */
function initPopovers() {
    const popovers = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popovers.map(el => new bootstrap.Popover(el));
}

/**
 * Initialize form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Toggle password visibility
 */
function initPasswordToggle() {
    document.querySelectorAll('.password-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('fa-eye-slash', 'fa-eye');
            }
        });
    });
}

/**
 * Initialize file input preview
 */
function initFilePreview() {
    document.querySelectorAll('.custom-file-input').forEach(input => {
        input.addEventListener('change', function() {
            const label = this.nextElementSibling;
            if (label && label.classList.contains('custom-file-label')) {
                label.textContent = this.files[0] ? this.files[0].name : 'Choose file';
            }
            
            // Image preview
            if (this.files && this.files[0]?.type.match('image.*')) {
                const preview = this.closest('.file-upload-wrapper')?.querySelector('.image-preview');
                if (preview) {
                    const reader = new FileReader();
                    reader.onload = e => {
                        preview.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded" alt="Preview">`;
                        preview.classList.remove('d-none');
                    };
                    reader.readAsDataURL(this.files[0]);
                }
            }
        });
    });
}

/**
 * Initialize tags input
 */
function initTagsInput() {
    const tagsInputs = document.querySelectorAll('input[data-role="tagsinput"]');
    if (tagsInputs.length > 0 && typeof $.fn.tagsinput === 'undefined') {
        loadScript('https://cdnjs.cloudflare.com/ajax/libs/bootstrap-tagsinput/0.8.0/bootstrap-tagsinput.min.js')
            .then(() => {
                $(tagsInputs).tagsinput({
                    tagClass: 'badge bg-primary me-1 mb-1',
                    trimValue: true,
                    maxTags: 10,
                    maxChars: 20,
                    confirmKeys: [13, 44, 32] // Enter, comma, space
                });
            });
    }
}

/**
 * Initialize modals
 */
function initModals() {
    // Close modals when clicking outside
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                const modalInstance = bootstrap.Modal.getInstance(this);
                if (modalInstance) modalInstance.hide();
            }
        });
    });
}

/**
 * Initialize back to top button
 */
function initBackToTop() {
    const btn = document.getElementById('btn-back-to-top');
    if (btn) {
        window.addEventListener('scroll', () => {
            btn.style.display = (window.pageYOffset > 300) ? 'block' : 'none';
        });
        
        btn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
}

/**
 * Initialize theme switcher
 */
function initThemeSwitcher() {
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
        // Load saved theme or default to light
        const currentTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-bs-theme', currentTheme);
        toggle.checked = currentTheme === 'dark';
        updateThemeIcon(toggle);
        
        // Toggle theme on change
        toggle.addEventListener('change', function() {
            const newTheme = this.checked ? 'dark' : 'light';
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(this);
        });
    }
}

/**
 * Update theme icon based on current theme
 */
function updateThemeIcon(toggle) {
    const icon = toggle.nextElementSibling?.querySelector('i');
    if (icon) {
        icon.className = toggle.checked ? 'fas fa-sun' : 'fas fa-moon';
    }
}

/**
 * Set up CSRF token for AJAX requests
 */
function setupAjaxCsrf() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    if (csrfToken) {
        $.ajaxSetup({
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
    }
}

/**
 * Initialize other components
 */
function initComponents() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add active class to current nav item
    const currentPage = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        }
    });
}

/**
 * Load script dynamically
 */
function loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}
