/* ================= INITIALIZE APP ================= */
function initializeApp() {
    AppState.init();
    
    // Setup mobile sidebar overlay
    const overlay = document.getElementById('sidebarOverlay');
    if (overlay) {
        overlay.addEventListener('click', () => {
            if (!AppState.sidebarCollapsed) {
                AppState.toggleSidebar();
            }
        });
    }
    
    // Handle window resize for mobile sidebar
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            const overlay = document.getElementById('sidebarOverlay');
            const sidebarFrame = document.getElementById('sidebarFrame');
            
            // On desktop, hide overlay and show sidebar normally
            if (window.innerWidth > 768) {
                if (overlay) overlay.classList.remove('active');
                if (sidebarFrame) {
                    sidebarFrame.style.position = '';
                    sidebarFrame.style.transform = '';
                }
            } else {
                // On mobile, handle sidebar state
                if (sidebarFrame && !AppState.sidebarCollapsed) {
                    if (overlay) overlay.classList.add('active');
                }
            }
        }, 250);
    });
    
    // Wait a bit for router to initialize
    setTimeout(() => {
        if (window.router) {
            // Load initial route
            window.router.handleRoute();
        }
    }, 200);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}