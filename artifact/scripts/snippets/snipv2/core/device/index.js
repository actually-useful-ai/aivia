/**
 * Device detection utilities
 */

/**
 * Checks if the current device is a mobile device
 * @returns {boolean} True if the device is mobile
 */
export const isMobile = () => /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

/**
 * Checks if the current device is an Android device
 * @returns {boolean} True if the device is Android
 */
export const isAndroid = () => /Android/i.test(navigator.userAgent); 