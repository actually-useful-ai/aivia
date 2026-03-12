/**
 * Animation utilities
 */

/**
 * Pull to refresh threshold in pixels
 */
export const PULL_REFRESH_THRESHOLD = 80;

/**
 * Creates a span element for streaming character animation
 * @param {string} char - The character to animate
 * @returns {HTMLSpanElement} The created span element
 */
export const createStreamingCharSpan = (char) => {
    const span = document.createElement('span');
    span.textContent = char;
    span.className = 'streaming-char';
    return span;
}; 