/**
 * Session and History Management
 * Extracted from from_main.js
 */

// Session Management
export const SessionManager = {
    SESSION_STORAGE_KEY: "chat_session",
    CHAT_HISTORY_KEY: "chatHistory",

    saveSession(messages, currentAssistant) {
        const sessionData = {
            messages,
            currentAssistant,
            timestamp: Date.now()
        };
        localStorage.setItem(this.SESSION_STORAGE_KEY, JSON.stringify(sessionData));
    },

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

// Chat History Management
export const ChatHistoryManager = {
    CHAT_HISTORY_KEY: "chatHistory",

    saveChatHistory(messages) {
        localStorage.setItem(this.CHAT_HISTORY_KEY, JSON.stringify(messages));
    },

    loadChatHistory() {
        const saved = localStorage.getItem(this.CHAT_HISTORY_KEY);
        return saved ? JSON.parse(saved) : [];
    },

    clearChatHistory() {
        localStorage.removeItem(this.CHAT_HISTORY_KEY);
        return [];
    },

    initializeChatHistory() {
        window.chatHistory = this.loadChatHistory();
        return window.chatHistory;
    }
};

// File Handling
export const FileManager = {
    handleFileOpen(file) {
        if (file.type === "text/html") {
            const url = URL.createObjectURL(file);
            window.open(url, "_blank");
            return true;
        }
        return false;
    },

    setupExternalLinks() {
        document.querySelectorAll('a[href^="http"]').forEach((link) => {
            link.setAttribute("target", "_blank");
            link.setAttribute("rel", "noopener noreferrer");
        });
    }
};

// State Management
export const StateManager = {
    createInitialState() {
        return {
            API_BASE_URL: "https://api.assisted.space",
            currentBotId: "7418144401408753670",
            conversationId: null,
            isFirstMessage: true,
            md: null,
            loadedCategories: new Set(),
            selectedBotId: "7439617637233016888",
        };
    },

    initializeState() {
        const state = this.createInitialState();
        
        if (!state.md) {
            state.md = window.md; // Assuming markdown initialization is handled elsewhere
        }

        return state;
    }
}; 