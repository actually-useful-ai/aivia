/**
 * Loading state utilities
 */

/**
 * Loading state management system
 */
export const LoadingState = {
    /**
     * Sets the loading state of a button
     * @param {HTMLElement} button - The button element
     * @param {boolean} isLoading - Whether the button is loading
     * @param {string} loadingText - Text to display while loading
     */
    setLoadingState(button, isLoading, loadingText = 'Processing...') {
        if (isLoading) {
            button.classList.add("loading");
            button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
            button.disabled = true;
        } else {
            button.classList.remove("loading");
            button.disabled = false;
        }
    },

    /**
     * Executes an operation with loading state
     * @param {HTMLElement} button - The button element
     * @param {Function} operation - The operation to execute
     * @param {string} loadingText - Text to display while loading
     * @returns {Promise<void>}
     */
    async withLoadingState(button, operation, loadingText = 'Processing...') {
        const originalButtonText = button.innerHTML;
        this.setLoadingState(button, true, loadingText);
        
        try {
            await operation();
        } finally {
            this.setLoadingState(button, false);
            button.innerHTML = originalButtonText;
        }
    }
}; 