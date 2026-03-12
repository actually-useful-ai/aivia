/**
 * thought-bubble.js
 * Implements thought bubble visualization for AI reasoning steps
 * 
 * This snippet shows how to create and manage thought bubbles that provide
 * visual representation of the AI's chain of thought process.
 */

/**
 * Create a thought bubble element with enhanced scrolling
 * @param {string} content - The thought content
 * @param {Object} md - The markdown-it instance
 */
export function createThoughtBubble(content, md) {
    const thoughtsContainer = document.getElementById('thoughts-container');
    if (!thoughtsContainer) return;
    
    const bubble = document.createElement('div');
    bubble.className = 'thought-bubble';
    bubble.innerHTML = md.render(content);
    
    // Add animation class
    bubble.classList.add('thought-bubble-appear');
    
    thoughtsContainer.appendChild(bubble);
    
    // Enhanced scrolling for thought bubbles
    scrollThoughtContainer(thoughtsContainer, true);
}

/**
 * Handles scrolling of thought container with multiple attempts for reliability
 * @param {HTMLElement} container - The thought container element
 * @param {boolean} force - Whether to force scroll
 */
function scrollThoughtContainer(container, force = false) {
    if (!container) return;
    
    // Immediate scroll attempt
    try {
        container.scrollTop = container.scrollHeight;
    } catch (e) {
        console.error('Error during immediate scroll:', e);
    }
    
    // Additional scroll attempts to ensure visibility on different devices
    setTimeout(() => {
        if (container) container.scrollTop = container.scrollHeight;
    }, 50);
    
    setTimeout(() => {
        if (container) container.scrollTop = container.scrollHeight;
    }, 150);
    
    setTimeout(() => {
        if (container) container.scrollTop = container.scrollHeight;
    }, 300);
}

/**
 * Clear all thought bubbles from the container
 */
export function clearThoughts() {
    const thoughtsContainer = document.getElementById('thoughts-container');
    if (thoughtsContainer) {
        thoughtsContainer.innerHTML = '';
    }
}

/**
 * Example CSS for thought bubbles
 * Add this to your CSS file
 */
/*
.thought-bubble {
    background-color: #e0f7fa;
    border: 1px solid #b2ebf2;
    border-radius: 12px;
    padding: 10px 15px;
    margin: 8px 0;
    max-width: 80%;
    animation: appear 0.3s ease-in;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    font-size: 14px;
    color: #37474f;
}

.thought-bubble-appear {
    animation: bubbleAppear 0.5s ease-out;
}

@keyframes bubbleAppear {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

#thoughts-container {
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    max-height: 300px;
    padding: 8px;
    background-color: #f5f5f5;
    border-radius: 8px;
    margin-bottom: 15px;
}
*/

/**
 * Example HTML structure needed:
 * 
 * <div id="thoughts-container" aria-live="polite" aria-label="AI thinking process">
 *    <!-- Thought bubbles will be inserted here -->
 * </div>
 */ 