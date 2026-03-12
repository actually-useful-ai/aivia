/**
 * API configuration utilities
 */

/**
 * API configuration
 */
export const API_CONFIG = {
    /**
     * Gets the base URL for API calls based on environment
     * @returns {string} The base URL for API calls
     */
    getBaseUrl() {
        return window.location.hostname === "localhost"
            ? "http://localhost:5002"
            : "https://api.assisted.space";
    }
}; 