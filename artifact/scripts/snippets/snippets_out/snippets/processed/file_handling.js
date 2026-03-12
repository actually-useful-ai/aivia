/**
 * File Handling and Clipboard Utilities
 * Consolidated from multiple files
 */

// Supported File Types
export const FileTypes = {
    supportedTypes: [
        // Image Formats
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
        'image/heic', 'image/heif', 'image/avif', 'image/tiff', 'image/bmp',
        'image/x-icon', 'image/vnd.microsoft.icon', 'image/svg+xml',
        'image/vnd.adobe.photoshop', 'image/x-adobe-dng', 'image/x-canon-cr2',
        'image/x-nikon-nef', 'image/x-sony-arw', 'image/x-fuji-raf',
        'image/x-olympus-orf', 'image/x-panasonic-rw2', 'image/x-rgb',
        'image/x-portable-pixmap', 'image/x-portable-graymap',
        'image/x-portable-bitmap',
        // Video Formats
        'video/mp4', 'video/quicktime', 'video/webm', 'video/x-msvideo',
        'video/x-flv', 'video/x-ms-wmv', 'video/x-matroska', 'video/3gpp',
        'video/x-m4v', 'video/x-ms-asf', 'video/x-mpegURL', 'video/x-ms-vob',
        'video/x-ms-tmp', 'video/x-mpeg', 'video/mp2t',
        // Generic
        'application/octet-stream'
    ],

    isSupported(fileType) {
        return this.supportedTypes.includes(fileType) || 
               fileType.startsWith('image/') || 
               fileType.startsWith('video/');
    },

    validateFile(file) {
        if (!file || (!file.type.startsWith('image/') && !file.type.startsWith('video/'))) {
            throw new Error('Unsupported file type');
        }
        if (file.size > 20 * 1024 * 1024) {
            throw new Error('File size exceeds limit');
        }
        if (!this.isSupported(file.type)) {
            throw new Error('Sorry, that file type confuses me.');
        }
        return true;
    }
};

// File Processing
export const FileProcessor = {
    async handleFileSelect(file) {
        if (!FileTypes.isSupported(file.type)) {
            throw new Error('Unsupported file type');
        }
        return await this.processFile(file);
    },

    async processFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsDataURL(file);
        });
    },

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

    handleFileOpen(file) {
        if (file.type === "text/html") {
            const url = URL.createObjectURL(file);
            window.open(url, "_blank");
            return true;
        }
        return false;
    }
};

// Clipboard Handler
export const ClipboardHandler = {
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.error("Copy failed:", err);
            throw new Error("Copy failed, try again");
        }
    },

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