/**
 * Protected content authentication
 */

export const ProtectedContentAuth = {
    // Configuration
    config: {
        apiBaseUrl: 'https://api.assisted.space/v2/auth',
        redirectUri: 'https://actuallyusefulai.com/auth/index.html'
    },

    /**
     * Checks if user has Patreon access
     * @returns {Promise<void>}
     */
    async checkPatreonAccess() {
        const accessToken = localStorage.getItem('patreon_access_token');

        if (!accessToken) {
            console.warn('No access token found, redirecting to login...');
            window.location.href = this.config.redirectUri;
            return;
        }

        try {
            const userResponse = await fetch(`${this.config.apiBaseUrl}/patreon/user`, {
                headers: { 'Authorization': `Bearer ${accessToken}` },
            });

            if (!userResponse.ok) throw new Error('Failed to fetch user data');
            const userData = await userResponse.json();

            if (!userData?.membership_details?.length || userData.membership_details[0].pledge_amount < 1) {
                console.warn('User does not meet pledge requirements, redirecting...');
                window.location.href = 'https://actuallyusefulai.com/auth';
            } else {
                console.log('User authenticated:', userData.full_name);
            }
        } catch (error) {
            console.error('Error verifying user:', error);
            window.location.href = 'https://actuallyusefulai.com/auth';
        }
    },

    /**
     * Sets up protected content access check
     */
    setupProtectedContent() {
        window.addEventListener('DOMContentLoaded', () => this.checkPatreonAccess());
    }
}; 