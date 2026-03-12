/**
 * Mobile responsiveness utilities
 */

/**
 * Mobile UI handling system
 */
export const MobileHandler = {
    /**
     * Handles mobile panel interactions
     * @param {string} panelId - The ID of the panel to handle
     * @param {HTMLElement} sidePanelsContainer - The side panels container element
     * @param {HTMLElement} inputContainer - The input container element
     */
    handleMobilePanel(panelId, sidePanelsContainer, inputContainer) {
        if (window.innerWidth <= 768) {
            // For mobile
            sidePanelsContainer.classList.toggle("active");
            if (sidePanelsContainer.classList.contains("active")) {
                inputContainer.style.display = "flex";
            } else {
                setTimeout(() => {
                    inputContainer.style.display = "flex";
                }, 300); // Match the transition duration
            }
        } else {
            // For desktop
            this.openPanel(panelId);
        }
    },

    /**
     * Sets up media query handling
     */
    setupMediaQuery() {
        const mediaQuery = window.matchMedia("(max-width: 1050px)");
        mediaQuery.addListener(this.handleMediaQueryChange);
        this.handleMediaQueryChange(mediaQuery);
    }
}; 