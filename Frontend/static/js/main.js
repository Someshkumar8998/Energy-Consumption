
document.addEventListener('DOMContentLoaded', () => {
    // Live Stats Simulation
    const stats = document.querySelectorAll('.live-stat-value');
    
    setInterval(() => {
        stats.forEach(stat => {
            // Randomly fluctuate values slightly to simulate real-time data
            let currentVal = parseFloat(stat.innerText.replace(/[^0-9.]/g, '')) || 0;
            let change = (Math.random() - 0.5) * 2; // Random flux between -1 and 1
            let newVal = Math.max(0, currentVal + change);
            
            // Format based on context (simple heuristic)
            if (stat.innerText.includes('kW')) {
                stat.innerText = newVal.toFixed(2) + ' kW';
            } else if (stat.innerText.includes('%')) {
                stat.innerText = Math.min(100, newVal).toFixed(1) + '%';
            } else {
                stat.innerText = newVal.toFixed(1); // Default
            }
        });
    }, 2000); // Update every 2 seconds

    // Smooth Scroll for Anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Form input animations
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });
        input.addEventListener('blur', () => {
            if (!input.value) {
                input.parentElement.classList.remove('focused');
            }
        });
    });

    // Add 'fade-in' class to elements as they scroll into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Stop observing once visible if desired
                // observer.unobserve(entry.target); 
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.glass-card, .section-title').forEach(el => {
        el.classList.add('fade-on-scroll');
        observer.observe(el);
    });
});

// Helper for method toggle in predict.html
function showMethod(methodId) {
    // Hide all input sections
    document.querySelectorAll('.input-section').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.method-btn').forEach(el => el.classList.remove('active'));

    // Show target
    document.getElementById(methodId).style.display = 'block';
    
    // Highlight button
    // (Assuming buttons communicate via data-target or similar, or just passed ID logic needs refinement in HTML)
    // Finding button that triggered this or logic in HTML to pass 'this'
    // For now, let's rely on the HTML structure handling class toggling via onclick wrapper if needed
    // or we can select by ID if buttons have IDs matching the method.
    
    // Simplistic approach for now matching existing inline JS logic but moved here if we want clean separation
    // But since the HTML calls showMethod('individual'), we need to handle button active state there or here.
}
