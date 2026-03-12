/**
 * Progress bar utilities
 */

/**
 * Progress bar management system
 */
export const ProgressManager = {
    progressInterval: null,

    /**
     * Starts the progress bar animation
     * @param {HTMLElement} progressBar - The progress bar element
     * @param {number} maxProgress - Maximum progress value
     * @param {number} increment - Progress increment per interval
     * @param {number} interval - Interval duration in milliseconds
     */
    startProgress(progressBar, maxProgress = 90, increment = 1, interval = 300) {
        let progress = 0;
        progressBar.style.width = "0%";
        
        this.progressInterval = setInterval(() => {
            if (progress < maxProgress) {
                progress += increment;
                progressBar.style.width = `${progress}%`;
            }
        }, interval);
    },

    /**
     * Stops and resets the progress bar
     * @param {HTMLElement} progressBar - The progress bar element
     */
    stopProgress(progressBar) {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        if (progressBar) {
            progressBar.style.width = "0%";
        }
    },

    /**
     * Sets the progress bar to a specific value
     * @param {HTMLElement} progressBar - The progress bar element
     * @param {number} progress - Progress value
     */
    setProgress(progressBar, progress) {
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    },

    /**
     * Simulates streaming progress animation
     * @param {HTMLElement} progressBar - The progress bar element
     * @param {number} startProgress - Starting progress value
     * @param {number} maxProgress - Maximum progress value
     * @param {number} increment - Progress increment per interval
     * @param {number} interval - Interval duration in milliseconds
     * @returns {Promise<void>} Resolves when animation completes
     */
    async simulateStreamProgress(progressBar, startProgress = 40, maxProgress = 95, increment = 0.8, interval = 300) {
        let currentProgress = startProgress;
        return new Promise((resolve) => {
            const streamInterval = setInterval(() => {
                if (currentProgress < maxProgress) {
                    currentProgress += increment;
                    this.setProgress(progressBar, currentProgress);
                } else {
                    clearInterval(streamInterval);
                    resolve();
                }
            }, interval);
        });
    }
}; 