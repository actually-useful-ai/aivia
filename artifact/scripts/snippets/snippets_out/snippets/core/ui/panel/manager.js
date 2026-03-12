/**
 * Panel State Management
 */

export const PanelManager = {
    activePanelId: null,
    isPanelOpen: false,

    /**
     * Closes all panels
     * @param {Array<HTMLElement>} panels - Array of panel elements
     * @param {Array<HTMLElement>} toggleButtons - Array of toggle button elements
     * @param {HTMLElement} panelToggles - Panel toggles container element
     * @param {HTMLElement} sidePanelsContainer - Side panels container element
     * @param {HTMLElement} chatContainer - Chat container element
     * @param {HTMLElement} inputContainer - Input container element
     */
    closeAllPanels(panels, toggleButtons, panelToggles, sidePanelsContainer, chatContainer, inputContainer) {
        panels.forEach((panel) => panel.classList.remove("active"));
        toggleButtons.forEach((btn) => {
            btn.classList.remove("active");
            btn.setAttribute("aria-pressed", "false");
        });
        
        panelToggles.classList.add("closed");
        sidePanelsContainer.classList.add("closed");
        chatContainer.classList.add("panel-closed");
        inputContainer.classList.remove("left-panel-open", "right-panel-open");

        this.isPanelOpen = false;
    },

    /**
     * Opens a specific panel
     * @param {string} panelId - ID of the panel to open
     * @param {Array<HTMLElement>} panels - Array of panel elements
     * @param {Array<HTMLElement>} toggleButtons - Array of toggle button elements
     * @param {HTMLElement} panelToggles - Panel toggles container element
     * @param {HTMLElement} sidePanelsContainer - Side panels container element
     * @param {HTMLElement} chatContainer - Chat container element
     * @param {HTMLElement} inputContainer - Input container element
     */
    openPanel(panelId, panels, toggleButtons, panelToggles, sidePanelsContainer, chatContainer, inputContainer) {
        this.closeAllPanels(panels, toggleButtons, panelToggles, sidePanelsContainer, chatContainer, inputContainer);
        
        const panel = document.getElementById(panelId + "Panel");
        const button = document.querySelector(`[data-panel="${panelId}"]`);

        panel.classList.add("active");
        button.classList.add("active");
        button.setAttribute("aria-pressed", "true");
        panelToggles.classList.remove("closed");
        sidePanelsContainer.classList.remove("closed");
        chatContainer.classList.remove("panel-closed");

        if (["assistants", "help", "settings"].includes(panelId)) {
            inputContainer.classList.add("left-panel-open");
        }

        this.activePanelId = panelId + "Panel";
        this.isPanelOpen = true;
    },

    /**
     * Handles toggle button click
     * @param {Event} event - The click event
     * @param {Array<HTMLElement>} panels - Array of panel elements
     * @param {Array<HTMLElement>} toggleButtons - Array of toggle button elements
     * @param {HTMLElement} panelToggles - Panel toggles container element
     * @param {HTMLElement} sidePanelsContainer - Side panels container element
     * @param {HTMLElement} chatContainer - Chat container element
     * @param {HTMLElement} inputContainer - Input container element
     */
    handleToggleButton(event, panels, toggleButtons, panelToggles, sidePanelsContainer, chatContainer, inputContainer) {
        event.preventDefault();
        const panelId = event.currentTarget.getAttribute("data-panel");
        
        if (this.isPanelOpen && this.activePanelId === panelId + "Panel") {
            this.closeAllPanels(panels, toggleButtons, panelToggles, sidePanelsContainer, chatContainer, inputContainer);
        } else {
            this.openPanel(panelId, panels, toggleButtons, panelToggles, sidePanelsContainer, chatContainer, inputContainer);
        }
    }
}; 