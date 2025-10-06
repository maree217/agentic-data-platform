// ==========================================================================
// Agentic Data Platform - Main JavaScript
// ==========================================================================

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initSmoothScroll();
    initScrollAnimations();
    initMobileMenu();
    initFormValidation();
});

// ==========================================================================
// Tab Navigation (Use Cases)
// ==========================================================================
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');

            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            const activeContent = document.getElementById(tabId);
            if (activeContent) {
                activeContent.classList.add('active');
                activeContent.classList.add('fade-in');
            }
        });
    });

    // Activate first tab by default
    if (tabButtons.length > 0) {
        tabButtons[0].click();
    }
}

// ==========================================================================
// Smooth Scroll Navigation
// ==========================================================================
function initSmoothScroll() {
    const navLinks = document.querySelectorAll('a[href^="#"]');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');

            // Check if it's a valid section ID
            if (href === '#' || href === '#!') return;

            const targetSection = document.querySelector(href);
            if (targetSection) {
                e.preventDefault();

                // Calculate offset for sticky header
                const headerHeight = document.querySelector('.header')?.offsetHeight || 0;
                const targetPosition = targetSection.offsetTop - headerHeight - 20;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                closeMobileMenu();
            }
        });
    });
}

// ==========================================================================
// Scroll Animations
// ==========================================================================
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animatedElements = document.querySelectorAll(
        '.feature-card, .workflow-step, .comparison-card, .pricing-card, .use-case-content'
    );

    animatedElements.forEach(el => observer.observe(el));
}

// ==========================================================================
// Mobile Menu
// ==========================================================================
function initMobileMenu() {
    const menuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
            menuToggle.classList.toggle('active');
            document.body.classList.toggle('menu-open');
        });
    }
}

function closeMobileMenu() {
    const mobileMenu = document.getElementById('mobile-menu');
    const menuToggle = document.getElementById('mobile-menu-toggle');

    if (mobileMenu && menuToggle) {
        mobileMenu.classList.remove('active');
        menuToggle.classList.remove('active');
        document.body.classList.remove('menu-open');
    }
}

// ==========================================================================
// Form Validation and Submission
// ==========================================================================
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');

    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(form);
            const data = Object.fromEntries(formData);

            // Basic validation
            if (!validateForm(data)) {
                showNotification('Please fill in all required fields', 'error');
                return;
            }

            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';

            try {
                // In production, send to actual endpoint
                await simulateFormSubmission(data);

                showNotification('Thank you! We\'ll be in touch soon.', 'success');
                form.reset();
            } catch (error) {
                showNotification('Something went wrong. Please try again.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    });
}

function validateForm(data) {
    // Check required fields
    const requiredFields = ['name', 'email', 'company'];
    return requiredFields.every(field => data[field] && data[field].trim() !== '');
}

async function simulateFormSubmission(data) {
    // Simulate API call
    return new Promise((resolve) => {
        setTimeout(() => {
            console.log('Form submitted:', data);
            resolve();
        }, 1000);
    });
}

// ==========================================================================
// Notification System
// ==========================================================================
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button class="notification-close">&times;</button>
    `;

    document.body.appendChild(notification);

    // Add close functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.classList.add('notification-exit');
        setTimeout(() => notification.remove(), 300);
    });

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.add('notification-exit');
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);

    // Animate in
    setTimeout(() => notification.classList.add('notification-visible'), 10);
}

// ==========================================================================
// Video Player Control
// ==========================================================================
function playDemoVideo() {
    const videoPlaceholder = document.getElementById('video-placeholder');

    // In production, replace with actual video embed
    videoPlaceholder.innerHTML = `
        <iframe
            width="100%"
            height="500"
            src="https://www.youtube.com/embed/YOUR_VIDEO_ID?autoplay=1"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
        ></iframe>
    `;
}

// ==========================================================================
// Scroll Progress Indicator
// ==========================================================================
function updateScrollProgress() {
    const scrollProgress = document.getElementById('scroll-progress');
    if (!scrollProgress) return;

    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight - windowHeight;
    const scrolled = window.scrollY;
    const progress = (scrolled / documentHeight) * 100;

    scrollProgress.style.width = `${progress}%`;
}

window.addEventListener('scroll', updateScrollProgress);

// ==========================================================================
// Copy to Clipboard (for code snippets)
// ==========================================================================
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy', 'error');
    });
}

// Attach to code blocks if present
document.querySelectorAll('.code-block').forEach(block => {
    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-code-btn';
    copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
    copyBtn.addEventListener('click', () => {
        const code = block.querySelector('code')?.textContent || block.textContent;
        copyToClipboard(code);
    });
    block.appendChild(copyBtn);
});

// ==========================================================================
// Statistics Counter Animation
// ==========================================================================
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Animate stats when they come into view
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
            entry.target.classList.add('counted');
            const target = parseInt(entry.target.getAttribute('data-target'));
            animateCounter(entry.target, target);
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-number[data-target]').forEach(stat => {
    statsObserver.observe(stat);
});

// ==========================================================================
// Request Demo Modal
// ==========================================================================
function openDemoModal() {
    const modal = document.getElementById('demo-modal');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeDemoModal() {
    const modal = document.getElementById('demo-modal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Close modal on outside click
window.addEventListener('click', (e) => {
    const modal = document.getElementById('demo-modal');
    if (e.target === modal) {
        closeDemoModal();
    }
});

// Close modal on ESC key
window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeDemoModal();
    }
});

// ==========================================================================
// GitHub Stats (if integrated)
// ==========================================================================
async function fetchGitHubStats() {
    const statsContainer = document.getElementById('github-stats');
    if (!statsContainer) return;

    try {
        // In production, replace with actual GitHub API call
        const stats = {
            stars: 1234,
            forks: 234,
            contributors: 45
        };

        statsContainer.innerHTML = `
            <div class="github-stat">
                <i class="fab fa-star"></i>
                <span>${stats.stars}</span> Stars
            </div>
            <div class="github-stat">
                <i class="fas fa-code-branch"></i>
                <span>${stats.forks}</span> Forks
            </div>
            <div class="github-stat">
                <i class="fas fa-users"></i>
                <span>${stats.contributors}</span> Contributors
            </div>
        `;
    } catch (error) {
        console.error('Failed to fetch GitHub stats:', error);
    }
}

// Fetch stats on page load
fetchGitHubStats();

// ==========================================================================
// Export functions for global use
// ==========================================================================
window.AgenticPlatform = {
    playDemoVideo,
    openDemoModal,
    closeDemoModal,
    copyToClipboard,
    showNotification
};
