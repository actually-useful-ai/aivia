
### Project Plan for Streaming Assistant Chat Interface

---

#### 1. Project Overview

The goal of this project is to build a dynamic, accessible, and responsive streaming chat interface for an AI assistant. The interface will support:

- **Streaming Chat Responses:** Using either WebSockets or Server-Sent Events (SSE) to enable live updates.
- **Multiple AI Models:** Ability to select from various AI models (text, image, etc.) with dynamic UI adaptation.
- **File and Image Uploads:** Option to attach files (or images) with validation.
- **Markdown & Code Highlighting:** Conversion of markdown to HTML with support for syntax highlighting and embedded math (via KaTeX).
- **Theme Support:** Day/Night mode toggle along with the ability to adjust font type and size for improved accessibility.
- **Enhanced Accessibility:** ARIA attributes, keyboard navigation support, and clear labeling for UI elements.
- **Panel Containers:** Built-in placeholders (side panels) for future expansion like help widgets, settings, or additional contextual information.

---

#### 2. Key Features & Requirements

- **Core Chat Functionality:**
  - Real-time streaming responses.
  - Model configuration (via JSON or API-provided config).
  - File attachment with preview (image upload, for instance).

- **Accessibility Enhancements:**
  - ARIA labels (for navigation, inputs, buttons, etc.).
  - Keyboard navigation and focus management.
  - A dedicated switch/control to change font size and type.
  - Clear color contrast with appropriate day/night mode.

- **Theming & Styling:**
  - CSS variables to support dynamic theming (day/night).
  - Customizable font sizes and type choices via settings.
  - Responsive design for mobile devices.

- **Markdown & Content Rendering:**
  - Render markdown content.
  - Code highlighting through Highlight.js.
  - Math display via KaTeX.
  
- **Future-Facing Panel Containers:**
  - Left/right panel placeholders for further development.
  - Extendable design to host supplementary features (conversation history, context cues, settings, etc.).

- **API & Streaming:**
  - RESTful endpoints for starting a chat conversation and file uploads.
  - WebSocket/SSE for live-streaming responses.
  - Comprehensive error handling and fallback options.

---

#### 3. Technical Stack

- **Frontend:**
  - **Languages & Markup:** HTML5, CSS3 (with CSS variables and media queries), JavaScript (ES6+).
  - **Libraries/Dependencies:**
    - **Markdown-it:** For markdown parsing.
    - **Highlight.js:** For code syntax highlighting.
    - **KaTeX:** For math rendering.
    - **Select2:** For enhanced dropdown/model selection.
    - **jQuery:** (if necessary for Select2).
  - **Frameworks (Optional):** Consider using Vue.js or React for component-based development if scaling is needed.

- **Backend:**
  - **APIs:** RESTful endpoints for chat messages, file uploads, user authentication, and configuration fetching.
  - **Streaming Options:** Websocket or Server-Sent Events (SSE) for streaming responses.
  - **Security:** CSRF protection, appropriate CORS settings, and content security policies.

- **Testing & Tooling:**
  - **Unit Testing:** Frameworks such as Jest (for JavaScript) for testing individual components.
  - **Integration Testing:** Test API interactions and streaming response handling.
  - **Bundling:** Webpack or Vite for code bundling and asset optimization.
  
---

#### 4. Project Structure

```
streaming-chat/
├── index.html                # Main landing page for the chat UI
├── assets/                   # Images, icons, and other static assets
├── config/
│   └── models.json           # Available model configurations
├── js/
│   ├── app.js                # Primary application logic and initialization
│   ├── state.js              # Centralized state management
│   ├── ui.js                 # UI interactions, layout management, and accessibility
│   ├── models.js             # Model configuration handling
│   ├── messages.js           # Message processing, markdown rendering, and streaming updates
│   └── api.js                # Communication with RESTful endpoints and websocket/SSE handlers
├── styles/
│   ├── main.css              # Core styling
│   ├── themes.css            # Day/Night theme definitions and font customizations
│   ├── accessibility.css     # Accessibility-specific styles (e.g., high contrast, large fonts)
│   └── responsive.css        # Mobile and responsive styles
└── tests/                    # Unit and integration tests
```

---

#### 5. Implementation Phases

##### **Phase 1: Core Infrastructure (Week 1)**

- **Setup Application Skeleton:**
  - Create basic HTML markup with proper sections (header, main chat container, input area, and sidebar panel placeholders).
  - Establish central state management in `state.js`.
  - Initialize markdown-it and code highlighting.
  
  ```javascript
  // Example from state.js
  const createAppState = () => ({
      currentModel: null,
      messages: [],
      isResponding: false,
      config: null,
      markdownRenderer: null,
      // Future customization options:
      fontSize: '1rem',
      fontFamily: 'inherit'
  });
  ```

