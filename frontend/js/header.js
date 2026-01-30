/* ================= THEME TOGGLE ================= */
function toggleTheme() {
    window.parent.postMessage({ type: "TOGGLE_DARK" }, "*");
}

function toggleMobileMenu() {
    window.parent.postMessage({ type: "TOGGLE_SIDEBAR" }, "*");
}

/* ================= SYNC WITH PARENT ================= */
window.addEventListener("message", (e) => {
    if (!e.data?.type) return;
    
    switch (e.data.type) {
        case "SYNC_DARK":
            document.documentElement.classList.toggle("dark", e.data.payload);
            break;
        case "UPDATE_HEADER_TITLE":
            const titleEl = document.getElementById('headerTitle');
            if (titleEl) titleEl.textContent = e.data.payload || 'Dashboard';
            break;
    }
});

/* ================= NOTIFY PARENT WHEN READY ================= */
window.addEventListener("load", () => {
    window.parent.postMessage({ type: "IFRAME_READY" }, "*");
});