/**
 * Progress and Loading Utilities
 * Extracted from old_alt_scripts.js
 */

// Progress Bar Management
export const ProgressManager = {
    progressInterval: null,

    startProgress(progressBar, maxProgress = 90, increment = 1, interval = 300) {
        let progress = 0;
        progressBar.style.width = "0%";
        
        this.progressInterval = setInterval(() => {
            if (progress < maxProgress) {
                progress += increment;
                progressBar.style.width = `${progress}%`;
            }
        }, interval);
    },

    stopProgress(progressBar) {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        if (progressBar) {
            progressBar.style.width = "0%";
        }
    },

    setProgress(progressBar, progress) {
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    },

    async simulateStreamProgress(progressBar, startProgress = 40, maxProgress = 95, increment = 0.8, interval = 300) {
        let currentProgress = startProgress;
        return new Promise((resolve) => {
            const streamInterval = setInterval(() => {
                if (currentProgress < maxProgress) {
                    currentProgress += increment;
                    this.setProgress(progressBar, currentProgress);
                } else {
                    clearInterval(streamInterval);
                    resolve();
                }
            }, interval);
        });
    }
};

// Loading State Management
export const LoadingState = {
    setLoadingState(button, isLoading, loadingText = 'Processing...') {
        if (isLoading) {
            button.classList.add("loading");
            button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
            button.disabled = true;
        } else {
            button.classList.remove("loading");
            button.disabled = false;
        }
    },

    async withLoadingState(button, operation, loadingText = 'Processing...') {
        const originalButtonText = button.innerHTML;
        this.setLoadingState(button, true, loadingText);
        
        try {
            await operation();
        } finally {
            this.setLoadingState(button, false);
            button.innerHTML = originalButtonText;
        }
    }
}; 