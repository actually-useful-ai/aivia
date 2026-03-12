/**
 * URL utilities
 */

/**
 * Creates a cache-busted URL for a file
 * @param {File} file - The file to create a URL for
 * @returns {string} The cache-busted URL
 */
export const createCacheBustedUrl = (file) => {
    return URL.createObjectURL(file) + '#' + new Date().getTime();
};

/**
 * Revokes a cache-busted URL
 * @param {string} url - The URL to revoke
 */
export const revokeCacheBustedUrl = (url) => {
    URL.revokeObjectURL(url.split('#')[0]);
}; 