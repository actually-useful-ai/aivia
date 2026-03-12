/**
 * Chat display management utilities
 */

import { MessageManager } from './message-manager';

/**
 * Chat display management system
 */
export const ChatDisplayManager = {
    /**
     * Updates the chat display with new messages
     * @param {Array} chatHistory - Array of chat messages
     */
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

    /**
     * Adds a system message to the chat
     * @param {string} content - The message content
     */
    addSystemMessage(content) {
        const messagesList = document.getElementById("messages");
        if (messagesList) {
            MessageManager.createMessageItem(content, "system-message", messagesList);
            MessageManager.autoScroll();
        }
    },

    /**
     * Shows a toast notification
     * @param {string} message - The message to show
     * @param {number} duration - Duration in milliseconds
     */
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