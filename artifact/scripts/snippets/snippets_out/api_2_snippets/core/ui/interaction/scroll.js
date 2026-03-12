/**
 * Scroll Management
 */

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