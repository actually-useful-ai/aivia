/**
 * Drag and Drop Handler
 */

export const DragDropHandler = {
    setupDragDrop(uploadArea, fileInput, handleFileSelect) {
        if (!uploadArea || !fileInput) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        // Handle dropped files
        uploadArea.addEventListener('drop', event => {
            const dt = event.dataTransfer;
            const files = dt.files;

            handleFiles(files);
        }, false);

        // Handle clicked files
        fileInput.addEventListener('change', event => {
            handleFiles(event.target.files);
        }, false);

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        function highlight(e) {
            uploadArea.classList.add('highlight');
        }

        function unhighlight(e) {
            uploadArea.classList.remove('highlight');
        }

        function handleFiles(files) {
            if (files && files[0]) {
                handleFileSelect(files[0]);
            }
        }
    }
}; 