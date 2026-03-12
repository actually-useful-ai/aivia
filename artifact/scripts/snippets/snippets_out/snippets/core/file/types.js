/**
 * File type utilities
 */

/**
 * Supported file types configuration
 */
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

    /**
     * Checks if a file type is supported
     * @param {string} fileType - The MIME type to check
     * @returns {boolean} Whether the file type is supported
     */
    isSupported(fileType) {
        return this.supportedTypes.includes(fileType) || 
               fileType.startsWith('image/') || 
               fileType.startsWith('video/');
    },

    /**
     * Validates a file against supported types and size limits
     * @param {File} file - The file to validate
     * @returns {boolean} True if the file is valid
     * @throws {Error} If the file is invalid
     */
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