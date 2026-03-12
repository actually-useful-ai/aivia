/**
 * Display mode management utilities
 */

/**
 * Initializes the display mode from saved preferences
 */
export const initializeDisplayMode = () => {
    const savedMode = localStorage.getItem("displayMode") || "light-mode";
    document.body.classList.remove("light-mode", "dark-mode");
    document.body.classList.add(savedMode);
};

/**
 * Toggles between light and dark mode
 */
export const toggleDayNightMode = () => {
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
}; 