/**
 * Assistant Interface Management
 */

export const AssistantManager = {
    /**
     * Changes the current bot ID
     * @param {string} botId - The new bot ID
     * @param {boolean} isInitialLoad - Whether this is the initial load
     */
    changeBotId(botId, isInitialLoad = false) {
        const cleanBotId = botId.replace(/['"]/g, "");
        window.currentBotId = cleanBotId;

        document.querySelectorAll(".panel-button").forEach((button) => {
            const buttonBotId = button.getAttribute("data-bot-id");
            if (buttonBotId) {
                button.classList.toggle("active", buttonBotId === cleanBotId);
                button.setAttribute("aria-pressed", buttonBotId === cleanBotId);
            }
        });

        if (!isInitialLoad) {
            this.addSystemMessage("Switched to a new assistant.");
        }
    },

    /**
     * Adds a system message to the chat
     * @param {string} content - The message content
     */
    addSystemMessage(content) {
        const messagesList = document.getElementById("messages");
        if (messagesList) {
            const li = document.createElement("li");
            li.className = "message system-message";
            li.textContent = content;
            messagesList.appendChild(li);
            this.autoScroll();
        }
    },

    /**
     * Auto-scrolls the messages list to the bottom
     */
    autoScroll() {
        const messagesList = document.getElementById("messages");
        if (messagesList) {
            messagesList.scrollTop = messagesList.scrollHeight;
        }
    },

    /**
     * Updates the assistant info display
     * @param {Object} selectedBot - The selected bot data
     */
    updateAssistantInfo(selectedBot) {
        const assistantAvatar = document.querySelector(".assistant-avatar");
        if (selectedBot.avatar && assistantAvatar) {
            assistantAvatar.src = selectedBot.avatar;
            assistantAvatar.width = 30;
            assistantAvatar.height = 30;
        }

        const assistantName = document.getElementById("currentAssistantName");
        if (assistantName) {
            assistantName.textContent = selectedBot.name;
        }

        window.currentBotAvatar = selectedBot.avatar;
        window.currentBotName = selectedBot.name;
    }
}; 