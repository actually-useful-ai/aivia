<script>
    const clientId = 'mrqWf4Kz2qZ4UkMxUlkT5F8fCq5lJQBIo5UZnrMzrh6v4xan7Ssx1SzE0PVhdD9J';
    const redirectUri = 'https://actuallyusefulai.com/auth/index.html';
    const apiBaseUrl = 'https://api.assisted.space/v2/auth';

    async function checkPatreonAccess() {
        const accessToken = localStorage.getItem('patreon_access_token');

        if (!accessToken) {
            console.warn('No access token found, redirecting to login...');
            window.location.href = redirectUri;
            return;
        }

        try {
            const userResponse = await fetch(`${apiBaseUrl}/patreon/user`, {
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
    }

    // Run access check on page load
    window.addEventListener('DOMContentLoaded', checkPatreonAccess);
</script>