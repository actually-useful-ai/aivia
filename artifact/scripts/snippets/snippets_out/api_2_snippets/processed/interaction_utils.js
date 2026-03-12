/**
 * Interaction Utilities
 * Consolidated from multiple files
 */

// UI State Management
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

// Drag and Drop Handler
export const DragDropHandler = {
    setupDragDrop(uploadArea, fileInput, handleFileSelect) {
        if (!uploadArea || !fileInput) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        // Handle dropped files
        uploadArea.addEventListener('drop', event => {
            const dt = event.dataTransfer;
            const files = dt.files;

            handleFiles(files);
        }, false);

        // Handle clicked files
        fileInput.addEventListener('change', event => {
            handleFiles(event.target.files);
        }, false);

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        function highlight(e) {
            uploadArea.classList.add('highlight');
        }

        function unhighlight(e) {
            uploadArea.classList.remove('highlight');
        }

        function handleFiles(files) {
            if (files && files[0]) {
                handleFileSelect(files[0]);
            }
        }
    }
};

// Button Manager
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

// Tray Manager
export const TrayManager = {
    setupTray(tray, settingsButton) {
        if (!tray || !settingsButton) return;

        let isOpen = false;

        const toggleTray = () => {
            isOpen = !isOpen;
            tray.classList.toggle('open', isOpen);
            settingsButton.setAttribute('aria-expanded', isOpen.toString());
            settingsButton.classList.toggle('active', isOpen);
        };

        // Toggle on button click
        settingsButton.addEventListener('click', (e) => {
            e.preventDefault();
            toggleTray();
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (isOpen && !tray.contains(e.target) && e.target !== settingsButton) {
                toggleTray();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (isOpen && e.key === 'Escape') {
                toggleTray();
            }
        });

        return {
            toggle: toggleTray,
            close: () => {
                if (isOpen) toggleTray();
            },
            open: () => {
                if (!isOpen) toggleTray();
            }
        };
    }
};

// Scroll Manager
export const ScrollManager = {
    setupScrollHandlers(container) {
        if (!container) return;

        // Auto-scroll on content change
        const autoScroll = () => {
            container.scrollTop = container.scrollHeight;
        };

        // Smooth scroll to bottom
        const smoothScrollToBottom = () => {
            container.scrollTo({
                top: container.scrollHeight,
                behavior: 'smooth'
            });
        };

        // Handle scroll events
        container.addEventListener('scroll', () => {
            if (container.scrollTop + container.clientHeight >= container.scrollHeight - 10) {
                // User has scrolled to bottom
                container.dataset.autoScroll = 'true';
            } else {
                // User has scrolled up
                container.dataset.autoScroll = 'false';
            }
        });

        return {
            autoScroll,
            smoothScrollToBottom,
            isAtBottom: () => container.dataset.autoScroll === 'true'
        };
    }
};

// Toast Notification Manager
export const ToastManager = {
    setupToast(containerId = 'toast', defaultDuration = 3000) {
        const toastElement = document.getElementById(containerId);
        if (!toastElement) return null;

        return {
            show: (message, duration = defaultDuration) => {
                toastElement.textContent = message;
                toastElement.classList.add('show');
                
                setTimeout(() => {
                    toastElement.classList.remove('show');
                }, duration);
            },
            hide: () => {
                toastElement.classList.remove('show');
            }
        };
    }
};

// Input Manager
export const InputManager = {
    setupInput(config) {
        const {
            input,
            submitButton,
            onSubmit,
            onKeyPress = true,
            clearOnSubmit = true,
            validation = (value) => value.trim() !== ''
        } = config;

        if (!input || !submitButton || !onSubmit) return;

        const handleSubmit = () => {
            const value = input.value;
            if (!validation(value)) return;

            onSubmit(value);
            if (clearOnSubmit) {
                input.value = '';
            }
        };

        submitButton.addEventListener('click', handleSubmit);

        if (onKeyPress) {
            input.addEventListener('keypress', (event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    handleSubmit();
                }
            });
        }

        return {
            clear: () => { input.value = ''; },
            getValue: () => input.value,
            setValue: (value) => { input.value = value; },
            focus: () => { input.focus(); }
        };
    }
};

// Stream Content Manager
export const StreamManager = {
    setupStream(config) {
        const {
            onDelta = () => {},
            onComplete = () => {},
            onError = console.error,
            decoder = new TextDecoder()
        } = config;

        return {
            async processStream(reader) {
                try {
                    while (true) {
                        const { value, done } = await reader.read();
                        if (done) break;

                        const chunk = decoder.decode(value, { stream: true });
                        const lines = chunk.split('\n');

                        for (const line of lines) {
                            if (line.startsWith('data:')) {
                                try {
                                    const data = JSON.parse(line.slice(5));
                                    if (data.type === 'delta') {
                                        onDelta(data);
                                    } else if (data.type === 'complete') {
                                        onComplete(data);
                                    }
                                } catch (error) {
                                    onError('Error parsing stream:', error);
                                }
                            }
                        }
                    }
                } catch (error) {
                    onError('Stream processing error:', error);
                }
            }
        };
    }
}; 