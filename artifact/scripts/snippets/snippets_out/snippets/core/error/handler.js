/**
 * Error Handling
 */

export const ErrorHandler = {
    /**
     * Wraps a promise with timeout and retry logic
     * @param {Promise} promise - The promise to wrap
     * @param {number} ms - Timeout in milliseconds
     * @param {number} maxAttempts - Maximum number of retry attempts
     * @returns {Promise} The wrapped promise
     */
    async timeoutPromise(promise, ms = 60000, maxAttempts = 3) {
        let attempts = 0;

        while (attempts < maxAttempts) {
            try {
                return await Promise.race([
                    promise,
                    new Promise((_, reject) =>
                        setTimeout(() => reject(new Error("Timeout occurred")), ms)
                    ),
                ]);
            } catch (error) {
                attempts++;
                if (attempts === maxAttempts) {
                    throw error;
                }
                // Exponential backoff before retrying
                await new Promise((resolve) =>
                    setTimeout(resolve, 1000 * Math.pow(2, attempts))
                );
                console.log(`Retry attempt ${attempts} of ${maxAttempts}`);
            }
        }
    },

    /**
     * Handles processing errors
     * @param {Error} error - The error object
     * @param {HTMLElement} displayElement - Element to display error
     * @param {HTMLElement} uploadArea - Upload area element
     */
    handleProcessingError(error, displayElement, uploadArea) {
        console.error("Error:", error);
        if (displayElement) {
            displayElement.textContent = "Processing failed. Please try again.";
        }
        if (uploadArea) {
            uploadArea.style.display = "flex";
        }
    },

    /**
     * Wraps an operation with error handling
     * @param {Function} operation - The operation to wrap
     * @param {Object} options - Error handling options
     * @param {HTMLElement} options.displayElement - Element to display error
     * @param {HTMLElement} options.uploadArea - Upload area element
     * @param {Function} options.cleanup - Cleanup function
     * @param {string} options.errorMessage - Custom error message
     * @returns {Promise<void>}
     */
    async withErrorHandling(operation, {
        displayElement = null,
        uploadArea = null,
        cleanup = null,
        errorMessage = "Processing failed after multiple attempts. Please try again."
    } = {}) {
        try {
            await operation();
        } catch (error) {
            console.error("Operation failed:", error);
            if (cleanup) {
                await cleanup();
            }
            if (displayElement) {
                displayElement.textContent = `${errorMessage} Error: ${error.message}`;
            }
            if (uploadArea) {
                uploadArea.style.display = "flex";
            }
            throw error;
        }
    }
}; 