/**
 * Button Management
 */

export const ButtonManager = {
    setupButtons(config) {
        const {
            pasteButton,
            restartButton,
            copyButton,
            settingsButton,
            ttsButton,
            handlers
        } = config;

        // Paste button
        if (pasteButton && handlers.paste) {
            pasteButton.addEventListener('click', handlers.paste);
        }

        // Restart button
        if (restartButton && handlers.restart) {
            restartButton.addEventListener('click', handlers.restart);
        }

        // Copy button
        if (copyButton && handlers.copy) {
            copyButton.addEventListener('click', handlers.copy);
        }

        // Settings button
        if (settingsButton && handlers.settings) {
            settingsButton.addEventListener('click', handlers.settings);
        }

        // TTS button
        if (ttsButton && handlers.tts) {
            ttsButton.addEventListener('click', handlers.tts);
        }
    },

    updateButtonState(button, isLoading, loadingText = 'Processing...', originalHtml = '') {
        if (isLoading) {
            button.classList.add('loading');
            button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
            button.disabled = true;
        } else {
            button.classList.remove('loading');
            button.innerHTML = originalHtml;
            button.disabled = false;
        }
    }
}; 