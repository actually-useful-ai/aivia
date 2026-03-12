/**
 * Image processing utilities
 */

/**
 * Resizes an image file to a specified maximum dimension while maintaining aspect ratio
 * @param {File} file - The image file to resize
 * @param {number} maxDimension - Maximum dimension (width or height) in pixels
 * @returns {Promise<string>} Base64 encoded image data
 */
export const resizeImage = async (file, maxDimension = 2048) => {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            let width = img.width;
            let height = img.height;
            
            if (width > height && width > maxDimension) {
                height = Math.round((height * maxDimension) / width);
                width = maxDimension;
            } else if (height > maxDimension) {
                width = Math.round((width * maxDimension) / height);
                height = maxDimension;
            }

            canvas.width = width;
            canvas.height = height;
            
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);
            
            const base64 = canvas.toDataURL('image/jpeg', 0.9);
            resolve(base64.split('base64,')[1]);
        };
        img.src = URL.createObjectURL(file);
    });
}; 