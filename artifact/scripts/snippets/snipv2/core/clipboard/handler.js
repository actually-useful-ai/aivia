/**
 * Enhanced clipboard handling utilities
 */

import { FileTypes } from '../file/types';

/**
 * Enhanced clipboard handling utilities
 */
export const ClipboardHandler = {
    /**
     * Sets up clipboard handling for the application
     * @param {HTMLElement} pasteButton - The paste button element
     * @param {Function} processImageCallback - Callback to process pasted images
     */
    setupClipboardHandling(pasteButton, processImageCallback) {
        // Universal paste handler
        document.addEventListener('paste', async (e) => {
            e.preventDefault();
            
            const clipboardData = e.clipboardData || window.clipboardData;
            if (!clipboardData) {
                console.log('No clipboard data available');
                return;
            }

            // Handle pasted files
            const clipboardFiles = clipboardData.files;
            if (clipboardFiles?.length > 0) {
                for (const file of clipboardFiles) {
                    if (FileTypes.isSupported(file.type)) {
                        console.log('File found in clipboard:', file.type);
                        await processImageCallback(file);
                        return;
                    }
                }
            }

            // Handle clipboard items
            const items = clipboardData.items;
            if (items) {
                for (const item of items) {
                    if (FileTypes.isSupported(item.type)) {
                        const file = item.getAsFile();
                        if (file && FileTypes.isSupported(file.type)) {
                            await processImageCallback(file);
                            return;
                        }
                    }
                }
            }
        });

        // Platform-specific paste button handler
        if (pasteButton) {
            pasteButton.addEventListener('click', async () => {
                if (/Android/i.test(navigator.userAgent)) {
                    await this.handleAndroidPaste(processImageCallback);
                } else {
                    await this.handleDefaultPaste();
                }
            });
        }
    },

    /**
     * Handles paste operations on Android devices
     * @param {Function} processImageCallback - Callback to process pasted images
     */
    async handleAndroidPaste(processImageCallback) {
        try {
            if (navigator.clipboard && navigator.clipboard.read) {
                const clipboardItems = await navigator.clipboard.read();
                for (const item of clipboardItems) {
                    for (const type of item.types) {
                        if (type.startsWith('image/') || type.startsWith('video/')) {
                            const blob = await item.getType(type);
                            const fileExtension = type.split('/')[1];
                            const file = new File([blob], `pasted-file.${fileExtension}`, { type });
                            await processImageCallback(file);
                            return;
                        }
                    }
                }
                alert('No image or video found in clipboard.');
            } else {
                alert('Clipboard API not supported in this browser.');
            }
        } catch (e) {
            console.error('Error reading clipboard:', e);
            alert('Failed to read clipboard. Please ensure the app has clipboard permissions.');
        }
    },

    /**
     * Handles paste operations on non-Android devices
     */
    async handleDefaultPaste() {
        const tempTextArea = document.createElement('textarea');
        tempTextArea.style.cssText = 'opacity:0;position:absolute;left:-9999px;';
        document.body.appendChild(tempTextArea);
        tempTextArea.focus();

        try {
            await document.execCommand('paste');
        } catch (err) {
            console.error('Paste command failed:', err);
        } finally {
            document.body.removeChild(tempTextArea);
        }
    }
}; 