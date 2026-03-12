/**
 * Toast Notification Management
 */

export const ToastManager = {
    setupToast(containerId = 'toast', defaultDuration = 3000) {
        const toastElement = document.getElementById(containerId);
        if (!toastElement) return null;

        return {
            show: (message, duration = defaultDuration) => {
                toastElement.textContent = message;
                toastElement.classList.add('show');
                
                setTimeout(() => {
                    toastElement.classList.remove('show');
                }, duration);
            },
            hide: () => {
                toastElement.classList.remove('show');
            }
        };
    }
}; 