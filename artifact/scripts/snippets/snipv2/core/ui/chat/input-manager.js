/**
 * Input management utilities
 */

/**
 * Input management system
 */
export const InputManager = {
    /**
     * Sets up event listeners for the input container
     * @param {HTMLElement} messageInput - The message input element
     * @param {HTMLElement} sendButton - The send button element
     * @param {Function} sendMessageCallback - Callback to handle message sending
     */
    setupEventListeners(messageInput, sendButton, sendMessageCallback) {
        messageInput.addEventListener("keypress", (event) => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessageCallback();
            }
        });

        sendButton.addEventListener("click", (event) => {
            event.preventDefault();
            sendMessageCallback();
        });

        // Auto-resize textarea
        messageInput.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = messageInput.scrollHeight + 'px';
        });
    },

    /**
     * Updates the input container geometry based on panel states
     * @param {HTMLElement} inputContainer - The input container element
     * @param {HTMLElement} leftPanel - The left panel element
     * @param {HTMLElement} rightPanel - The right panel element
     */
    updateInputContainerGeometry(inputContainer, leftPanel, rightPanel) {
        const rightWidth = rightPanel && rightPanel.classList.contains("open") 
            ? rightPanel.offsetWidth 
            : 0;

        const leftWidth = leftPanel && !leftPanel.classList.contains("closed")
            ? leftPanel.offsetWidth
            : 0;

        requestAnimationFrame(() => {
            if (inputContainer) {
                inputContainer.style.width = `calc(100% - ${leftWidth}px - ${rightWidth}px)`;
                inputContainer.style.right = `${rightWidth}px`;
                inputContainer.style.left = `${leftWidth}px`;
            }
        });
    }
}; 