/**
 * Bot Management
 */

export const BotManager = {
    /**
     * Creates the bots panel
     * @param {string} botsPanelId - ID of the bots panel element
     * @returns {Promise<void>}
     */
    async createBotsPanel(botsPanelId = "assistantsPanel") {
        const botsPanel = document.getElementById(botsPanelId);
        if (!botsPanel) return;

        botsPanel.innerHTML = `
            <div class="panel-section">
                <h2 class="panel-section-header">Assistants</h2>
                <div id="botCategories"></div>
            </div>
        `;

        try {
            const response = await fetch("bots.json");
            const data = await response.json();
            await this.populateBotCategories(data);
        } catch (error) {
            console.error("Error loading bots:", error);
            document.getElementById("botCategories").innerHTML =
                '<p class="error-message" role="alert">Error loading assistants.</p>';
        }
    },

    /**
     * Populates bot categories
     * @param {Object} data - Bot data
     * @param {Set} loadedCategories - Set of loaded category names
     * @returns {Promise<void>}
     */
    async populateBotCategories(data, loadedCategories = new Set()) {
        const botCategories = document.getElementById("botCategories");
        if (!botCategories) return;

        data.categories.forEach((category) => {
            if (loadedCategories.has(category.name)) return;

            const visibleBots = category.bots.filter(
                (bot) => bot.state !== "hidden"
            );

            if (visibleBots.length > 0) {
                const categorySection = this.createCategorySection(category, visibleBots);
                botCategories.appendChild(categorySection);
                loadedCategories.add(category.name);
            }
        });
    },

    /**
     * Creates a category section
     * @param {Object} category - Category data
     * @param {Array} visibleBots - Array of visible bots
     * @returns {HTMLElement} The created category section
     */
    createCategorySection(category, visibleBots) {
        const categorySection = document.createElement("div");
        categorySection.className = "panel-section";

        const header = document.createElement("h4");
        header.className = "panel-section-header";
        header.textContent = category.name;
        categorySection.appendChild(header);

        const buttonRow = document.createElement("div");
        buttonRow.className = "button-row single";
        buttonRow.setAttribute("role", "group");
        buttonRow.setAttribute("aria-label", `${category.name} Bots`);

        visibleBots.forEach((bot) => {
            const button = this.createBotButton(bot);
            buttonRow.appendChild(button);
        });

        categorySection.appendChild(buttonRow);
        return categorySection;
    },

    /**
     * Creates a bot button
     * @param {Object} bot - Bot data
     * @returns {HTMLElement} The created button element
     */
    createBotButton(bot) {
        const button = document.createElement("button");
        button.className = `panel-button ${
            bot.id === window.currentBotId ? "active active-marker" : ""
        } ${
            ["premium", "professional"].includes(bot.state) ? bot.state : ""
        }`;
        button.setAttribute("data-bot-id", bot.id);
        button.setAttribute("data-tooltip", bot.description);
        button.setAttribute(
            "aria-pressed",
            bot.id === window.currentBotId ? "true" : "false"
        );
        button.setAttribute("aria-label", bot.name);

        const iconClass = this.getBotIconClass(bot);
        button.innerHTML = `<i class="${iconClass}" aria-hidden="true"></i> ${bot.name}`;

        if (["false", "premium", "professional"].includes(bot.state)) {
            button.disabled = true;
        }

        button.onclick = () => this.selectBot(bot.id, bot.name, bot.description, bot.buttons);
        return button;
    },

    /**
     * Gets the icon class for a bot
     * @param {Object} bot - Bot data
     * @returns {string} The icon class
     */
    getBotIconClass(bot) {
        const botActionIcons = {
            disabled: "fas fa-lock",
            premium: "fas fa-star",
            professional: "fas fa-crown",
            default: "fas fa-robot"
        };

        return bot.state === "false"
            ? botActionIcons.disabled
            : ["premium", "professional"].includes(bot.state)
            ? botActionIcons[bot.state]
            : botActionIcons[bot.action] || botActionIcons.default;
    }
}; 