- **Basic UI Layout:**
  - Design `index.html` with semantic HTML5 (header, main, aside [for future panels]).
  - Introduce ARIA roles and labels (e.g., role="main", aria-label for chat regions).
  - Insert panel containers (left/right panels) that can later be populated with additional content.

  ```html
  <!-- Example snippet from index.html -->
  <body>
      <header role="banner">
          <h1 id="app-title">Streaming Assistant Chat</h1>
          <button id="themeToggle" aria-label="Toggle Day/Night Mode">Toggle Theme</button>
          <!-- Optionally, an accessibility switch -->
          <button id="fontSettings" aria-label="Adjust Font Size/Family">Font Settings</button>
      </header>
      <div class="layout-container">
          <aside id="left-panel" aria-label="Additional navigation panel">
              <!-- Future content: conversation history, navigation links etc. -->
          </aside>
          <main id="chat-main" aria-label="Chat conversation">
              <!-- Chat container, messages will be appended here -->
              <ul id="messages" aria-live="polite"></ul>
          </main>
          <aside id="right-panel" aria-label="Additional information panel">
              <!-- Future content: contextual help, settings -->
          </aside>
      </div>
      <footer>
          <!-- Input area -->
          <div id="chatInputContainer" role="form" aria-label="Chat input form">
              <textarea id="messageInput" aria-label="Type your message" placeholder="Type a message..."></textarea>
              <button id="sendButton" aria-label="Send message">Send</button>
          </div>
      </footer>
  </body>
  ```

- **Core Theme Variables:**
  ```css
  /* Core Theme Variables */
  :root {
      --primary-bg: #ffffff;
      --secondary-bg: #f8f9fa;
      --primary-text: #1a1a1a;
      --secondary-text: #4a4a4a;
      --accent-color: #0066cc;
      --border-color: #dde1e4;
      --success-color: #28a745;
      --error-color: #dc3545;
      --message-bg: #f8f9fa;
      --bot-message-bg: #ffffff;
      --user-message-bg: #0066cc;
      --user-message-text: #ffffff;
      --system-message-color: #666666;
      --button-hover: #0052a3;
      --input-border: #ced4da;
      --input-focus: #0066cc;
      --thought-bg: #e0f7fa;
      --thought-border: #b2ebf2;
  }
  ```

---

##### **Phase 2: UI Components & Accessibility (Week 2)**

- **Message Rendering & Input Handling:**
  - Implement message rendering with markdown support and streaming updates.
  - Create helper functions to render "think tags" or loading states.
  - Ensure dynamic ARIA announcements for new messages.

- **Accessibility & Customization:**
  - Add ARIA attributes (role, aria-label, aria-live).
  - Include keyboard navigation support (tab focusing, Enter/Shift+Enter differentiation).
  - Develop a font settings module to allow users to choose font size and family. Store preferences (e.g., in localStorage).
  - Integrate day/night mode toggling with CSS custom properties.
  
  ```javascript
  // Example from ui.js: Toggle theme and change font size
  function setTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('theme', theme);
  }
  
  function updateFontSettings(fontSize, fontFamily) {
      document.documentElement.style.setProperty('--font-size', fontSize);
      document.documentElement.style.setProperty('--font-family', fontFamily);
      // Optionally persist settings
      localStorage.setItem('fontSize', fontSize);
      localStorage.setItem('fontFamily', fontFamily);
  }
  ```

- **Panel Containers:**
  - Create placeholder containers (e.g., left-panel, right-panel) with minimal styling. Document their intended use.
  - Use semantic landmarks (e.g., `<aside>`) and ensure they are keyboard accessible.

---

##### **Core Interface Implementations**

