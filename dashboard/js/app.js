/**
 * DevOps Agent — Main Dashboard Application
 * Handles navigation, UI interactions, and state management.
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initNotifications();
    initCounters();
    initActivityFeed();
    initBgParticles();
    initMarketplace();
    
    // Show welcome toast
    showToast('NUCLEUS Agent System Online', 'success', 'fa-solid fa-check-double');
});

// ── NAVIGATION ──────────────────────────────────────────────────────────
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const viewSections = document.querySelectorAll('.view-section');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const target = item.getAttribute('data-target');
            
            // Update nav active state
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Switch views with animation
            viewSections.forEach(section => {
                section.classList.remove('active');
                if (section.id === `view-${target}`) {
                    section.classList.add('active');
                    triggerSectionAnimate(section);
                }
            });
        });
    });
}

function triggerSectionAnimate(section) {
    const cards = section.querySelectorAll('.glass, .kpi-card, .data-table, .node-card, .timeline-item');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(15px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 60);
    });
}

// ── NOTIFICATIONS ───────────────────────────────────────────────────────
function initNotifications() {
    const notifBtn = document.getElementById('notif-btn');
    const notifPanel = document.getElementById('notif-panel');
    const notifClose = document.getElementById('notif-close');
    const notifOverlay = document.getElementById('notif-overlay');

    const toggleNotif = () => {
        notifPanel.classList.toggle('open');
        notifOverlay.classList.toggle('open');
    };

    notifBtn.addEventListener('click', toggleNotif);
    notifClose.addEventListener('click', toggleNotif);
    notifOverlay.addEventListener('click', toggleNotif);
}

// ── COUNTERS ────────────────────────────────────────────────────────────
function initCounters() {
    const counters = document.querySelectorAll('.counter-animate');
    
    const animateCounter = (el) => {
        const target = +el.getAttribute('data-target');
        const count = +el.innerText;
        const speed = 200;
        const inc = target / speed;

        if (count < target) {
            el.innerText = Math.ceil(count + inc);
            setTimeout(() => animateCounter(el), 1);
        } else {
            el.innerText = target;
        }
    };

    // Use Intersection Observer for trigger
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(c => observer.observe(c));
}

// ── ACTIVITY FEED ───────────────────────────────────────────────────────
function initActivityFeed() {
    const feed = document.getElementById('activity-feed');
    const activities = [
        { type: 'blue', icon: 'fa-robot', text: 'Agent running <strong>health check</strong> on prod-cluster', time: 'Just now' },
        { type: 'green', icon: 'fa-check-circle', text: 'Pipeline <code>webapp-deploy</code> completed successfully', time: '1m ago' },
        { type: 'purple', icon: 'fa-shield-halved', text: 'Security scan identified <strong>3 high</strong> vulnerabilities', time: '5m ago' },
        { type: 'yellow', icon: 'fa-coins', text: 'FinOps: Recommended termination of <strong>2 idle</strong> instances', time: '12m ago' }
    ];

    setInterval(() => {
        const act = activities[Math.floor(Math.random() * activities.length)];
        addFeedItem(act);
    }, 8000);
}

function addFeedItem(act) {
    const feed = document.getElementById('activity-feed');
    const item = document.createElement('div');
    item.className = 'feed-item';
    item.innerHTML = `
        <div class="feed-icon ${act.type}"><i class="fa-solid ${act.icon}"></i></div>
        <div class="feed-text">${act.text}</div>
        <div class="feed-time">${act.time}</div>
    `;
    feed.prepend(item);
    
    if (feed.children.length > 8) {
        feed.removeChild(feed.lastChild);
    }
}

// ── TOAST SYSTEM ────────────────────────────────────────────────────────
function showToast(message, type = 'info', icon = 'fa-solid fa-circle-info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="${icon} toast-icon"></i>
        <div class="toast-msg">${message}</div>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ── BACKGROUND PARTICLES ────────────────────────────────────────────────
function initBgParticles() {
    const canvas = document.getElementById('bg-canvas');
    const ctx = canvas.getContext('2d');
    
    let w, h, particles = [];
    
    const resize = () => {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    };
    
    window.addEventListener('resize', resize);
    resize();

    class Particle {
        constructor() {
            this.x = Math.random() * w;
            this.y = Math.random() * h;
            this.size = Math.random() * 2;
            this.vx = (Math.random() - 0.5) * 0.3;
            this.vy = (Math.random() - 0.5) * 0.3;
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;
            if (this.x < 0 || this.x > w) this.vx *= -1;
            if (this.y < 0 || this.y > h) this.vy *= -1;
        }
        draw() {
            ctx.fillStyle = 'rgba(59, 130, 246, 0.5)';
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    for (let i = 0; i < 80; i++) particles.push(new Particle());

    function animate() {
        ctx.clearRect(0, 0, w, h);
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        requestAnimationFrame(animate);
    }
    animate();
}

// ── MARKETPLACE DEPLOYMENT ─────────────────────────────────────────────
function initMarketplace() {
    const deployBtns = document.querySelectorAll('.deploy-blueprint');
    const jobsTable = document.querySelector('#deployment-jobs tbody');

    deployBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const app = btn.getAttribute('data-app');
            const taskId = 'DEP-' + Math.floor(Math.random() * 9000 + 1000);
            
            showToast(`Starting deployment of ${app}...`, 'info', 'fa-solid fa-cloud-arrow-up');
            
            // Add job to table
            if (jobsTable.innerText.includes('No active deployments')) {
                jobsTable.innerHTML = '';
            }

            const row = document.createElement('tr');
            row.id = `job-${taskId}`;
            row.innerHTML = `
                <td><code>${taskId}</code></td>
                <td><strong>${app}</strong></td>
                <td><span class="status-badge running"><i class="fa-solid fa-spinner fa-spin"></i> Provisioning</span></td>
                <td><div class="progress-bar"><div class="progress-fill" style="width: 10%; background: var(--primary)"></div></div></td>
            `;
            jobsTable.prepend(row);

            // Simulate Agent working through steps
            await simulateDeployment(taskId, app);
        });
    });
}

async function simulateDeployment(taskId, app) {
    const row = document.getElementById(`job-${taskId}`);
    const statusBadge = row.querySelector('.status-badge');
    const progressFill = row.querySelector('.progress-fill');

    // Step 1: Infra
    await delay(2000);
    progressFill.style.width = '35%';
    statusBadge.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creating Infra';
    
    // Step 2: Config
    await delay(3000);
    progressFill.style.width = '70%';
    statusBadge.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Configuring App';
    statusBadge.className = 'status-badge warning';

    // Step 3: Done
    await delay(2500);
    progressFill.style.width = '100%';
    progressFill.style.background = 'var(--success)';
    statusBadge.innerHTML = '<i class="fa-solid fa-check"></i> Deployed';
    statusBadge.className = 'status-badge success';

    showToast(`${app} Stack is now LIVE!`, 'success', 'fa-solid fa-rocket');
    
    // Add to activity feed
    addFeedItem({
        type: 'green',
        icon: 'fa-rocket',
        text: `Agent successfully <strong>deployed</strong> ${app} stack (ID: ${taskId})`,
        time: 'Just now'
    });
}

function delay(ms) {
    return new Promise(res => setTimeout(res, ms));
}
