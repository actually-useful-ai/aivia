/**
 * UI Utilities
 * Extracted from old_alt_scripts.js
 */

// UI State Management
export const UIStateManager = {
    toggleProcessingState(pasteButton, restartButton, isProcessing) {
        if (isProcessing) {
            pasteButton.classList.add('hidden');
            restartButton.classList.remove('hidden');
        } else {
            pasteButton.classList.remove('hidden');
            restartButton.classList.add('hidden');
        }
    },

    initializeScrollHandler(element) {
        if (!element) return;
        
        element.addEventListener("scroll", () => {
            if (element.scrollTop + element.clientHeight >= element.scrollHeight) {
                window.scrollBy({
                    top: 100,
                    behavior: "smooth"
                });
            }
        });
    }
};

// Processing State Management
export const ProcessingManager = {
    startProcessing(document) {
        document.body.classList.add("processing");
    },

    processingComplete() {
        console.log("Processing complete.");
    },

    restart() {
        window.location.reload();
    }
};

// Page Lifecycle Management
export const PageLifecycle = {
    initialize(altTextGenerator) {
        document.addEventListener("DOMContentLoaded", () => {
            console.log("DOM loaded, initializing");
            const altTextDisplay = document.querySelector(".alt-text-display");
            if (altTextDisplay) {
                UIStateManager.initializeScrollHandler(altTextDisplay);
            }
        });

        window.addEventListener("beforeunload", () => {
            console.log("Page unloading, cleaning up");
            if (altTextGenerator && altTextGenerator.nukeIt) {
                altTextGenerator.nukeIt();
            }
        });
    }
}; 