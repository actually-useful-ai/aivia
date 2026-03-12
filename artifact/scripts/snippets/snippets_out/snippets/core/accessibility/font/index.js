/**
 * Font management utilities
 */

/**
 * Available font configurations
 */
export const availableFonts = [
    { name: "Open Sans", class: "font-open-sans" },
    { name: "Inclusive Sans", class: "font-inclusive" },
    { name: "Arial", class: "font-arial" },
    { name: "System UI", class: "font-system" },
];

let currentFontIndex = 0;

/**
 * Toggles between available fonts
 * @returns {string} The name of the newly selected font
 */
export const toggleFont = () => {
    const root = document.documentElement;
    currentFontIndex = (currentFontIndex + 1) % availableFonts.length;
    const newFont = availableFonts[currentFontIndex];

    // Remove all font classes
    availableFonts.forEach((font) => {
        root.classList.remove(font.class);
    });

    // Add new font class
    root.classList.add(newFont.class);
    root.style.setProperty("--font-primary", `'${newFont.name}', sans-serif`);
    localStorage.setItem("preferredFont", newFont.name);

    return newFont.name;
};

/**
 * Initializes font preferences from saved settings
 */
export const initializeFontPreferences = () => {
    const savedFont = localStorage.getItem("preferredFont");
    if (savedFont) {
        const fontIndex = availableFonts.findIndex((f) => f.name === savedFont);
        if (fontIndex !== -1) {
            currentFontIndex = fontIndex - 1; // Subtract 1 because toggleFont will add 1
            toggleFont();
        }
    }
};

/**
 * Initializes font scaling from saved settings
 */
export const initializeFontScale = () => {
    const savedScale = localStorage.getItem("fontScale");
    if (savedScale) {
        document.documentElement.style.setProperty("--font-scale", savedScale);
        updateFontSizeDisplay(savedScale);
    }
};

/**
 * Changes the font size
 * @param {'increase' | 'decrease'} action - The action to perform
 */
export const changeFontSize = (action) => {
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
        updateFontSizeDisplay(newScale);
    }
};

/**
 * Resets font size to default
 */
export const resetFontSize = () => {
    const defaultScale = 1.0;
    const root = document.documentElement;
    root.style.setProperty("--font-scale", `${defaultScale}`);
    localStorage.setItem("fontScale", `${defaultScale}`);
    updateFontSizeDisplay(defaultScale);
};

/**
 * Updates the font size display element
 * @param {number} scale - The current font scale
 */
export const updateFontSizeDisplay = (scale) => {
    const fontSizeDisplay = document.getElementById("currentFontSize");
    if (fontSizeDisplay) {
        fontSizeDisplay.textContent = `${Math.round(scale * 100)}%`;
    }
}; 