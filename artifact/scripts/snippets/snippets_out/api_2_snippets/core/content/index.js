/**
 * Content processing utilities
 */

/**
 * Cleans up content by removing leading/trailing spaces, dashes, and "Alt text:" prefix
 * @param {string} content - The content to clean up
 * @returns {string} The cleaned content
 */
export const cleanupContent = (content) => {
    return content
        .replace(/^[\s-]+|[\s-]+$/g, '') // Remove leading/trailing spaces and dashes
        .replace(/^Alt text:\s*/i, ''); // Remove "Alt text:" prefix case-insensitive
}; 