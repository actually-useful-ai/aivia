/**
 * UI State Management
 */

export const UIStateManager = {
    // Initialize UI state
    initializeState() {
        return {
            isProcessing: false,
            isUploading: false,
            isPanelOpened: false,
            currentFileId: null,
            pendingFiles: [],
            debounceTimeout: null
        };
    },

    // Toggle processing state
    toggleProcessingState(pasteButton, restartButton, isProcessing) {
        if (isProcessing) {
            pasteButton.classList.add('hidden');
            restartButton.classList.remove('hidden');
        } else {
            pasteButton.classList.remove('hidden');
            restartButton.classList.add('hidden');
        }
    },

    // Reset UI state
    resetUIState(elements) {
        // Reset containers
        if (elements.resultContainer) {
            elements.resultContainer.style.display = "none";
        }
        if (elements.uploadArea) {
            elements.uploadArea.style.display = "flex";
        }
        if (elements.copyButton) {
            elements.copyButton.style.display = "none";
        }

        // Reset progress
        if (elements.progressBar) {
            elements.progressBar.style.width = "0%";
        }

        // Reset messages
        if (elements.altTextDisplay) {
            elements.altTextDisplay.textContent = "";
        }

        // Reset buttons
        this.toggleProcessingState(
            elements.pasteButton,
            elements.restartButton,
            false
        );
    }
}; 