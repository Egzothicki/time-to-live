document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form'); // Target the form on the page

    // Ensure the form is detected
    if (form) {
        // Listen for Enter key press
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault(); // Prevent the default form submission
                form.submit(); // Submit the form (login or register)
            }
        });
    } else {
        console.log('No form detected on the page.');
    }
});