/**
 * Message management utilities
 */

/**
 * Message management system
 */
export const MessageManager = {
    /**
     * Creates a message list item
     * @param {string} content - The message content
     * @param {string} type - The message type
     * @param {HTMLElement} messagesList - The messages list element
     * @returns {HTMLElement} The created message element
     */
    createMessageItem(content, type, messagesList) {
        const li = document.createElement("li");
        li.className = `message ${type}`;
        li.innerHTML = this.processMessageContent(content);
        messagesList.appendChild(li);
        return li;
    },

    /**
     * Creates a message element with proper ARIA attributes
     * @param {string} content - The message content
     * @param {string} type - The message type
     * @returns {HTMLElement} The created message container
     */
    createMessageElement(content, type) {
        const container = document.createElement('div');
        container.className = `message-container ${type}-container`;
        container.setAttribute('role', 'listitem');

        const message = document.createElement('div');
        message.className = `message ${type}`;
        message.innerHTML = content;

        if (type === 'bot') {
            message.setAttribute('aria-label', 'Assistant message');
        } else {
            message.setAttribute('aria-label', 'Your message');
        }

        container.appendChild(message);
        return container;
    },

    /**
     * Processes message content for display
     * @param {string|Object} content - The content to process
     * @returns {string} The processed content
     */
    processMessageContent(content) {
        // Process markdown, links, code blocks, etc.
        return typeof content === 'string' ? content : JSON.stringify(content);
    },

    /**
     * Scrolls the messages list to the bottom
     */
    autoScroll() {
        const messagesList = document.getElementById("messages");
        if (messagesList) {
            messagesList.scrollTop = messagesList.scrollHeight;
        }
    }
}; 