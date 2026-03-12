/**
 * State management utilities
 */

/**
 * State management system
 */
export const StateManager = {
    /**
     * Creates the initial application state
     * @returns {Object} The initial state object
     */
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

    /**
     * Initializes the application state
     * @returns {Object} The initialized state
     */
    initializeState() {
        const state = this.createInitialState();
        
        if (!state.md) {
            state.md = window.md; // Assuming markdown initialization is handled elsewhere
        }

        return state;
    }
}; 