```typescript
/**
 * Message Types and States
 * Defines the structure and types of messages in the chat system
 */
interface MessageTypes {
    standard: {
        user: string;
        assistant: string;
        system: string;
    };
    special: {
        thought: string;
        error: string;
        preview: string;
    };
}

interface MessageState {
    content: string;
    type: keyof MessageTypes;
    timestamp: number;
    metadata?: {
        model?: string;
        attachments?: Array<{
            type: string;
            data: string;
        }>;
    };
}

/**
 * Preview System
 * Handles code preview functionality and detection
 */
interface PreviewSystem {
    togglePreview(): void;
    detectCodeContent(content: string): boolean;
    updatePreviewVisibility(content: string): void;
    renderPreview(content: string): void;
}

const codeDetectionRules = {
    hasNewline: (content: string) => content.includes('\n'),
    hasBraces: (content: string) => /[{}]/.test(content),
    hasSemicolon: (content: string) => content.includes(';'),
    startsWithKeyword: (content: string) => 
        /^(const|let|var|function|import|export|class)\s/.test(content)
};

/**
 * Drag and Drop System
 * Manages file drag and drop functionality
 */
interface DragAndDropSystem {
    setupDropArea(element: HTMLElement): void;
    validateFile(file: File): boolean;
    handleDrop(event: DragEvent): void;
    updateDropAreaState(state: 'idle' | 'dragging' | 'invalid' | 'success'): void;
}

interface DropAreaEvents {
    onDragEnter: (e: DragEvent) => void;
    onDragOver: (e: DragEvent) => void;
    onDragLeave: (e: DragEvent) => void;
    onDrop: (e: DragEvent) => void;
}

/**
 * Model-Specific Interfaces
 * Defines different types of model interfaces and their requirements
 */
interface ModelInterfaces {
    chat: {
        setup(): void;
        handlePromptTrigger?: (trigger: string) => void;
    };
    image: {
        setup(): void;
        validateImage(file: File): boolean;
        processImage(file: File): Promise<string>;
    };
    prompt: {
        setup(): void;
        validatePrompt(prompt: string): boolean;
    };
    starters: {
        setup(): void;
        createStarterButton(starter: StarterConfig): HTMLElement;
    };
}

interface StarterConfig {
    label: string;
    message: string;
    category?: string;
    icon?: string;
}

/**
 * Toast Notification System
 * Manages user notifications and alerts
 */
interface ToastSystem {
    show(message: string, options?: {
        duration?: number;
        type?: 'success' | 'error' | 'info' | 'warning';
        position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
    }): void;
    hide(): void;
    updatePosition(position: string): void;
}

/**
 * Auto-Scroll Management
 * Handles chat container scrolling behavior
 */
interface ScrollManager {
    autoScroll(container: HTMLElement): void;
    isUserScrolled(): boolean;
    shouldAutoScroll(): boolean;
    onNewMessage(): void;
    onUserScroll(): void;
}

/**
 * State Management System
 * Central state management for the application
 */
interface StateManager {
    state: {
        currentModel: string | null;
        messages: MessageState[];
        isResponding: boolean;
        currentFile: File | null;
        config: any;
        userPreferences: {
            theme: 'light' | 'dark';
            fontSize: string;
            fontFamily: string;
            autoScroll: boolean;
        };
    };
    
    mutations: {
        setModel(model: string): void;
        addMessage(message: MessageState): void;
        setResponding(isResponding: boolean): void;
        setFile(file: File | null): void;
        updateConfig(config: any): void;
        updatePreferences(preferences: Partial<typeof state.userPreferences>): void;
    };
}

/**
 * Error Handling and Recovery
 * Comprehensive error management system
 */
interface ErrorHandling {
    handleError(error: Error): void;
    recoverFromError(error: Error): void;
    retryOperation<T>(
        operation: () => Promise<T>,
        maxRetries: number
    ): Promise<T>;
    showErrorToUser(error: Error): void;
}

interface ErrorTypes {
    NetworkError: typeof Error;
    ModelError: typeof Error;
    FileError: typeof Error;
    ValidationError: typeof Error;
}

/**
 * Implementation Examples
 */

// Example Toast Implementation
class ToastManager implements ToastSystem {
    private toastElement: HTMLElement;
    
    constructor() {
        this.toastElement = document.createElement('div');
        this.toastElement.className = 'toast';
        document.body.appendChild(this.toastElement);
    }
    
    show(message: string, options = {}) {
        this.toastElement.textContent = message;
        this.toastElement.className = `toast show ${options.type || ''}`;
        setTimeout(() => this.hide(), options.duration || 3000);
    }
    
    hide() {
        this.toastElement.className = 'toast';
    }
}

// Example Scroll Manager Implementation
class ChatScrollManager implements ScrollManager {
    private container: HTMLElement;
    private userScrolled: boolean = false;
    
    constructor(container: HTMLElement) {
        this.container = container;
        this.setupScrollListener();
    }
    
    private setupScrollListener() {
        this.container.addEventListener('scroll', () => this.onUserScroll());
    }
    
    autoScroll() {
        if (this.shouldAutoScroll()) {
            this.container.scrollTop = this.container.scrollHeight;
        }
    }
    
    isUserScrolled(): boolean {
        const { scrollTop, scrollHeight, clientHeight } = this.container;
        return scrollHeight - scrollTop - clientHeight > 50;
    }
    
    shouldAutoScroll(): boolean {
        return !this.userScrolled;
    }
    
    onUserScroll() {
        this.userScrolled = this.isUserScrolled();
    }
    
    onNewMessage() {
        this.autoScroll();
    }
}

/**
 * Additional Core Implementations
 */

// Example State Manager Implementation
class AppStateManager implements StateManager {
    private state: StateManager['state'] = {
        currentModel: null,
        messages: [],
        isResponding: false,
        currentFile: null,
        config: null,
        userPreferences: {
            theme: 'light',
            fontSize: '16px',
            fontFamily: 'system-ui',
            autoScroll: true
        }
    };

    private listeners: Set<() => void> = new Set();

    mutations = {
        setModel: (model: string) => {
            this.state.currentModel = model;
            this.notifyListeners();
        },
        addMessage: (message: MessageState) => {
            this.state.messages.push(message);
            this.notifyListeners();
        },
        setResponding: (isResponding: boolean) => {
            this.state.isResponding = isResponding;
            this.notifyListeners();
        },
        setFile: (file: File | null) => {
            this.state.currentFile = file;
            this.notifyListeners();
        },
        updateConfig: (config: any) => {
            this.state.config = config;
            this.notifyListeners();
        },
        updatePreferences: (preferences: Partial<typeof this.state.userPreferences>) => {
            this.state.userPreferences = { ...this.state.userPreferences, ...preferences };
            this.notifyListeners();
        }
    };

    private notifyListeners() {
        this.listeners.forEach(listener => listener());
    }

    subscribe(listener: () => void) {
        this.listeners.add(listener);
        return () => this.listeners.delete(listener);
    }
}

// Example Drag and Drop Implementation
class FileDropArea implements DragAndDropSystem {
    private element: HTMLElement;
    private options: {
        acceptedTypes: string[];
        maxSize: number;
    };

    constructor(element: HTMLElement, options = {
        acceptedTypes: ['image/*'],
        maxSize: 5 * 1024 * 1024 // 5MB
    }) {
        this.element = element;
        this.options = options;
        this.setupDropArea(element);
    }

    setupDropArea(element: HTMLElement) {
        const events: DropAreaEvents = {
            onDragEnter: (e) => {
                e.preventDefault();
                this.updateDropAreaState('dragging');
            },
            onDragOver: (e) => {
                e.preventDefault();
            },
            onDragLeave: (e) => {
                e.preventDefault();
                this.updateDropAreaState('idle');
            },
            onDrop: (e) => {
                e.preventDefault();
                this.handleDrop(e);
            }
        };

        Object.entries(events).forEach(([event, handler]) => {
            element.addEventListener(event.toLowerCase(), handler as EventListener);
        });
    }

    validateFile(file: File): boolean {
        const { acceptedTypes, maxSize } = this.options;
        
        if (file.size > maxSize) {
            this.updateDropAreaState('invalid');
            return false;
        }

        const isValidType = acceptedTypes.some(type => {
            if (type.endsWith('/*')) {
                const category = type.split('/')[0];
                return file.type.startsWith(`${category}/`);
            }
            return file.type === type;
        });

        if (!isValidType) {
            this.updateDropAreaState('invalid');
            return false;
        }

        return true;
    }

    handleDrop(event: DragEvent) {
        const file = event.dataTransfer?.files[0];
        if (!file) return;

        if (this.validateFile(file)) {
            this.updateDropAreaState('success');
            // Emit file ready event
            this.element.dispatchEvent(new CustomEvent('fileReady', { detail: file }));
        }
    }

    updateDropAreaState(state: 'idle' | 'dragging' | 'invalid' | 'success') {
        const stateClasses = {
            idle: 'drop-area',
            dragging: 'drop-area dragging',
            invalid: 'drop-area invalid',
            success: 'drop-area success'
        };
        
        this.element.className = stateClasses[state];
    }
}

// Example Error Handler Implementation
class ChatErrorHandler implements ErrorHandling {
    private toast: ToastSystem;
    
    constructor(toast: ToastSystem) {
        this.toast = toast;
    }
    
    async handleError(error: Error) {
        console.error('Error occurred:', error);
        
        if (error instanceof ErrorTypes.NetworkError) {
            await this.recoverFromError(error);
        } else {
            this.showErrorToUser(error);
        }
    }
    
    async recoverFromError(error: Error) {
        if (error instanceof ErrorTypes.NetworkError) {
            this.toast.show('Connection lost. Attempting to reconnect...', {
                type: 'warning',
                duration: 5000
            });
            
            // Attempt to reconnect
            await this.retryOperation(
                async () => {
                    // Reconnection logic here
                    return Promise.resolve();
                },
                3
            );
        }
    }
    
    async retryOperation<T>(
        operation: () => Promise<T>,
        maxRetries: number
    ): Promise<T> {
        for (let i = 0; i < maxRetries; i++) {
            try {
                return await operation();
            } catch (error) {
                if (i === maxRetries - 1) throw error;
                await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
            }
        }
        throw new Error('Max retries exceeded');
    }
    
    showErrorToUser(error: Error) {
        const userFriendlyMessage = this.getUserFriendlyMessage(error);
        this.toast.show(userFriendlyMessage, {
            type: 'error',
            duration: 5000
        });
    }
    
    private getUserFriendlyMessage(error: Error): string {
        const errorMessages = {
            [ErrorTypes.NetworkError.name]: 'Unable to connect to the server. Please check your internet connection.',
            [ErrorTypes.ModelError.name]: 'The AI model encountered an error. Please try again.',
            [ErrorTypes.FileError.name]: 'There was an error processing your file. Please try again.',
            [ErrorTypes.ValidationError.name]: 'Please check your input and try again.'
        };
        
        return errorMessages[error.constructor.name] || 'An unexpected error occurred. Please try again.';
    }
}

/**
 * Application Initialization and Setup
 */

class ChatApplication {
    private state: AppStateManager;
    private toast: ToastManager;
    private scroll: ChatScrollManager;
    private errorHandler: ChatErrorHandler;
    private dropArea: FileDropArea;

    constructor() {
        // Initialize core systems
        this.state = new AppStateManager();
        this.toast = new ToastManager();
        this.scroll = new ChatScrollManager(document.querySelector('.chat-container')!);
        this.errorHandler = new ChatErrorHandler(this.toast);
        
        // Initialize UI components
        this.initializeUI();
        
        // Load configuration
        this.loadConfig().catch(error => this.errorHandler.handleError(error));
    }

    private async initializeUI() {
        // Setup markdown renderer
        const md = window.markdownit({
            html: true,
            linkify: true,
            typographer: true,
            highlight: (str, lang) => {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(str, { language: lang }).value;
                    } catch (__) {}
                }
                return '';
            }
        });

        // Setup file drop area
        const dropAreaElement = document.querySelector('.drop-area');
        if (dropAreaElement) {
            this.dropArea = new FileDropArea(dropAreaElement, {
                acceptedTypes: ['image/*', 'application/pdf'],
                maxSize: 10 * 1024 * 1024 // 10MB
            });
        }

        // Setup event listeners
        this.setupEventListeners();
        
        // Initialize theme
        this.initializeTheme();
    }

    private setupEventListeners() {
        // Message input handling
        const messageInput = document.getElementById('messageInput');
        messageInput?.addEventListener('keydown', (event: KeyboardEvent) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                this.sendMessage();
            }
        });

        // File handling
        const fileInput = document.getElementById('fileInput');
        fileInput?.addEventListener('change', (event: Event) => {
            const file = (event.target as HTMLInputElement).files?.[0];
            if (file) {
                this.state.mutations.setFile(file);
                this.toast.show('File attached successfully', { type: 'success' });
            }
        });

        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        themeToggle?.addEventListener('click', () => {
            const currentTheme = this.state.state.userPreferences.theme;
            this.state.mutations.updatePreferences({
                theme: currentTheme === 'light' ? 'dark' : 'light'
            });
        });
    }

    private initializeTheme() {
        // Set initial theme based on system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.state.mutations.updatePreferences({
            theme: prefersDark ? 'dark' : 'light'
        });

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            this.state.mutations.updatePreferences({
                theme: e.matches ? 'dark' : 'light'
            });
        });
    }

    private async loadConfig() {
        try {
            const response = await fetch('./models.json');
            if (!response.ok) throw new ErrorTypes.NetworkError('Failed to load configuration');
            
            const config = await response.json();
            this.state.mutations.updateConfig(config);
            
            // Set initial model
            if (config.defaultModel) {
                this.state.mutations.setModel(config.defaultModel);
            }
        } catch (error) {
            throw new ErrorTypes.ModelError('Failed to initialize models');
        }
    }

    private async sendMessage() {
        const messageInput = document.getElementById('messageInput') as HTMLTextAreaElement;
        const content = messageInput.value.trim();
        
        if (!content && !this.state.state.currentFile) {
            this.toast.show('Please enter a message or attach a file', { type: 'warning' });
            return;
        }

        try {
            this.state.mutations.setResponding(true);
            
            // Add user message
            this.state.mutations.addMessage({
                content,
                type: 'standard.user',
                timestamp: Date.now(),
                metadata: {
                    model: this.state.state.currentModel,
                    attachments: this.state.state.currentFile ? [{
                        type: this.state.state.currentFile.type,
                        data: await this.readFileAsBase64(this.state.state.currentFile)
                    }] : undefined
                }
            });

            // Clear input
            messageInput.value = '';
            this.state.mutations.setFile(null);
            
            // Scroll to bottom
            this.scroll.onNewMessage();
            
            // TODO: Implement actual message sending logic here
            
        } catch (error) {
            this.errorHandler.handleError(error as Error);
        } finally {
            this.state.mutations.setResponding(false);
        }
    }

    private readFileAsBase64(file: File): Promise<string> {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result as string);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    new ChatApplication();
});

/**
 * Additional System Implementations
 */

// Model Source Handler Implementation
class ModelSourceHandlerImpl implements ModelSourceHandler {
    mistral = {
        async handleStream(response: Response) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const content = line.slice(6);
                        if (content.trim() === '[DONE]') continue;
                        const data = JSON.parse(content);
                        // Process data
                    }
                }
            }
        },
        
        formatRequest(content: string, messages: Message[]) {
            return {
                message: content,
                messages,
                stream: true
            };
        }
    };
    
    camina = {
        async handleFileUpload(file: File) {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/api/files/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('File upload failed');
            }
            
            const { file_id } = await response.json();
            return file_id;
        },
        
        async handleStream(response: Response) {
            // Similar to mistral stream handling
        },
        
        formatRequest(content: string, messages: Message[], fileId?: string) {
            return {
                message: content,
                messages,
                file_id: fileId,
                stream: true
            };
        }
    };
    
    // Additional source handlers...
}

// File Upload System Implementation
class FileUploadSystem {
    private supportedTypes = {
        image: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        document: ['application/pdf', 'text/plain'],
        all: ['image/*', 'application/pdf', 'text/plain']
    };
    
    private maxSizes = {
        image: 5 * 1024 * 1024, // 5MB
        document: 10 * 1024 * 1024, // 10MB
        default: 2 * 1024 * 1024 // 2MB
    };
    
    async uploadFile(file: File) {
        if (!this.validateFile(file)) {
            throw new Error('Invalid file type or size');
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        return response.json();
    }
    
    private validateFile(file: File): boolean {
        const isValidType = this.supportedTypes.all.some(type => {
            if (type.endsWith('/*')) {
                const category = type.split('/')[0];
                return file.type.startsWith(`${category}/`);
            }
            return file.type === type;
        });
        
        const isValidSize = file.size <= this.maxSizes.default;
        
        return isValidType && isValidSize;
    }
    
    async handleImageAttachment(file: File) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                resolve({
                    base64Content: reader.result as string,
                    messageUpdate: {
                        images: [reader.result as string]
                    }
                });
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
}

// Stream Handler Implementation
class StreamHandler {
    private decoder = new TextDecoder();
    
    setupStream(response: Response) {
        return {
            reader: response.body.getReader(),
            decoder: this.decoder
        };
    }
    
    async processChunk(chunk: string, modelSource: string) {
        if (!chunk.trim()) return {};
        
        try {
            const data = JSON.parse(chunk);
            
            switch (modelSource) {
                case 'mistral':
                    return this.processMistralChunk(data);
                case 'camina':
                    return this.processCaminaChunk(data);
                default:
                    return this.processDefaultChunk(data);
            }
        } catch (error) {
            console.warn('Error processing chunk:', error);
            return {};
        }
    }
    
    private processMistralChunk(data: any) {
        if (!data.choices?.[0]?.delta) return {};
        
        return {
            content: data.choices[0].delta.content,
            tokens: data.usage?.total_tokens,
            done: data.choices[0].finish_reason === 'stop'
        };
    }
    
    // Additional chunk processors...
    
    updateUI(content: string, tokens: number) {
        // Update UI with new content and token count
    }
    
    handleStreamError(error: Error) {
        console.error('Stream error:', error);
        // Handle error appropriately
    }
}

// Message Renderer Implementation
class MessageRenderer {
    private md: any; // markdown-it instance
    
    constructor() {
        this.md = window.markdownit({
            html: true,
            linkify: true,
            typographer: true,
            highlight: this.handleCodeHighlight
        });
    }
    
    processMessageContent(content: string): string {
        return this.md.render(content);
    }
    
    createMessageItem(content: string, type: string) {
        const container = document.createElement('div');
        container.className = `message-container ${type}-container`;
        
        const messageEl = document.createElement('div');
        messageEl.className = `message ${type}`;
        
        const tokenCountEl = document.createElement('div');
        tokenCountEl.className = 'token-count';
        
        container.appendChild(messageEl);
        container.appendChild(tokenCountEl);
        
        if (content) {
            messageEl.innerHTML = this.processMessageContent(content);
        }
        
        return { messageEl, tokenCountEl };
    }
    
    private handleCodeHighlight(str: string, lang: string) {
        if (lang && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(str, { language: lang }).value;
            } catch (__) {}
        }
        return ''; // use external default escaping
    }
}

// Loading State Manager Implementation
class LoadingStateManager {
    private loadingStates = new Set<string>();
    private thoughtBubbles: HTMLElement[] = [];
    
    setLoading(isLoading: boolean) {
        const elements = document.querySelectorAll('.loading-affected');
        elements.forEach(el => {
            if (isLoading) {
                el.classList.add('loading');
            } else {
                el.classList.remove('loading');
            }
        });
    }
    
    createThoughtBubble(content: string) {
        const bubble = document.createElement('div');
        bubble.className = 'thought-bubble';
        bubble.textContent = content;
        this.thoughtBubbles.push(bubble);
        document.querySelector('.chat-container')?.appendChild(bubble);
    }
    
    removeThoughtBubbles() {
        this.thoughtBubbles.forEach(bubble => bubble.remove());
        this.thoughtBubbles = [];
    }
    
    handleLoadingTimeout(timeout: number) {
        return new Promise((resolve) => {
            setTimeout(() => {
                this.setLoading(false);
                resolve(undefined);
            }, timeout);
        });
    }
}

// Session Manager Implementation
class SessionManager {
    private readonly STORAGE_KEY = 'chat_session';
    private readonly MAX_MESSAGES = 100;
    private readonly SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes
    
    initializeSession() {
        const session = this.loadPersistedMessages();
        if (session) {
            // Validate session timeout
            const lastActivity = localStorage.getItem('last_activity');
            if (lastActivity && Date.now() - Number(lastActivity) > this.SESSION_TIMEOUT) {
                this.clearSession();
                return [];
            }
            return session;
        }
        return [];
    }
    
    persistMessages(messages: Message[]) {
        if (messages.length > this.MAX_MESSAGES) {
            messages = messages.slice(-this.MAX_MESSAGES);
        }
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(messages));
        localStorage.setItem('last_activity', Date.now().toString());
    }
    
    loadPersistedMessages(): Message[] {
        const stored = localStorage.getItem(this.STORAGE_KEY);
        return stored ? JSON.parse(stored) : [];
    }
    
    clearSession() {
        localStorage.removeItem(this.STORAGE_KEY);
        localStorage.removeItem('last_activity');
    }
    
    handleSessionTimeout() {
        const checkInterval = setInterval(() => {
            const lastActivity = localStorage.getItem('last_activity');
            if (lastActivity && Date.now() - Number(lastActivity) > this.SESSION_TIMEOUT) {
                this.clearSession();
                clearInterval(checkInterval);
                // Notify user of session expiration
                window.dispatchEvent(new CustomEvent('sessionExpired'));
            }
        }, 60000); // Check every minute
    }
}

// API Error Handler Implementation
class APIErrorHandler {
    private retryStrategy = {
        maxRetries: 3,
        backoffFactor: 2,
        timeout: 1000
    };
    
    async handleNetworkError(error: Error) {
        console.error('Network error:', error);
        // Implement retry logic with exponential backoff
        return this.retryWithBackoff(async () => {
            // Retry the failed request
        });
    }
    
    private async retryWithBackoff(operation: () => Promise<any>) {
        let retries = 0;
        while (retries < this.retryStrategy.maxRetries) {
            try {
                return await operation();
            } catch (error) {
                retries++;
                if (retries === this.retryStrategy.maxRetries) throw error;
                
                const delay = this.retryStrategy.timeout * Math.pow(this.retryStrategy.backoffFactor, retries - 1);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    
    handleModelError(error: Error) {
        console.error('Model error:', error);
        // Handle model-specific errors
    }
    
    handleUploadError(error: Error) {
        console.error('Upload error:', error);
        // Handle upload-specific errors
    }
    
    handleStreamError(error: Error) {
        console.error('Stream error:', error);
        // Handle streaming-specific errors
    }
}

// API Client Implementation
class APIClient {
    private baseUrl: string;
    private errorHandler: APIErrorHandler;
    private streamHandler: StreamHandler;
    
    constructor(
        baseUrl: string,
        errorHandler: APIErrorHandler,
        streamHandler: StreamHandler
    ) {
        this.baseUrl = baseUrl;
        this.errorHandler = errorHandler;
        this.streamHandler = streamHandler;
    }
    
    async sendMessage(content: string, model: string, messages: Message[], file?: File) {
        try {
            const modelConfig = await this.getModelConfig(model);
            const requestBody = await this.prepareRequestBody(content, model, messages, file);
            
            const response = await fetch(`${this.baseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                },
                body: JSON.stringify(requestBody)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return this.streamHandler.setupStream(response);
            
        } catch (error) {
            return this.errorHandler.handleNetworkError(error as Error);
        }
    }
    
    private async getModelConfig(modelId: string) {
        const response = await fetch(`${this.baseUrl}/models/${modelId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch model configuration');
        }
        return response.json();
    }
    
    private async prepareRequestBody(
        content: string,
        model: string,
        messages: Message[],
        file?: File
    ) {
        const body: any = {
            model,
            messages,
            stream: true
        };
        
        if (file) {
            const fileData = await this.handleFileAttachment(file);
            body.file = fileData;
        }
        
        return body;
    }
    
    private async handleFileAttachment(file: File) {
        const fileUploader = new FileUploadSystem();
        try {
            if (file.type.startsWith('image/')) {
                return await fileUploader.handleImageAttachment(file);
            } else {
                return await fileUploader.uploadFile(file);
            }
        } catch (error) {
            this.errorHandler.handleUploadError(error as Error);
            throw error;
        }
    }
}

##### **Phase 3: Model Integration & API Communication (Week 3)**

- **Model Configuration:**
  - Load configuration from `/config/models.json` to populate model selection (e.g., via Select2).
  - Use ARIA labels on selectors to ensure screen reader clarity.

- **API Implementation & Streaming:**
  - Implement API client logic in `api.js` to handle posting messages and file uploads.
  - Support streaming responses via WebSocket or SSE.
  - Ensure proper error handling with user notifications (toast messages) and ARIA live announcements.

  ```javascript
  // Example from api.js: sendMessage with streaming support
  class APIClient {
      async sendMessage(message, currentModel) {
          const response = await fetch('/api/chat', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ message, model: currentModel })
          });
          return this.handleStreamingResponse(response);
      }
  }
  ```

---

##### **Phase 4: Enhanced Features & Future Expansions (Week 4)**

- **Theme & Accessibility Enhancements:**
  - Extend `themes.css` with day/night definitions and accessibility-specific adjustments.
  
  ```css
  /* Example snippet from themes.css */
  :root[data-theme="light"] {
      --primary-bg: #ffffff;
      --primary-text: #1a1a1a;
      --accent-color: #0066cc;
  }
  
  :root[data-theme="dark"] {
      --primary-bg: #1a1a1a;
      --primary-text: #ffffff;
      --accent-color: #3399ff;
  }
  ```

- **Font Customization Module:**
  - Implement a UI panel (e.g., modal or inline settings) for users to change font properties.
  - Ensure the changes are applied live and saved for future sessions.

- **Side Panels & Additional UI Extensions:**
  - Further develop the left/right panel containers for future features like conversation history, additional settings, AI hints, and contextual data.
  - Maintain modular and encapsulated code to easily add new features.

---

##### **Phase 5: Testing, Optimization & Deployment (Week 5)**

- **Testing:**
  - Write unit tests (using Jest or similar) for message rendering, API integration, and UI interactions.
  - Integration tests to simulate streaming and switching models.
  - Accessibility audits using tools like Lighthouse, aXe, or WAVE.

- **Performance & Deployment:**
  - Bundle assets using Webpack/Vite and optimize CSS/JS.
  - Optimize image and asset loading.
  - Implement error tracking, usage analytics, and set up a service worker for offline caching.
  - Configure CSRF, CORS, and content security policies before production deployment.

---

#### 6. Deployment Checklist

```markdown
1. Build & Bundle
   - Use Webpack/Vite for bundling and minifying assets.
   - Configure CSS preprocessing (Sass or PostCSS if needed).

