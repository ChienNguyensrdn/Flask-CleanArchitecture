/* ================= SIDEBAR FUNCTIONALITY ================= */
function toggleSidebar() {
    window.parent.postMessage({ type: "TOGGLE_SIDEBAR" }, "*");
}

/* ================= NAVIGATION ================= */
function navigateRoute(route) {
    // Send navigation message to parent
    window.parent.postMessage({ 
        type: "NAVIGATE", 
        payload: route 
    }, "*");
    
    // Update active state in sidebar
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-route') === route) {
            item.classList.add('active');
        }
    });
}

/* ================= SYNC WITH PARENT ================= */
window.addEventListener("message", (e) => {
    if (!e.data?.type) return;

    switch (e.data.type) {
        case "SYNC_DARK":
            document.documentElement.classList.toggle("dark", e.data.payload);
            break;
        case "SYNC_SIDEBAR_COLLAPSED":
            const sidebar = document.querySelector(".sidebar");
            if (sidebar) {
                if (e.data.payload) {
                    sidebar.classList.add("collapsed");
                } else {
                    sidebar.classList.remove("collapsed");
                }
            }
            break;
        case "UPDATE_ACTIVE_ROUTE":
            // Update active menu item based on current route
            const menuItems = document.querySelectorAll('.menu-item');
            menuItems.forEach(item => {
                item.classList.remove('active');
                if (item.getAttribute('data-route') === e.data.payload) {
                    item.classList.add('active');
                }
            });
            break;
    }
});

/* ================= NOTIFY PARENT WHEN READY ================= */
window.addEventListener("load", () => {
    window.parent.postMessage({ type: "IFRAME_READY" }, "*");
});