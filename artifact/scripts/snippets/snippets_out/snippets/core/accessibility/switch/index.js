/**
 * Switch control utilities
 */

/**
 * Initializes switch control functionality
 * @returns {Object} Switch control functions
 */
export const initializeSwitchControl = () => {
    let currentFocusIndex = 0;
    const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    let scanning = false;
    let scanInterval;

    return {
        /**
         * Moves focus to the next focusable element
         */
        moveToNextElement: () => {
            const elements = Array.from(document.querySelectorAll(focusableElements));
            currentFocusIndex = (currentFocusIndex + 1) % elements.length;
            elements[currentFocusIndex].focus();
        },

        /**
         * Activates (clicks) the currently focused element
         */
        selectCurrentElement: () => {
            document.activeElement.click();
        },

        /**
         * Toggles automatic scanning of focusable elements
         * @returns {boolean} The new scanning state
         */
        toggleScanning: () => {
            scanning = !scanning;
            if (scanning) {
                scanInterval = setInterval(() => {
                    const elements = Array.from(document.querySelectorAll(focusableElements));
                    currentFocusIndex = (currentFocusIndex + 1) % elements.length;
                    elements[currentFocusIndex].focus();
                }, 2000);
            } else {
                clearInterval(scanInterval);
            }
            return scanning;
        }
    };
}; 