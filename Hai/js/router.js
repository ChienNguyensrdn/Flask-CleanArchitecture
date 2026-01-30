// ================= ROUTES CONFIGURATION =================
// Each route points to an HTML page that can bring its own CSS via <link> tags in <head>.
const routes = {
    '/': { title: 'Dashboard', file: './pages/dashboard.html' },
    '/dashboard': { title: 'Dashboard', file: './pages/dashboard.html' },
    '/users': { title: 'Users', file: './pages/users.html' },
    '/conference': { title: 'Conference / CFP', file: './pages/conference.html' },
    '/submissions': { title: 'Submissions', file: './pages/submissions.html' },
    '/program-committee': { title: 'Program Committee', file: './pages/program-committee.html' },
    '/assign-review': { title: 'Assign & Review', file: './pages/Assign-Review/assign-review.html' },
    '/assign-review/scores': { title: 'Scores & Comments', file: './pages/Assign-Review/assign-review-scores.html' },
    '/assign-review/discussion': { title: 'Internal Discussion', file: './pages/Assign-Review/assign-review-discussion.html' },
    '/assign-review/rebuttal': { title: 'Rebuttal (Optional)', file: './pages/Assign-Review/assign-review-rebuttal.html' },
    '/decisions': { title: 'Decisions', file: './pages/decisions.html' },
    '/camera-ready': { title: 'Camera-ready', file: './pages/camera-ready.html' },
    '/reports': { title: 'Reports & Analytics', file: './pages/reports.html' },
    '/settings': { title: 'Settings', file: './pages/settings.html' }
};

// ================= ROUTER CLASS =================
class Router {
    constructor(containerSelector) {
        this.container = document.querySelector(containerSelector);
        this.currentRoute = null;
        
        // Initialize router
        this.init();
    }
    
    init() {
        // Listen for hash change events (for hash-based routing)
        window.addEventListener('hashchange', () => this.handleRoute());
        
        // Handle initial route
        this.handleRoute();
    }
    
    async navigate(path) {
        // Normalize path - ensure it starts with /
        let normalizedPath = path;
        if (!normalizedPath.startsWith('/')) {
            normalizedPath = '/' + normalizedPath;
        }
        
        // Use hash-based routing to avoid server 404 errors on reload
        const hashPath = '#' + normalizedPath;
        
        // Update URL hash without reload
        if (window.location.hash !== hashPath) {
            window.location.hash = hashPath;
        } else {
            // If hash is already correct, just load the route
            await this.loadRoute(normalizedPath);
        }
    }
    
    async handleRoute() {
        // Use hash-based routing
        let path = window.location.hash.slice(1) || '/';
        
        // Normalize path - ensure it starts with / and remove trailing slashes
        if (path !== '/') {
            path = '/' + path.replace(/^\/+|\/+$/g, '');
        }
        
        await this.loadRoute(path);
    }
    
    async loadRoute(path) {
        // Normalize path
        const normalizedPath = path === '/' ? '/' : path.replace(/\/$/, '');
        
        // Get route from config
        const route = routes[normalizedPath] || routes['/'];
        const routeFile = route.file;
        
        if (this.currentRoute === routeFile) {
            // Already loaded, but still resync header/sidebar (useful when iframes reload)
            this.syncRouteUI(normalizedPath, route.title);
            return;
        }
        
        this.currentRoute = routeFile;
        
        try {
            // Show loading state
            if (this.container) {
                this.container.innerHTML = '<div class="loading-spinner">Đang tải...</div>';
            }
            
            // Fetch and load content
            const response = await fetch(routeFile);
            if (!response.ok) {
                throw new Error(`Failed to load: ${routeFile}`);
            }
            
            const html = await response.text();
            
            // Extract body content and head resources from the HTML
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const bodyContent = doc.body.innerHTML;
            
            // Extract and inject CSS links from head
            const cssLinks = doc.head.querySelectorAll('link[rel="stylesheet"]');
            cssLinks.forEach(link => {
                const href = link.getAttribute('href');
                // Check if this CSS is already loaded
                const existingLink = document.head.querySelector(`link[href="${href}"]`);
                if (!existingLink) {
                    const newLink = document.createElement('link');
                    newLink.rel = 'stylesheet';
                    newLink.href = href;
                    document.head.appendChild(newLink);
                }
            });
            
            // Inject content into container
            if (this.container) {
                this.container.innerHTML = bodyContent;
                
                // Re-initialize any scripts in the loaded content
                this.initScripts(this.container);
            }

            // Sync route state to iframes (header/sidebar)
            this.syncRouteUI(normalizedPath, route.title);
            
        } catch (error) {
            console.error('Route loading error:', error);
            if (this.container) {
                this.container.innerHTML = `
                    <div class="error-message">
                        <h3>Không thể tải trang</h3>
                        <p>${error.message}</p>
                        <button onclick="if(window.router) window.router.navigate('/')">Về trang chủ</button>
                    </div>
                `;
            }
        }
    }

    syncRouteUI(path, title) {
        const sidebarFrame = document.getElementById('sidebarFrame');
        const headerFrame = document.getElementById('headerFrame');

        if (sidebarFrame?.contentWindow) {
            sidebarFrame.contentWindow.postMessage(
                { type: 'UPDATE_ACTIVE_ROUTE', payload: path },
                '*'
            );
        }

        if (headerFrame?.contentWindow) {
            headerFrame.contentWindow.postMessage(
                { type: 'UPDATE_HEADER_TITLE', payload: title },
                '*'
            );
        }
    }
    
    initScripts(container) {
        // Re-run any scripts in the loaded content
        const scripts = container.querySelectorAll('script');
        scripts.forEach(oldScript => {
            const newScript = document.createElement('script');
            Array.from(oldScript.attributes).forEach(attr => {
                newScript.setAttribute(attr.name, attr.value);
            });
            newScript.appendChild(document.createTextNode(oldScript.innerHTML));
            oldScript.parentNode.replaceChild(newScript, oldScript);
        });
    }
}

// ================= EXPORT ROUTER INSTANCE =================
let router = null;

// Initialize router when DOM is ready
function initRouter() {
    const container = document.querySelector('.content-container');
    if (container) {
        router = new Router('.content-container');
        window.router = router;
    } else {
        // Retry if container not ready yet
        setTimeout(initRouter, 100);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRouter);
} else {
    initRouter();
}