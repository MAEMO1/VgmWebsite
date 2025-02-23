// Performance monitoring and Service Worker registration
document.addEventListener('DOMContentLoaded', function() {
    // Register Service Worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/js/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful');
            })
            .catch(err => {
                console.error('ServiceWorker registration failed:', err);
            });
    }

    // Performance monitoring
    if ('performance' in window && 'getEntriesByType' in window.performance) {
        // Monitor page load performance
        window.addEventListener('load', () => {
            const perfData = window.performance.getEntriesByType('navigation')[0];
            const metrics = {
                // Time to First Byte
                ttfb: perfData.responseStart - perfData.requestStart,
                // DOM Content Loaded
                dcl: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                // Load Complete
                loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
                // First Paint
                fp: performance.getEntriesByName('first-paint')[0]?.startTime,
                // First Contentful Paint
                fcp: performance.getEntriesByName('first-contentful-paint')[0]?.startTime
            };

            // Log performance metrics
            console.log('Performance Metrics:', metrics);
        });
    }

    // Intersection Observer for lazy loading
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });

    lazyImages.forEach(img => imageObserver.observe(img));

    // Enhanced form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add micro-interactions
    const interactiveElements = document.querySelectorAll('button, .nav-link, .btn');
    interactiveElements.forEach(element => {
        element.addEventListener('click', function(e) {
            const ripple = document.createElement('div');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size/2;
            const y = e.clientY - rect.top - size/2;
            
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
});
