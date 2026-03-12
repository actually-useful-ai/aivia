/**
 * HTML Components Templates
 */

export const Templates = {
    /**
     * File Upload Area Template
     * @returns {string} The upload area HTML
     */
    uploadArea: () => `
        <div id="uploadArea" 
             class="upload-area" 
             aria-labelledby="upload-heading"
             role="button"
             tabindex="0"
             aria-pressed="false">
            <i class="fas fa-cloud-upload-alt upload-icon" aria-hidden="true"></i>
            <h2 id="upload-heading" class="upload-text">
                Drop, paste, or click to upload!
            </h2>
            <div class="upload-subtext">
                JPG, JPEG, PNG, GIF, WEBP, and more. Try any format, it might work!<br /><br />
                Max size: 20MB
            </div>
            <input type="file"
                   id="fileInput"
                   accept="image/*,video/*,.heic,.heif,image/heic,image/heif,video/quicktime,video/webm,video/mp4,video/x-msvideo,video/x-flv,video/x-ms-wmv,video/x-matroska,video/3gpp,video/x-m4v,video/x-ms-asf,video/x-mpegURL,video/x-ms-vob,video/x-ms-tmp,video/x-mpeg,video/mp2t"
                   hidden
                   aria-describedby="upload-heading" />
        </div>`,

    /**
     * Result Container Template
     * @returns {string} The result container HTML
     */
    resultContainer: () => `
        <div id="resultContainer" 
             class="result-container"
             role="region"
             aria-live="polite"
             aria-atomic="true">
            <div id="streamingIndicator"
                 class="streaming-indicator"
                 role="status"
                 aria-live="assertive">
                <img id="uploadedImage"
                     class="uploaded-image"
                     src=""
                     alt="Processing..." />
                <div class="progress-bar"
                     role="progressbar"
                     aria-valuemin="0"
                     aria-valuemax="100">
                    <div class="progress-fill"></div>
                </div>
            </div>
            <div id="altTextDisplay"
                 class="alt-text-display"
                 role="textbox"
                 aria-readonly="true"></div>
            <button id="copyButton"
                    class="copy-button"
                    aria-label="Copy Alt Text to Clipboard">
                <i class="fas fa-copy" aria-hidden="true"></i> Copy to Clipboard
            </button>
        </div>`,

    /**
     * Control Buttons Template
     * @returns {string} The control buttons HTML
     */
    controlButtons: () => `
        <button id="settingsButton"
                class="settings-button"
                aria-haspopup="true"
                aria-controls="settings-tray"
                aria-label="Open Settings">
            <i class="fas fa-question" aria-hidden="true"></i>
        </button>
        <button id="pasteButton"
                class="paste-button"
                aria-label="Paste Image">
            <i class="fas fa-paste"></i> Paste Image
        </button>
        <button id="restartButton"
                class="restart-button"
                aria-label="Start Over"
                onclick="window.location.reload()">
            <i class="fas fa-redo"></i> Start Over
        </button>`,

    /**
     * Support Buttons Template
     * @param {string} donateUrl - URL for donations
     * @param {string} patreonUrl - URL for Patreon
     * @returns {string} The support buttons HTML
     */
    supportButtons: (donateUrl = "https://coolhand.gumroad.com/l/donate?layout=profile", patreonUrl = "https://assisted.space/join") => `
        <div class="support-buttons">
            <a href="${donateUrl}"
               target="_blank"
               class="support-button">
                <i class="fas fa-heart"></i> Tip
            </a>
            <a href="${patreonUrl}"
               target="_blank"
               class="support-button">
                <i class="fas fa-star"></i> Patreon
            </a>
        </div>`,

    /**
     * Settings Tray Template
     * @param {string} content - The tray content
     * @returns {string} The settings tray HTML
     */
    settingsTray: (content) => `
        <div id="settings-tray"
             class="tray"
             aria-labelledby="about-heading"
             role="dialog">
            <div class="tray-content">
                <h3 id="about-heading">What is this?</h3>
                ${content}
            </div>
        </div>`
}; 