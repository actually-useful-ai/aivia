/**
 * Panel Logo Management
 */

export const PanelLogoManager = {
    /**
     * Adds a logo to the panel
     * @param {string} logoUrl - URL of the logo image
     */
    addPanelLogo(logoUrl = "https://i.imgur.com/aSNdzIx.gif") {
        const sidePanel = document.querySelector(".right-panel-container");
        if (!sidePanel) {
            console.error("Side panel container not found.");
            return;
        }

        let logo = document.querySelector(".side-panel-logo");
        if (!logo) {
            logo = document.createElement("img");
            logo.src = logoUrl;
            logo.className = "side-panel-logo";
            logo.alt = "Panel Logo";
            logo.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 120px;
                height: 120px;
                opacity: 0.5;
                z-index: 1;
            `;
            sidePanel.appendChild(logo);
        }

        // Show logo when panel is empty
        const observer = new MutationObserver(() => {
            const panelContent = sidePanel.querySelector(".panel-content");
            const isEmpty = !panelContent || !panelContent.children.length;
            logo.style.display = isEmpty ? "block" : "none";
        });

        observer.observe(sidePanel, {
            childList: true,
            subtree: true,
        });

        // Initial state
        const panelContent = sidePanel.querySelector(".panel-content");
        const isEmpty = !panelContent || !panelContent.children.length;
        logo.style.display = isEmpty ? "block" : "none";
    }
}; 