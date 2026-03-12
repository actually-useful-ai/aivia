/**
 * File handling utilities
 */

/**
 * File management system
 */
export const FileManager = {
    /**
     * Handles opening a file in a new window
     * @param {File} file - The file to open
     * @returns {boolean} Whether the file was handled
     */
    handleFileOpen(file) {
        if (file.type === "text/html") {
            const url = URL.createObjectURL(file);
            window.open(url, "_blank");
            return true;
        }
        return false;
    },

    /**
     * Sets up external links to open in new tabs
     */
    setupExternalLinks() {
        document.querySelectorAll('a[href^="http"]').forEach((link) => {
            link.setAttribute("target", "_blank");
            link.setAttribute("rel", "noopener noreferrer");
        });
    }
}; 