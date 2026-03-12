// Device detection
export const isMobile = () => /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
export const isAndroid = () => /Android/i.test(navigator.userAgent);

// Image processing
export const resizeImage = async (file, maxDimension = 2048) => {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            let width = img.width;
            let height = img.height;
            
            if (width > height && width > maxDimension) {
                height = Math.round((height * maxDimension) / width);
                width = maxDimension;
            } else if (height > maxDimension) {
                width = Math.round((width * maxDimension) / height);
                height = maxDimension;
            }

            canvas.width = width;
            canvas.height = height;
            
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);
            
            const base64 = canvas.toDataURL('image/jpeg', 0.9);
            resolve(base64.split('base64,')[1]);
        };
        img.src = URL.createObjectURL(file);
    });
};

// System prompt for alt text generation
export const ALT_TEXT_SYSTEM_PROMPT = `You're an Alt Text Specialist, dedicated to creating precise and accessible alt text for digital images, especially memes. Your primary goal is to ensure visually impaired individuals can engage with imagery by providing concise, accurate, and ethically-minded descriptions.

Create Alt Text
- **Depict essential visuals and visible text accurately.**
- **Avoid adding social-emotional context or narrative interpretations unless specifically requested.**
- **Refrain from speculating on artists' intentions.**
- **Avoid prepending with "Alt text:" for direct usability.**
- **Maintain clarity and consistency for all descriptions, including direct image links.**
- **Character limit:** All descriptions must be under 1000 characters.`;

// Content processing
export const cleanupContent = (content) => {
    return content
        .replace(/^[\s-]+|[\s-]+$/g, '') // Remove leading/trailing spaces and dashes
        .replace(/^Alt text:\s*/i, ''); // Remove "Alt text:" prefix case-insensitive
};

// URL utilities
export const createCacheBustedUrl = (file) => {
    return URL.createObjectURL(file) + '#' + new Date().getTime();
};

export const revokeCacheBustedUrl = (url) => {
    URL.revokeObjectURL(url.split('#')[0]);
};

// Pull to refresh constants
export const PULL_REFRESH_THRESHOLD = 80;

// Animation utilities
export const createStreamingCharSpan = (char) => {
    const span = document.createElement('span');
    span.textContent = char;
    span.className = 'streaming-char';
    return span;
};

// Default model
export const DEFAULT_MODEL = "coolhand/impossible_alt:13b";

// API endpoint
export const API_BASE_URL = "https://7584e4c6571c.ngrok.app/api";

// API interactions
export const makeApiCall = async (messages, base64Image, model, apiBaseUrl) => {
    const requestBody = {
        model,
        messages,
        stream: true
    };

    if (base64Image) {
        requestBody.messages[requestBody.messages.length - 1].images = [base64Image];
    }

    console.log("API Request details:", {
        url: `${apiBaseUrl}/chat`,
        body: { 
            ...requestBody, 
            messages: requestBody.messages,
            images: requestBody.images ? ['[Image Data]'] : undefined 
        }
    });

    return fetch(`${apiBaseUrl}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    });
};

export const processStreamedResponse = async (response, {
    onContent = () => {},
    onDone = () => {},
    onError = () => {}
} = {}) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullContent = "";
    let totalTokens = 0;

    try {
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.trim() === '') continue;

                try {
                    const data = JSON.parse(line);
                    
                    if (data.message?.content) {
                        fullContent += data.message.content;
                        onContent(data.message.content);
                    }

                    if (data.done) {
                        totalTokens = data.prompt_eval_count + data.eval_count;
                        onDone({
                            fullContent,
                            totalTokens,
                            messages: [{
                                role: "assistant",
                                content: fullContent
                            }]
                        });
                    }
                } catch (error) {
                    console.warn("Error parsing line:", line, error);
                    continue;
                }
            }
        }
    } catch (error) {
        onError(error);
        throw error;
    }

    return { fullContent, totalTokens };
};

// Clipboard utilities
export const copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (error) {
        console.error('Failed to copy text:', error);
        return false;
    }
};

// Image analysis
export const analyzeImage = async (base64Content, model, apiBaseUrl) => {
    try {
        const messages = [{
            role: "system",
            content: ALT_TEXT_SYSTEM_PROMPT
        }, {
            role: "user",
            content: "Please provide alt text for this image.",
            images: base64Content ? [base64Content] : undefined
        }];

        const response = await makeApiCall(messages, base64Content, model, apiBaseUrl);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API Error (${response.status}): ${errorText}`);
        }

        return response;
    } catch (error) {
        console.error('Error analyzing image:', error);
        throw error;
    }
};

// Patreon Integration
export const PATREON_CONFIG = {
    CLIENT_ID: 'mrqWf4Kz2qZ4UkMxUlkT5F8fCq5lJQBIo5UZnrMzrh6v4xan7Ssx1SzE0PVhdD9J',
    REDIRECT_URI: 'https://actuallyusefulai.com/alt/dev/index.html',
    API_BASE: 'https://api.assisted.space/v2/auth'
};

export class PatreonIntegration {
    constructor(loginButtonId = 'donorLogin') {
        this.donorButton = document.getElementById(loginButtonId);
        if (!this.donorButton) {
            console.warn(`Button with id '${loginButtonId}' not found`);
            return;
        }
        this.setupInitialButton();
        this.setupAuth();
    }

    setupInitialButton() {
        if (localStorage.getItem('patreonToken')) {
            this.donorButton.textContent = 'Logout';
            this.donorButton.onclick = () => this.handleLogout();
        } else {
            this.donorButton.textContent = 'Donor Login';
            this.donorButton.onclick = () => this.initiateOAuth();
        }
    }

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

    handleLogout() {
        localStorage.removeItem('patreonToken');
        localStorage.removeItem('oauth_state');
        this.donorButton.textContent = 'Donor Login';
        this.donorButton.onclick = () => this.initiateOAuth();
    }

    static isLoggedIn() {
        return !!localStorage.getItem('patreonToken');
    }

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

    static getToken() {
        return localStorage.getItem('patreonToken');
    }
}

// Example usage:
/*
// Initialize Patreon integration
const patreon = new PatreonIntegration('donorLogin');

// Check login status
if (PatreonIntegration.isLoggedIn()) {
    // Get current user
    const user = await PatreonIntegration.getCurrentUser();
    if (user) {
        console.log('Logged in as:', user.full_name);
    }
}

// Make authenticated API calls
const token = PatreonIntegration.getToken();
if (token) {
    const response = await fetch('your-api-endpoint', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
}
*/ 