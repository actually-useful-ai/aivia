/**
 * Text-to-speech utilities
 */

/**
 * Initializes text-to-speech functionality
 * @returns {Object} Text-to-speech control functions
 */
export const initializeTextToSpeech = () => {
    const synth = window.speechSynthesis;

    return {
        /**
         * Speaks the provided text
         * @param {string} text - The text to speak
         * @param {string} priority - The ARIA live region priority
         */
        speak: (text, priority = "polite") => {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = parseFloat(localStorage.getItem("speechRate")) || 1;
            utterance.pitch = parseFloat(localStorage.getItem("speechPitch")) || 1;
            synth.speak(utterance);
        },

        /**
         * Adjusts the speech rate
         * @param {'increase' | 'decrease'} direction - The direction to adjust
         * @returns {number} The new speech rate
         */
        adjustSpeechRate: (direction) => {
            const currentRate = parseFloat(localStorage.getItem("speechRate")) || 1;
            const newRate = direction === "increase"
                ? Math.min(currentRate + 0.1, 2)
                : Math.max(currentRate - 0.1, 0.5);
            localStorage.setItem("speechRate", newRate.toString());
            return newRate;
        }
    };
}; 