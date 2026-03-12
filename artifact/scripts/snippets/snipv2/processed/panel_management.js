/**
 * Panel Management Utilities
 * Extracted from from_main.js
 */

// Panel State Management
export const PanelManager = {
    activePanelId: null,
    isPanelOpen: false,

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

// Panel Logo Management
export const PanelLogoManager = {
    addPanelLogo(logoUrl = "https://i.imgur.com/aSNdzIx.gif") {
        const sidePanel = document.querySelector(".right-panel-container");
        if (!sidePanel) {
            console.error("Side panel container not found.");
            return;
        }

        let logo = document.querySelector(".side-panel-logo");
        if (!logo) {
            logo = document.createElement("img");
            logo.src = logoUrl;
            logo.className = "side-panel-logo";
            logo.alt = "Panel Logo";
            logo.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 120px;
                height: 120px;
                opacity: 0.5;
                z-index: 1;
            `;
            sidePanel.appendChild(logo);
        }

        // Show logo when panel is empty
        const observer = new MutationObserver(() => {
            const panelContent = sidePanel.querySelector(".panel-content");
            const isEmpty = !panelContent || !panelContent.children.length;
            logo.style.display = isEmpty ? "block" : "none";
        });

        observer.observe(sidePanel, {
            childList: true,
            subtree: true,
        });

        // Initial state
        const panelContent = sidePanel.querySelector(".panel-content");
        const isEmpty = !panelContent || !panelContent.children.length;
        logo.style.display = isEmpty ? "block" : "none";
    }
};

// Panel Mutation Observer
export const PanelObserver = {
    setupMutationObservers(leftPanelContainer, updateCallback) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === "class") {
                    requestAnimationFrame(updateCallback);
                }
            });
        });

        observer.observe(leftPanelContainer, {
            attributes: true,
        });

        return observer;
    }
}; 