2. Security
   - Set up CSRF protection and CORS policies.
   - Apply content security policy headers.

3. Accessibility Audit
   - Perform screen reader testing and keyboard navigation testing.
   - Validate ARIA labels and role attributes.

4. Performance Optimization
   - Implement code splitting and lazy loading.
   - Optimize image/assets.

5. Monitoring & Analytics
   - Integrate error logging and performance monitoring.
   - Set up usage analytics.
```

---

#### 7. Future Enhancements & Considerations

- **Advanced Functionality:**
  - Conversation history and export/import of chats.
  - Integration with external APIs for context or richer conversation.
  - Custom prompt templates and model comparisons.

- **UI Enhancements:**
  - Advanced markdown editor with inline preview.
  - Adaptive layouts for more extended panel use (extra information, side-nav).
  - Customizable themes beyond day/night (e.g., high contrast mode).

- **Accessibility:**
  - Constant review and updates based on accessibility feedback.
  - Expand keyboard controls and offer voice-controlled navigation.

interface ModelSystem {
    loadModelConfig(): Promise<void>;
    updateModelDependentUI(modelId: string): void;
    renderInterfaceForModel(modelObj: any): void;
    formatModelOption(model: any): string;
    formatModelSelection(model: any): string;
}

interface AccessibilityFeatures {
    keyboardNavigation: {
        sendMessage: 'Enter';
        newLine: 'Shift+Enter';
        focusInput: 'Alt+I';
        togglePreview: 'Alt+P';
    };
    
    ariaLabels: {
        messageInput: string;
        sendButton: string;
        fileInput: string;
        modelSelect: string;
        chatContainer: string;
    };
    
    screenReaderAnnouncements: {
        messageSent: string;
        messageReceived: string;
        fileAttached: string;
        modelChanged: string;
    };
}

interface MessageProcessor {
    processMessageContent(content: string): string;
    createMessageItem(content: string, type: "user" | "assistant" | "system"): HTMLElement;
    createThoughtBubble(content: string): void;
    clearThoughts(): void;
}

interface FileHandler {
    handleFileSelect(event: Event): void;
    setupImageDropArea(): void;
    readFileAsBase64(file: File): Promise<string>;
    updateAttachmentUI(attachOption: string): void;
}

