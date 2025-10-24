

/**
 * Shows a toast notification.
 * @param {string} message The message to display.
 * @param {boolean} isSuccess True for a success toast, false for an error toast.
 */
function showToast(message, isSuccess = true) {
    // This function assumes the toast HTML elements are present in the DOM.
    const toastId = isSuccess ? 'successToast' : 'errorToast';
    const messageId = isSuccess ? 'toastMessage' : 'errorMessage';

    const messageSpan = document.getElementById(messageId);
    if (messageSpan) {
        messageSpan.textContent = message;
    }

    const toastElement = document.getElementById(toastId);
    
    // Ensure bootstrap is loaded
    if (toastElement && typeof bootstrap !== 'undefined') {
        const toast = new bootstrap.Toast(toastElement, {
            animation: true,
            autohide: true,
            delay: 3000
        });
        toast.show();
    } else {
        // Fallback for when bootstrap or toast elements are not available
        console.error('Bootstrap JS not loaded or toast element not found.');
        alert(message);
    }
}