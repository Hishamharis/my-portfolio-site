// ========== PORTFOLIO JAVASCRIPT ==========
// Fixed: CSRF token handling, loading screen, contact form POST
'use strict';

// ========== CONFIGURATION ==========
const CONFIG = {
    particles: {
        count: window.innerWidth > 768 ? 40 : 20,
        enabled: !window.matchMedia('(prefers-reduced-motion: reduce)').matches
    },
    debug: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
};

// ========== SECURITY ==========
const sanitizeInput = (input) => {
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
};

// ========== CSRF TOKEN HELPER ==========
// Reads the csrftoken cookie that Django sets automatically
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ========== LOADING SCREEN ==========
window.addEventListener('load', () => {
    const loadingScreen = document.getElementById('loadingScreen');
    if (loadingScreen) {
        setTimeout(() => {
            loadingScreen.classList.add('hidden');
        }, 800);
    }
});

// ========== PARTICLES.JS ==========
document.addEventListener('DOMContentLoaded', () => {
    if (typeof particlesJS === 'undefined' || !document.getElementById('particles-js')) return;

    setTimeout(() => {
        if (!CONFIG.particles.enabled) return;
        particlesJS('particles-js', {
            particles: {
                number: { value: CONFIG.particles.count, density: { enable: true, value_area: 1000 } },
                color: { value: '#00d9ff' },
                shape: { type: 'circle' },
                opacity: { value: 0.4, random: true, anim: { enable: true, speed: 0.8, opacity_min: 0.1, sync: false } },
                size: { value: 2, random: true, anim: { enable: true, speed: 1.5, size_min: 0.1, sync: false } },
                line_linked: { enable: true, distance: 120, color: '#00d9ff', opacity: 0.2, width: 1 },
                move: { enable: true, speed: 1.5, direction: 'none', random: true, straight: false, out_mode: 'out', bounce: false }
            },
            interactivity: {
                detect_on: 'canvas',
                events: { onhover: { enable: true, mode: 'grab' }, onclick: { enable: false }, resize: true },
                modes: { grab: { distance: 120, line_linked: { opacity: 0.4 } } }
            },
            retina_detect: true
        });
    }, 500);
});

// ========== AOS ANIMATION ==========
setTimeout(() => {
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 800, once: true, offset: 100, easing: 'ease-out-cubic', disable: window.innerWidth < 768 });
    }
}, 300);

// ========== TYPING EFFECT ==========
class TypeWriter {
    constructor(element, words, wait = 3000) {
        this.element = element;
        this.words = words;
        this.text = '';
        this.wordIndex = 0;
        this.wait = parseInt(wait, 10);
        this.isDeleting = false;
        this.type();
    }

    type() {
        const current = this.wordIndex % this.words.length;
        const fullText = this.words[current];

        if (this.isDeleting) {
            this.text = fullText.substring(0, this.text.length - 1);
        } else {
            this.text = fullText.substring(0, this.text.length + 1);
        }

        this.element.textContent = this.text;
        let typeSpeed = 120;

        if (this.isDeleting) typeSpeed /= 2;

        if (!this.isDeleting && this.text === fullText) {
            typeSpeed = this.wait;
            this.isDeleting = true;
        } else if (this.isDeleting && this.text === '') {
            this.isDeleting = false;
            this.wordIndex++;
            typeSpeed = 500;
        }

        setTimeout(() => this.type(), typeSpeed);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const typingElement = document.getElementById('typingText');
    if (typingElement) {
        new TypeWriter(typingElement, [
            'Full-Stack Developer',
            'Django Specialist',
            'UI/UX Enthusiast',
            'Problem Solver',
            'Tech Innovator'
        ], 2000);
    }
});

// ========== NAVBAR SCROLL ==========
let ticking = false;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    if (!ticking) {
        requestAnimationFrame(() => {
            if (navbar) {
                navbar.classList.toggle('scrolled', window.pageYOffset > 100);
            }
            ticking = false;
        });
        ticking = true;
    }
}, { passive: true });

// ========== SMOOTH SCROLLING ==========
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#' || !document.querySelector(href)) return;
            e.preventDefault();

            const target = document.querySelector(href);
            window.scrollTo({ top: target.offsetTop - 80, behavior: 'smooth' });

            document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
            this.classList.add('active');

            const navbarCollapse = document.querySelector('.navbar-collapse');
            if (navbarCollapse?.classList.contains('show')) navbarCollapse.classList.remove('show');
        });
    });
});

