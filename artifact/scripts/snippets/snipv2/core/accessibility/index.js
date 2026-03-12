/**
 * Accessibility utilities index
 */

// Display mode utilities
export * from './display';

// Font utilities
export * from './font';

// Speech utilities
export * from './speech';

// Switch control utilities
export * from './switch';

// Eye gaze utilities
export * from './eye-gaze';

/**
 * Sets up ARIA landmarks and keyboard accessibility
 * @returns {HTMLElement} The screen reader announcer element
 */
export const setupAccessibilityFeatures = () => {
    // Set up ARIA landmarks
    document.querySelectorAll('[role="region"]').forEach(region => {
        if (!region.hasAttribute('aria-label')) {
            region.setAttribute('aria-label', region.id || 'Content region');
        }
    });

    // Ensure all interactive elements are keyboard accessible
    document.querySelectorAll('button, a, [role="button"]').forEach(element => {
        if (!element.hasAttribute('tabindex')) {
            element.setAttribute('tabindex', '0');
        }
    });

    // Add screen reader announcements for dynamic content
    const announcer = document.createElement('div');
    announcer.setAttribute('aria-live', 'polite');
    announcer.setAttribute('aria-atomic', 'true');
    announcer.className = 'sr-only';
    document.body.appendChild(announcer);

    return announcer;
}; 