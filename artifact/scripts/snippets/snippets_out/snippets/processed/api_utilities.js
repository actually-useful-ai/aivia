/**
 * API and Message Utilities
 * Extracted from old_alt_scripts.js
 */

// API Configuration
export const API_CONFIG = {
    getBaseUrl() {
        return window.location.hostname === "localhost"
            ? "http://localhost:5002"
            : "https://api.assisted.space";
    }
};

// Message Rotation System
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

    rotateMessage(messageElement) {
        if (!messageElement) return;
        
        this.currentIndex = (this.currentIndex + 1) % this.messages.length;
        messageElement.style.opacity = "0";
        setTimeout(() => {
            messageElement.textContent = this.messages[this.currentIndex];
            messageElement.style.opacity = "1";
        }, 200);
    },

    startRotation(messageElement, interval = 5000) {
        if (!messageElement) return;
        
        messageElement.textContent = this.messages[0];
        return setInterval(() => this.rotateMessage(messageElement), interval);
    }
};

// Image Counter Utility
export const ImageCounter = {
    async fetchCount() {
        try {
            const response = await fetch(`${API_CONFIG.getBaseUrl()}/image_counter`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                }
            });
            const data = await response.json();
            return data.count;
        } catch (error) {
            console.error("Error fetching image count:", error);
            return null;
        }
    },

    async updateDisplayCount(messageElement) {
        const count = await this.fetchCount();
        if (count !== null && messageElement) {
            MessageRotator.messages[0] = `Images Processed: ${count.toLocaleString()}!`;
            if (messageElement.textContent === "Loading count...") {
                messageElement.textContent = MessageRotator.messages[0];
            }
        }
    }
}; 