// ========== ACTIVE SECTION HIGHLIGHTING ==========
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link');
let sectionTicking = false;

window.addEventListener('scroll', () => {
    if (!sectionTicking) {
        requestAnimationFrame(() => {
            let current = '';
            sections.forEach(section => {
                if (pageYOffset >= (section.offsetTop - 150)) current = section.getAttribute('id');
            });
            navLinks.forEach(link => {
                link.classList.toggle('active', link.getAttribute('href') === `#${current}`);
            });
            sectionTicking = false;
        });
        sectionTicking = true;
    }
}, { passive: true });

// ========== COUNTER ANIMATION ==========
const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const target = parseInt(entry.target.getAttribute('data-count'));
            const duration = 1500;
            const increment = target / (duration / 16);
            let current = 0;

            const update = () => {
                current += increment;
                if (current < target) {
                    entry.target.textContent = Math.ceil(current);
                    requestAnimationFrame(update);
                } else {
                    entry.target.textContent = target + (target > 10 ? '+' : '');
                }
            };
            update();
            counterObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.3 });

document.querySelectorAll('.stat-number').forEach(counter => counterObserver.observe(counter));

// ========== SKILL BARS ANIMATION ==========
const skillObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.style.width = entry.target.getAttribute('data-progress') + '%';
            }, 100);
            skillObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.3 });

document.querySelectorAll('.skill-progress').forEach(skill => {
    skill.style.width = '0%';
    skillObserver.observe(skill);
});

// ========== SCROLL TO TOP ==========
const scrollTopBtn = document.getElementById('scrollTop');
let scrollTicking = false;

window.addEventListener('scroll', () => {
    if (!scrollTicking) {
        requestAnimationFrame(() => {
            if (scrollTopBtn) scrollTopBtn.classList.toggle('visible', window.pageYOffset > 300);
            scrollTicking = false;
        });
        scrollTicking = true;
    }
}, { passive: true });

scrollTopBtn?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

// ========== CONTACT FORM — DJANGO AJAX ==========
const contactForm = document.getElementById('contactForm');

if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name    = sanitizeInput(document.getElementById('name').value);
        const email   = sanitizeInput(document.getElementById('email').value);
        const subject = sanitizeInput(document.getElementById('subject').value);
        const message = sanitizeInput(document.getElementById('message').value);

        // Basic email check
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            showNotification('Please enter a valid email address', 'error');
            return;
        }

        const submitBtn = contactForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Sending...';

        try {
            const response = await fetch('/api/contact/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')   // ← Django CSRF cookie
                },
                body: JSON.stringify({ name, email, subject, message })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                showNotification('Message sent successfully! I\'ll get back to you soon.', 'success');
                contactForm.reset();
            } else {
                showNotification(data.error || 'Failed to send message.', 'error');
            }

        } catch (error) {
            showNotification('Network error. Please try again.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
}

// ========== NOTIFICATION SYSTEM ==========
function showNotification(message, type = 'info') {
    document.querySelector('.notification')?.remove();

    const icons = { success: 'check-circle', error: 'exclamation-circle', info: 'info-circle' };
    const colors = {
        success: 'rgba(34, 197, 94, 0.9)',
        error:   'rgba(239, 68, 68, 0.9)',
        info:    'rgba(59, 130, 246, 0.9)'
    };

    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerHTML = `
        <i class="bi bi-${icons[type] || icons.info}"></i>
        <span>${message}</span>
        <button class="notification-close">&times;</button>
    `;

    Object.assign(notification.style, {
        position: 'fixed', top: '20px', right: '20px',
        padding: '1rem 1.5rem',
        background: colors[type] || colors.info,
        color: 'white', borderRadius: '10px',
        display: 'flex', alignItems: 'center', gap: '1rem',
        zIndex: '10000', animation: 'slideInRight 0.3s ease',
        boxShadow: '0 10px 40px rgba(0,0,0,0.3)',
        backdropFilter: 'blur(10px)', maxWidth: '400px'
    });

    document.body.appendChild(notification);

    const dismiss = () => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    };

    notification.querySelector('.notification-close').addEventListener('click', dismiss);
    setTimeout(() => { if (notification.parentElement) dismiss(); }, 5000);
}

// Notification keyframes (injected once)
const notifStyle = document.createElement('style');
notifStyle.textContent = `
    @keyframes slideInRight  { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes slideOutRight { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
    .notification-close { background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer; padding: 0; line-height: 1; }
`;
document.head.appendChild(notifStyle);