/**
 * Chat UI Components and Utilities
 * Consolidated from chat_components.js and chat-ui.js
 */

// Message Creation and Management
export const MessageManager = {
    createMessageItem(content, type, messagesList) {
        const li = document.createElement("li");
        li.className = `message ${type}`;
        li.innerHTML = this.processMessageContent(content);
        messagesList.appendChild(li);
        return li;
    },

    createMessageElement(content, type) {
        const container = document.createElement('div');
        container.className = `message-container ${type}-container`;
        container.setAttribute('role', 'listitem');

        const message = document.createElement('div');
        message.className = `message ${type}`;
        message.innerHTML = content;

        if (type === 'bot') {
            message.setAttribute('aria-label', 'Assistant message');
        } else {
            message.setAttribute('aria-label', 'Your message');
        }

        container.appendChild(message);
        return container;
    },

    processMessageContent(content) {
        // Process markdown, links, code blocks, etc.
        return typeof content === 'string' ? content : JSON.stringify(content);
    },

    autoScroll() {
        const messagesList = document.getElementById("messages");
        if (messagesList) {
            messagesList.scrollTop = messagesList.scrollHeight;
        }
    }
};

// Input Container Management
export const InputManager = {
    setupEventListeners(messageInput, sendButton, sendMessageCallback) {
        messageInput.addEventListener("keypress", (event) => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessageCallback();
            }
        });

        sendButton.addEventListener("click", (event) => {
            event.preventDefault();
            sendMessageCallback();
        });

        // Auto-resize textarea
        messageInput.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = messageInput.scrollHeight + 'px';
        });
    },

    updateInputContainerGeometry(inputContainer, leftPanel, rightPanel) {
        const rightWidth = rightPanel && rightPanel.classList.contains("open") 
            ? rightPanel.offsetWidth 
            : 0;

        const leftWidth = leftPanel && !leftPanel.classList.contains("closed")
            ? leftPanel.offsetWidth
            : 0;

        requestAnimationFrame(() => {
            if (inputContainer) {
                inputContainer.style.width = `calc(100% - ${leftWidth}px - ${rightWidth}px)`;
                inputContainer.style.right = `${rightWidth}px`;
                inputContainer.style.left = `${leftWidth}px`;
            }
        });
    }
};

// Mobile Responsiveness
export const MobileHandler = {
    handleMobilePanel(panelId, sidePanelsContainer, inputContainer) {
        if (window.innerWidth <= 768) {
            // For mobile
            sidePanelsContainer.classList.toggle("active");
            if (sidePanelsContainer.classList.contains("active")) {
                inputContainer.style.display = "flex";
            } else {
                setTimeout(() => {
                    inputContainer.style.display = "flex";
                }, 300); // Match the transition duration
            }
        } else {
            // For desktop
            this.openPanel(panelId);
        }
    },

    setupMediaQuery() {
        const mediaQuery = window.matchMedia("(max-width: 1050px)");
        mediaQuery.addListener(this.handleMediaQueryChange);
        this.handleMediaQueryChange(mediaQuery);
    }
};

// Chat Display Updates
export const ChatDisplayManager = {
    updateChatDisplay(chatHistory = []) {
        const messagesList = document.getElementById("messages");
        if (!messagesList) return;

        messagesList.innerHTML = "";
        
        if (Array.isArray(chatHistory)) {
            chatHistory.forEach((message) => {
                MessageManager.createMessageItem(
                    message.content, 
                    message.type, 
                    messagesList
                );
            });
        }

        MessageManager.autoScroll();
    },

    addSystemMessage(content) {
        const messagesList = document.getElementById("messages");
        if (messagesList) {
            MessageManager.createMessageItem(content, "system-message", messagesList);
            MessageManager.autoScroll();
        }
    },

    showToast(message, duration = 3000) {
        const toast = document.getElementById('toast');
        if (!toast) return;

        toast.textContent = message;
        toast.setAttribute('aria-hidden', 'false');
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
            toast.setAttribute('aria-hidden', 'true');
        }, duration);
    }
}; 