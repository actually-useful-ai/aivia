/**
 * Error Handling Utilities
 * Extracted from old_alt_scripts.js
 */

// Error Handler
export const ErrorHandler = {
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

    handleProcessingError(error, displayElement, uploadArea) {
        console.error("Error:", error);
        if (displayElement) {
            displayElement.textContent = "Processing failed. Please try again.";
        }
        if (uploadArea) {
            uploadArea.style.display = "flex";
        }
    },

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