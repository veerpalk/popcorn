const locationTabs = document.querySelectorAll('.tab');

locationTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove 'active' class from all tabs
        locationTabs.forEach(t => t.classList.remove('active'));

        // Add 'active' class to the clicked tab
        tab.classList.add('active');
    });
});
