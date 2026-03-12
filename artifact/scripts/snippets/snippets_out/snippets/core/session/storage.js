/**
 * Session storage utilities
 */

/**
 * Session management system
 */
export const SessionManager = {
    SESSION_STORAGE_KEY: "chat_session",
    CHAT_HISTORY_KEY: "chatHistory",

    /**
     * Saves the current session state
     * @param {Array} messages - Current messages
     * @param {Object} currentAssistant - Current assistant configuration
     */
    saveSession(messages, currentAssistant) {
        const sessionData = {
            messages,
            currentAssistant,
            timestamp: Date.now()
        };
        localStorage.setItem(this.SESSION_STORAGE_KEY, JSON.stringify(sessionData));
    },

    /**
     * Loads the saved session state
     * @returns {Object|null} The saved session data or null if invalid/expired
     */
    loadSession() {
        const savedSession = localStorage.getItem(this.SESSION_STORAGE_KEY);
        if (savedSession) {
            const { messages, currentAssistant, timestamp } = JSON.parse(savedSession);
            // Only restore if session is less than 24 hours old
            if (Date.now() - timestamp < 24 * 60 * 60 * 1000) {
                return { messages, currentAssistant };
            }
        }
        return null;
    }
};

/**
 * Chat history management system
 */
export const ChatHistoryManager = {
    CHAT_HISTORY_KEY: "chatHistory",

    /**
     * Saves the chat history
     * @param {Array} messages - Messages to save
     */
    saveChatHistory(messages) {
        localStorage.setItem(this.CHAT_HISTORY_KEY, JSON.stringify(messages));
    },

    /**
     * Loads the saved chat history
     * @returns {Array} The saved chat history or empty array
     */
    loadChatHistory() {
        const saved = localStorage.getItem(this.CHAT_HISTORY_KEY);
        return saved ? JSON.parse(saved) : [];
    },

    /**
     * Clears the chat history
     * @returns {Array} Empty array
     */
    clearChatHistory() {
        localStorage.removeItem(this.CHAT_HISTORY_KEY);
        return [];
    },

    /**
     * Initializes chat history in window object
     * @returns {Array} The initialized chat history
     */
    initializeChatHistory() {
        window.chatHistory = this.loadChatHistory();
        return window.chatHistory;
    }
}; 