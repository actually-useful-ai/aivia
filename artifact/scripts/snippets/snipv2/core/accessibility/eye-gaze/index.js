/**
 * Eye gaze utilities
 */

/**
 * Initializes eye gaze support
 * @param {number} dwellTime - Time in milliseconds before activation
 * @returns {Object} Eye gaze control functions
 */
export const initializeEyeGaze = (dwellTime = 1000) => {
    let dwellTimer;
    let lastElement;

    return {
        /**
         * Handles gaze events on elements
         * @param {HTMLElement} element - The element being gazed at
         */
        handleGaze: (element) => {
            if (element !== lastElement) {
                clearTimeout(dwellTimer);
                lastElement = element;

                if (element.matches('button, [role="button"]')) {
                    dwellTimer = setTimeout(() => {
                        element.click();
                        element.classList.add("dwell-activated");
                        setTimeout(() => element.classList.remove("dwell-activated"), 200);
                    }, dwellTime);
                }
            }
        }
    };
}; 