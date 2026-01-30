// Interactive slider for "Assignment Progress" on Assign & Review page

(function () {
    function clamp(value, min, max) {
        return Math.min(max, Math.max(min, value));
    }

    function syncAssignReviewTabs() {
        const hash = window.location.hash || '';
        const path = hash.startsWith('#') ? hash.slice(1) : hash;
        const tabs = document.querySelectorAll('.ar-tabs .tab');
        if (!tabs.length) return;

        tabs.forEach((tab) => {
            const href = tab.getAttribute('href') || '';
            const isActive = href && href === '#' + path;
            tab.classList.toggle('active', isActive);
            tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
        });
    }

    function initAssignmentProgress() {
        const progress = document.querySelector('.card-side .progress');
        const bar = progress?.querySelector('.progress-bar');
        const knob = progress?.querySelector('.progress-knob');
        const pill = document.querySelector('.progress-pill');

        if (!progress || !bar || !knob || !pill) return;

        let isDragging = false;

        function applyPercent(percent) {
            const value = clamp(Math.round(percent), 0, 100);
            bar.style.width = value + '%';
            knob.style.left = value + '%';
            pill.textContent = value + '% Completed';
            progress.dataset.progress = String(value);
            knob.setAttribute('aria-valuenow', String(value));
        }

        function percentFromEvent(event) {
            const rect = progress.getBoundingClientRect();
            const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX;
            const ratio = (clientX - rect.left) / rect.width;
            return clamp(ratio * 100, 0, 100);
        }

        // Initialize from data attribute or default 75
        const initial = Number(progress.dataset.progress || '75');
        applyPercent(initial);

        function handlePointerDown(event) {
            event.preventDefault();
            isDragging = true;
            applyPercent(percentFromEvent(event));
            window.addEventListener('mousemove', handlePointerMove);
            window.addEventListener('mouseup', handlePointerUp);
            window.addEventListener('touchmove', handlePointerMove, { passive: false });
            window.addEventListener('touchend', handlePointerUp);
        }

        function handlePointerMove(event) {
            if (!isDragging) return;
            event.preventDefault();
            applyPercent(percentFromEvent(event));
        }

        function handlePointerUp() {
            if (!isDragging) return;
            isDragging = false;
            window.removeEventListener('mousemove', handlePointerMove);
            window.removeEventListener('mouseup', handlePointerUp);
            window.removeEventListener('touchmove', handlePointerMove);
            window.removeEventListener('touchend', handlePointerUp);
        }

        // Click anywhere on bar to set value
        progress.addEventListener('click', (event) => {
            // Avoid double handling when dragging knob
            if (isDragging) return;
            applyPercent(percentFromEvent(event));
        });

        // Dragging via knob
        knob.addEventListener('mousedown', handlePointerDown);
        knob.addEventListener('touchstart', handlePointerDown, { passive: false });

        // Keyboard accessibility
        knob.addEventListener('keydown', (event) => {
            const step = 5;
            const current = Number(progress.dataset.progress || '0');
            if (event.key === 'ArrowRight' || event.key === 'ArrowUp') {
                applyPercent(current + step);
            } else if (event.key === 'ArrowLeft' || event.key === 'ArrowDown') {
                applyPercent(current - step);
            } else if (event.key === 'Home') {
                applyPercent(0);
            } else if (event.key === 'End') {
                applyPercent(100);
            }
        });
    }

    function initTableCheckboxes() {
        // Handle checkbox selection for all tables on the page
        const tables = document.querySelectorAll('.table');
        
        tables.forEach(table => {
            const headerCheckbox = table.querySelector('thead input[type="checkbox"]');
            const rowCheckboxes = table.querySelectorAll('tbody input[type="checkbox"]');
            const rows = table.querySelectorAll('tbody tr');
            
            if (!headerCheckbox || !rowCheckboxes.length) return;
            
            // Select all functionality
            headerCheckbox.addEventListener('change', function() {
                const isChecked = this.checked;
                rowCheckboxes.forEach(cb => {
                    cb.checked = isChecked;
                });
                rows.forEach((row, index) => {
                    if (isChecked) {
                        row.classList.add('row-active');
                    } else {
                        row.classList.remove('row-active');
                    }
                });
            });
            
            // Individual row selection
            rowCheckboxes.forEach((checkbox, index) => {
                checkbox.addEventListener('change', function() {
                    const row = rows[index];
                    if (this.checked) {
                        row.classList.add('row-active');
                    } else {
                        row.classList.remove('row-active');
                    }
                    
                    // Update header checkbox state
                    const allChecked = Array.from(rowCheckboxes).every(cb => cb.checked);
                    const someChecked = Array.from(rowCheckboxes).some(cb => cb.checked);
                    headerCheckbox.checked = allChecked;
                    headerCheckbox.indeterminate = someChecked && !allChecked;
                });
            });
            
            // Initialize row-active class based on initial checked state
            rowCheckboxes.forEach((checkbox, index) => {
                if (checkbox.checked) {
                    rows[index].classList.add('row-active');
                }
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            syncAssignReviewTabs();
            initAssignmentProgress();
            initTableCheckboxes();
        });
    } else {
        syncAssignReviewTabs();
        initAssignmentProgress();
        initTableCheckboxes();
    }
})();

