/**
 * Tray Management
 */

export const TrayManager = {
    setupTray(tray, settingsButton) {
        if (!tray || !settingsButton) return;

        let isOpen = false;

        const toggleTray = () => {
            isOpen = !isOpen;
            tray.classList.toggle('open', isOpen);
            settingsButton.setAttribute('aria-expanded', isOpen.toString());
            settingsButton.classList.toggle('active', isOpen);
        };

        // Toggle on button click
        settingsButton.addEventListener('click', (e) => {
            e.preventDefault();
            toggleTray();
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (isOpen && !tray.contains(e.target) && e.target !== settingsButton) {
                toggleTray();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (isOpen && e.key === 'Escape') {
                toggleTray();
            }
        });

        return {
            toggle: toggleTray,
            close: () => {
                if (isOpen) toggleTray();
            },
            open: () => {
                if (!isOpen) toggleTray();
            }
        };
    }
}; 