/**
 * Patreon authentication utilities
 */

/**
 * Patreon configuration
 */
export const PATREON_CONFIG = {
    CLIENT_ID: 'mrqWf4Kz2qZ4UkMxUlkT5F8fCq5lJQBIo5UZnrMzrh6v4xan7Ssx1SzE0PVhdD9J',
    REDIRECT_URI: 'https://actuallyusefulai.com/alt/dev/index.html',
    API_BASE: 'https://api.assisted.space/v2/auth'
};

/**
 * Patreon integration class for handling authentication and user management
 */
export class PatreonIntegration {
    /**
     * Creates a new PatreonIntegration instance
     * @param {string} loginButtonId - ID of the login button element
     */
    constructor(loginButtonId = 'donorLogin') {
        this.donorButton = document.getElementById(loginButtonId);
        if (!this.donorButton) {
            console.warn(`Button with id '${loginButtonId}' not found`);
            return;
        }
        this.setupInitialButton();
        this.setupAuth();
    }

    /**
     * Sets up the initial state of the login button
     */
    setupInitialButton() {
        if (localStorage.getItem('patreonToken')) {
            this.donorButton.textContent = 'Logout';
            this.donorButton.onclick = () => this.handleLogout();
        } else {
            this.donorButton.textContent = 'Donor Login';
            this.donorButton.onclick = () => this.initiateOAuth();
        }
    }

    /**
     * Sets up authentication handling
     */
    setupAuth() {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const storedState = localStorage.getItem('oauth_state');

        if (code) {
            if (state && storedState && state === storedState) {
                this.handleOAuthCallback(code);
            } else {
                console.error('State mismatch - possible CSRF attempt');
                this.donorButton.textContent = 'Login Failed - Try Again';
            }
            localStorage.removeItem('oauth_state');
            window.history.replaceState({}, document.title, window.location.pathname);
        }

        if (localStorage.getItem('patreonToken')) {
            this.validateToken();
        }
    }

    /**
     * Initiates the OAuth flow
     */
    async initiateOAuth() {
        try {
            const state = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2);
            localStorage.setItem('oauth_state', state);
            
            const params = new URLSearchParams({
                response_type: 'code',
                client_id: PATREON_CONFIG.CLIENT_ID,
                redirect_uri: PATREON_CONFIG.REDIRECT_URI,
                scope: 'identity identity.memberships campaigns campaigns.members',
                state: state
            });
            
            window.location.href = `https://www.patreon.com/oauth2/authorize?${params.toString()}`;
        } catch (error) {
            console.error('Error initiating OAuth:', error);
            this.donorButton.textContent = 'Login Failed - Try Again';
        }
    }

    /**
     * Handles the OAuth callback
     * @param {string} code - The authorization code
     */
    async handleOAuthCallback(code) {
        try {
            const response = await fetch(`${PATREON_CONFIG.API_BASE}/patreon/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    code,
                    grant_type: 'authorization_code',
                    redirect_uri: PATREON_CONFIG.REDIRECT_URI
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Token exchange failed:', errorData);
                throw new Error('Failed to get access token');
            }

            const data = await response.json();
            if (!data.success || !data.access_token) {
                throw new Error('Invalid token response');
            }

            localStorage.setItem('patreonToken', data.access_token);
            this.donorButton.textContent = 'Logout';
            this.donorButton.onclick = () => this.handleLogout();
        } catch (error) {
            console.error('Error during authentication:', error);
            this.donorButton.textContent = 'Login Failed - Try Again';
            this.donorButton.onclick = () => this.initiateOAuth();
        }
    }

    /**
     * Validates the current token
     * @returns {Promise<Object|null>} The user data if valid, null otherwise
     */
    async validateToken() {
        const token = localStorage.getItem('patreonToken');
        if (!token) return;

        try {
            const response = await fetch(`${PATREON_CONFIG.API_BASE}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token })
            });

            if (!response.ok) {
                throw new Error('Token validation failed');
            }

            const data = await response.json();
            if (!data.valid) {
                this.handleLogout();
            }
            return data.user;
        } catch (error) {
            console.error('Error validating token:', error);
            this.handleLogout();
            return null;
        }
    }

    /**
     * Handles user logout
     */
    handleLogout() {
        localStorage.removeItem('patreonToken');
        localStorage.removeItem('oauth_state');
        this.donorButton.textContent = 'Donor Login';
        this.donorButton.onclick = () => this.initiateOAuth();
    }

    /**
     * Checks if a user is currently logged in
     * @returns {boolean} Whether a user is logged in
     */
    static isLoggedIn() {
        return !!localStorage.getItem('patreonToken');
    }

    /**
     * Gets the current user's data
     * @returns {Promise<Object|null>} The user data if available
     */
    static async getCurrentUser() {
        const token = localStorage.getItem('patreonToken');
        if (!token) return null;

        try {
            const response = await fetch(`${PATREON_CONFIG.API_BASE}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token })
            });

            if (!response.ok) return null;

            const data = await response.json();
            return data.valid ? data.user : null;
        } catch (error) {
            console.error('Error getting current user:', error);
            return null;
        }
    }

    /**
     * Gets the current authentication token
     * @returns {string|null} The current token if available
     */
    static getToken() {
        return localStorage.getItem('patreonToken');
    }
} 