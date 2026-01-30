/* ================= MESSAGE HANDLER ================= */
window.addEventListener('message', (event) => {
    const { type, payload } = event.data || {};

    switch (type) {
        case 'TOGGLE_DARK':
            AppState.toggleDarkMode();
            break;

        case 'TOGGLE_SIDEBAR':
            AppState.toggleSidebar();
            break;
            
        case 'IFRAME_READY':
            // Iframe is ready, sync state
            AppState.syncAll();
            // Also sync current route UI (active menu + header title)
            if (window.router) {
                window.router.handleRoute();
            }
            break;
            
        case 'NAVIGATE':
            // Handle navigation from sidebar
            if (window.router) {
                window.router.navigate(payload);
                // Update sidebar active state
                const sidebarFrame = document.getElementById('sidebarFrame');
                if (sidebarFrame?.contentWindow) {
                    sidebarFrame.contentWindow.postMessage({
                        type: 'UPDATE_ACTIVE_ROUTE',
                        payload: payload
                    }, '*');
                }
            } else {
                // Router not ready yet, retry
                setTimeout(() => {
                    if (window.router) {
                        window.router.navigate(payload);
                    }
                }, 300);
            }
            break;
    }
});