/**
 * Bot and Assistant Management
 * Extracted from from_main.js
 */

// Bot Management
export const BotManager = {
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

// Assistant Interface Management
export const AssistantManager = {
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

    autoScroll() {
        const messagesList = document.getElementById("messages");
        if (messagesList) {
            messagesList.scrollTop = messagesList.scrollHeight;
        }
    },

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