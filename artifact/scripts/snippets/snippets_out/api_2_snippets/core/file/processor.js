/**
 * File processing utilities
 */

import { FileTypes } from './types';

/**
 * File processing utilities
 */
export const FileProcessor = {
    /**
     * Handles file selection and validation
     * @param {File} file - The file to handle
     * @returns {Promise<string>} The processed file data
     */
    async handleFileSelect(file) {
        if (!FileTypes.isSupported(file.type)) {
            throw new Error('Unsupported file type');
        }
        return await this.processFile(file);
    },

    /**
     * Processes a file into a data URL
     * @param {File} file - The file to process
     * @returns {Promise<string>} The data URL
     */
    async processFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsDataURL(file);
        });
    },

    /**
     * Creates an HTML embed element for a file
     * @param {File} file - The file to embed
     * @param {string} fileUrl - The URL of the file
     * @returns {HTMLElement} The embed container element
     */
    createFileEmbed(file, fileUrl) {
        const container = document.createElement('div');
        container.className = 'file-embed';

        if (file.type.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = fileUrl;
            img.alt = file.name;
            container.appendChild(img);
        } else if (file.type.startsWith('video/')) {
            const video = document.createElement('video');
            video.src = fileUrl;
            video.controls = true;
            container.appendChild(video);
        }

        return container;
    },

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
    }
}; 