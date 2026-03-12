/**
 * Accessibility Utilities
 * Consolidated from multiple files
 */

export const AccessibilityUtils = {
    // Display Mode Management
    initializeDisplayMode() {
        const savedMode = localStorage.getItem("displayMode") || "light-mode";
        document.body.classList.remove("light-mode", "dark-mode");
        document.body.classList.add(savedMode);
    },

    toggleDayNightMode() {
        const currentMode = localStorage.getItem("displayMode") || "light-mode";
        const newMode = currentMode === "dark-mode" ? "light-mode" : "dark-mode";
        document.body.classList.remove("light-mode", "dark-mode");
        document.body.classList.add(newMode);
        localStorage.setItem("displayMode", newMode);

        // Update loading gif if present
        const loadingGif = document.querySelector(".loading-gif");
        if (loadingGif) {
            loadingGif.src = loadingGif.src.replace(
                `triangle_construct_${currentMode.split('-')[0]}.gif`,
                `triangle_construct_${newMode.split('-')[0]}.gif`
            );
        }
    },

    // Font Management
    availableFonts: [
        { name: "Open Sans", class: "font-open-sans" },
        { name: "Inclusive Sans", class: "font-inclusive" },
        { name: "Arial", class: "font-arial" },
        { name: "System UI", class: "font-system" },
    ],

    currentFontIndex: 0,

    toggleFont() {
        const root = document.documentElement;
        this.currentFontIndex = (this.currentFontIndex + 1) % this.availableFonts.length;
        const newFont = this.availableFonts[this.currentFontIndex];

        // Remove all font classes
        this.availableFonts.forEach((font) => {
            root.classList.remove(font.class);
        });

        // Add new font class
        root.classList.add(newFont.class);
        root.style.setProperty("--font-primary", `'${newFont.name}', sans-serif`);
        localStorage.setItem("preferredFont", newFont.name);

        return newFont.name;
    },

    initializeFontPreferences() {
        const savedFont = localStorage.getItem("preferredFont");
        if (savedFont) {
            const fontIndex = this.availableFonts.findIndex((f) => f.name === savedFont);
            if (fontIndex !== -1) {
                this.currentFontIndex = fontIndex - 1; // Subtract 1 because toggleFont will add 1
                this.toggleFont();
            }
        }
    },

    // Font Size Management
    initializeFontScale() {
        const savedScale = localStorage.getItem("fontScale");
        if (savedScale) {
            document.documentElement.style.setProperty("--font-scale", savedScale);
            this.updateFontSizeDisplay(savedScale);
        }
    },

    changeFontSize(action) {
        const root = document.documentElement;
        const currentScale = parseFloat(
            getComputedStyle(root).getPropertyValue("--font-scale")
        );

        let newScale;
        if (action === "increase") {
            newScale = Math.min(currentScale + 0.1, 2.0);
        } else if (action === "decrease") {
            newScale = Math.max(currentScale - 0.1, 0.8);
        }

        if (newScale) {
            root.style.setProperty("--font-scale", newScale);
            localStorage.setItem("fontScale", newScale.toString());
            this.updateFontSizeDisplay(newScale);
        }
    },

    resetFontSize() {
        const defaultScale = 1.0;
        const root = document.documentElement;
        root.style.setProperty("--font-scale", `${defaultScale}`);
        localStorage.setItem("fontScale", `${defaultScale}`);
        this.updateFontSizeDisplay(defaultScale);
    },

    updateFontSizeDisplay(scale) {
        const fontSizeDisplay = document.getElementById("currentFontSize");
        if (fontSizeDisplay) {
            fontSizeDisplay.textContent = `${Math.round(scale * 100)}%`;
        }
    },

    // Text-to-Speech
    initializeTextToSpeech() {
        const synth = window.speechSynthesis;

        return {
            speak: (text, priority = "polite") => {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = parseFloat(localStorage.getItem("speechRate")) || 1;
                utterance.pitch = parseFloat(localStorage.getItem("speechPitch")) || 1;
                synth.speak(utterance);
            },

            adjustSpeechRate: (direction) => {
                const currentRate = parseFloat(localStorage.getItem("speechRate")) || 1;
                const newRate = direction === "increase"
                    ? Math.min(currentRate + 0.1, 2)
                    : Math.max(currentRate - 0.1, 0.5);
                localStorage.setItem("speechRate", newRate.toString());
                return newRate;
            }
        };
    },

    // Switch Control
    initializeSwitchControl() {
        let currentFocusIndex = 0;
        const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
        let scanning = false;
        let scanInterval;

        return {
            moveToNextElement: () => {
                const elements = Array.from(document.querySelectorAll(focusableElements));
                currentFocusIndex = (currentFocusIndex + 1) % elements.length;
                elements[currentFocusIndex].focus();
            },

            selectCurrentElement: () => {
                document.activeElement.click();
            },

            toggleScanning: () => {
                scanning = !scanning;
                if (scanning) {
                    scanInterval = setInterval(() => {
                        const elements = Array.from(document.querySelectorAll(focusableElements));
                        currentFocusIndex = (currentFocusIndex + 1) % elements.length;
                        elements[currentFocusIndex].focus();
                    }, 2000);
                } else {
                    clearInterval(scanInterval);
                }
                return scanning;
            }
        };
    },

    // Eye Gaze Support
    initializeEyeGaze(dwellTime = 1000) {
        let dwellTimer;
        let lastElement;

        return {
            handleGaze: (element) => {
                if (element !== lastElement) {
                    clearTimeout(dwellTimer);
                    lastElement = element;

                    if (element.matches('button, [role="button"]')) {
                        dwellTimer = setTimeout(() => {
                            element.click();
                            element.classList.add("dwell-activated");
                            setTimeout(() => element.classList.remove("dwell-activated"), 200);
                        }, dwellTime);
                    }
                }
            }
        };
    },

    // ARIA and Keyboard Support
    setupAccessibilityFeatures() {
        // Set up ARIA landmarks
        document.querySelectorAll('[role="region"]').forEach(region => {
            if (!region.hasAttribute('aria-label')) {
                region.setAttribute('aria-label', region.id || 'Content region');
            }
        });

        // Ensure all interactive elements are keyboard accessible
        document.querySelectorAll('button, a, [role="button"]').forEach(element => {
            if (!element.hasAttribute('tabindex')) {
                element.setAttribute('tabindex', '0');
            }
        });

        // Add screen reader announcements for dynamic content
        const announcer = document.createElement('div');
        announcer.setAttribute('aria-live', 'polite');
        announcer.setAttribute('aria-atomic', 'true');
        announcer.className = 'sr-only';
        document.body.appendChild(announcer);

        return announcer;
    }
}; 