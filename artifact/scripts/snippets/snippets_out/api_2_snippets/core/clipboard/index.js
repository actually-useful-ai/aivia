/**
 * Clipboard utilities
 */

/**
 * Copies text to the clipboard
 * @param {string} text - The text to copy
 * @returns {Promise<boolean>} Whether the copy was successful
 */
export const copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (error) {
        console.error('Failed to copy text:', error);
        return false;
    }
}; 