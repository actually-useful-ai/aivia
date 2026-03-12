/**
 * Template Utilities
 */

export const TemplateUtils = {
    /**
     * Creates an element from a template string
     * @param {string} template - The template string
     * @returns {HTMLElement} The created element
     */
    createElement(template) {
        const div = document.createElement('div');
        div.innerHTML = template.trim();
        return div.firstChild;
    },

    /**
     * Injects a template into a container
     * @param {string|HTMLElement} container - The container element or selector
     * @param {string} template - The template string
     */
    inject(container, template) {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }
        if (container) {
            container.innerHTML = template;
        }
    },

    /**
     * Creates and appends an element to a container
     * @param {string|HTMLElement} container - The container element or selector
     * @param {string} template - The template string
     * @returns {HTMLElement|null} The created element or null
     */
    append(container, template) {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }
        if (container) {
            const element = this.createElement(template);
            container.appendChild(element);
            return element;
        }
        return null;
    }
}; 