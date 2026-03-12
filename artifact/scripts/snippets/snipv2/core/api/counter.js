/**
 * Image counter utilities
 */

import { API_CONFIG } from './config';
import { MessageRotator } from '../ui/message-rotator';

/**
 * Image counter system
 */
export const ImageCounter = {
    /**
     * Fetches the current image count from the API
     * @returns {Promise<number|null>} The current count or null if failed
     */
    async fetchCount() {
        try {
            const response = await fetch(`${API_CONFIG.getBaseUrl()}/image_counter`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                }
            });
            const data = await response.json();
            return data.count;
        } catch (error) {
            console.error("Error fetching image count:", error);
            return null;
        }
    },

    /**
     * Updates the display with the current count
     * @param {HTMLElement} messageElement - The element to update
     */
    async updateDisplayCount(messageElement) {
        const count = await this.fetchCount();
        if (count !== null && messageElement) {
            MessageRotator.messages[0] = `Images Processed: ${count.toLocaleString()}!`;
            if (messageElement.textContent === "Loading count...") {
                messageElement.textContent = MessageRotator.messages[0];
            }
        }
    }
}; 