// ============================================
// SkillMatch Pro — Main JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initSidebar();
    initFlashDismiss();
    initAnimations();
});

// Theme Toggle
function initTheme() {
    const toggle = document.getElementById('themeToggle');
    const icon = document.getElementById('themeIcon');
    if (!toggle) return;

    const saved = localStorage.getItem('sm-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved, icon);

    toggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('sm-theme', next);
        updateThemeIcon(next, icon);
    });
}

function updateThemeIcon(theme, icon) {
    if (!icon) return;
    icon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
}

// Sidebar Toggle (mobile)
function initSidebar() {
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (!toggle || !sidebar) return;

    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    // Close on outside click (mobile)
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
            if (!sidebar.contains(e.target) && e.target !== toggle) {
                sidebar.classList.remove('open');
            }
        }
    });
}

// Auto-dismiss flash messages
function initFlashDismiss() {
    const flashes = document.querySelectorAll('.flash-msg');
    flashes.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            setTimeout(() => msg.remove(), 300);
        }, 5000);
    });
}

// Staggered card animations
function initAnimations() {
    const cards = document.querySelectorAll('.stat-card, .card, .employee-card, .feature-card');
    cards.forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(16px)';
        card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 80 * i);
    });
}

// Toast notification helper
function showToast(message, type = 'success') {
    const container = document.querySelector('.flash-container') || createFlashContainer();
    const msg = document.createElement('div');
    msg.className = `flash-msg flash-${type}`;
    const icons = { success: 'fa-check-circle', danger: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
    msg.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
    container.appendChild(msg);
    setTimeout(() => {
        msg.style.opacity = '0';
        setTimeout(() => msg.remove(), 300);
    }, 4000);
}

function createFlashContainer() {
    const c = document.createElement('div');
    c.className = 'flash-container';
    document.querySelector('.content-body')?.prepend(c);
    return c;
}
