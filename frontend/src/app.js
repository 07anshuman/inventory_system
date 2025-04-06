document.addEventListener('DOMContentLoaded', function() {
    // Navigation handling
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show corresponding section
            const sectionId = this.getAttribute('data-section');
            document.getElementById(sectionId).classList.add('active');
        });
    });
    
    // Show error message
    window.showError = function(message) {
        alert(`Error: ${message}`);
    };
    
    // Format date for display
    window.formatDate = function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    };
    
    // Initialize all modules
    initSearch();
    initWaste();
    initSimulation();
    initPlacement();
    initRearrange();
    initImportExport();
    initLogs();
});

