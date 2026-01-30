/* ================= GLOBAL STATE MANAGEMENT ================= */
const AppState = {
    darkMode: localStorage.getItem('darkMode') === 'true' || false,
    sidebarCollapsed: localStorage.getItem('sidebarCollapsed') === 'true' || false,
    
    init() {
        // Apply saved state
        if (this.darkMode) {
            document.documentElement.classList.add('dark');
        }
        if (this.sidebarCollapsed) {
            document.getElementById('sidebarFrame')?.classList.add('collapsed');
        }
        
        // Sync with iframes after they load
        this.syncAll();
    },
    
    save() {
        localStorage.setItem('darkMode', this.darkMode);
        localStorage.setItem('sidebarCollapsed', this.sidebarCollapsed);
    },
    
    syncAll() {
        // Wait for iframes to load
        setTimeout(() => {
            this.broadcast({
                type: 'SYNC_DARK',
                payload: this.darkMode
            });
            this.broadcast({
                type: 'SYNC_SIDEBAR_COLLAPSED',
                payload: this.sidebarCollapsed
            });
        }, 100);
    },
    
    toggleDarkMode() {
        this.darkMode = !this.darkMode;
        document.documentElement.classList.toggle('dark', this.darkMode);
        this.broadcast({
            type: 'SYNC_DARK',
            payload: this.darkMode
        });
        this.save();
    },
    
    toggleSidebar() {
        const sidebarFrame = document.getElementById('sidebarFrame');
        const overlay = document.getElementById('sidebarOverlay');
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile) {
            // On mobile: toggle sidebar visibility (not collapsed state)
            const isCurrentlyVisible = sidebarFrame && !sidebarFrame.classList.contains('collapsed');
            
            if (isCurrentlyVisible) {
                // Close sidebar on mobile
                if (sidebarFrame) {
                    sidebarFrame.classList.add('collapsed');
                }
                if (overlay) {
                    overlay.classList.remove('active');
                }
            } else {
                // Open sidebar on mobile
                if (sidebarFrame) {
                    sidebarFrame.classList.remove('collapsed');
                }
                if (overlay) {
                    overlay.classList.add('active');
                }
            }
        } else {
            // On desktop: toggle collapsed state
            this.sidebarCollapsed = !this.sidebarCollapsed;
            if (sidebarFrame) {
                sidebarFrame.classList.toggle('collapsed', this.sidebarCollapsed);
            }
            if (overlay) {
                overlay.classList.remove('active');
            }
            this.save();
        }
        
        // Broadcast collapsed state to sidebar iframe
        const isCollapsed = sidebarFrame?.classList.contains('collapsed') || false;
        this.broadcast({
            type: 'SYNC_SIDEBAR_COLLAPSED',
            payload: isCollapsed
        });
    },
    
    broadcast(message) {
        const headerFrame = document.getElementById('headerFrame');
        const sidebarFrame = document.getElementById('sidebarFrame');
        
        [headerFrame, sidebarFrame].forEach(frame => {
            try {
                frame?.contentWindow?.postMessage(message, '*');
            } catch (e) {
                console.warn('Failed to post message to iframe:', e);
            }
        });
    }
};