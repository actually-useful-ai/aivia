/**
 * Panel Mutation Observer
 */

export const PanelObserver = {
    /**
     * Sets up mutation observers for panels
     * @param {HTMLElement} leftPanelContainer - The left panel container element
     * @param {Function} updateCallback - Callback to handle updates
     * @returns {MutationObserver} The created observer
     */
    setupMutationObservers(leftPanelContainer, updateCallback) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === "class") {
                    requestAnimationFrame(updateCallback);
                }
            });
        });

        observer.observe(leftPanelContainer, {
            attributes: true,
        });

        return observer;
    }
}; 