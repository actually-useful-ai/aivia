/**
 * Message rotation utilities
 */

/**
 * Message rotation system
 */
export const MessageRotator = {
    messages: [
        "Loading count...",
        "Back from the dead!",
        "Multiple languages!",
        "Try the text to speech!",
        "No image training!",
        "Adjust length!",
        "See the ? button!",
        "This isn't a chatbot!",
        "Stores absolutely nothing!",
        "Try Enhance!",
        "Support this project below!",
        "Try the interpreters!",
        "Free to use!",
        "I don't make images!",
        "Source code below!",
        "Streaming text to speech!",
        "Privacy first!",
        "Analyze art styles!",
        "Switch controls!",
        "Interpret context!",
        "Read emotions and moods!",
        "Copy to nuke all records!",
        "Supports 10+ languages!",
        "Drag and drop enabled!",
        "Keyboard controls!",
        "Real-time processing!",
        "Encrypted API calls!",
        "Mobile-friendly interface!",
        "No account needed!",
        "Give me your money!",
        "Why are you still watching this?"
    ],
    currentIndex: 0,

    /**
     * Rotates to the next message
     * @param {HTMLElement} messageElement - The element to update
     */
    rotateMessage(messageElement) {
        if (!messageElement) return;
        
        this.currentIndex = (this.currentIndex + 1) % this.messages.length;
        messageElement.style.opacity = "0";
        setTimeout(() => {
            messageElement.textContent = this.messages[this.currentIndex];
            messageElement.style.opacity = "1";
        }, 200);
    },

    /**
     * Starts the message rotation
     * @param {HTMLElement} messageElement - The element to update
     * @param {number} interval - The rotation interval in milliseconds
     * @returns {number} The interval ID
     */
    startRotation(messageElement, interval = 5000) {
        if (!messageElement) return;
        
        messageElement.textContent = this.messages[0];
        return setInterval(() => this.rotateMessage(messageElement), interval);
    }
}; 