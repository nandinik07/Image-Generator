// State
let currentTab = 'generate';

// Functions
function generateImage() {
    const prompt = document.getElementById('promptInput').value;
    const style = document.getElementById('styleSelect').value;
    const ratio = document.getElementById('ratioSelect').value;
    const btn = document.getElementById('genBtn');
    const btnSpan = btn.querySelector('span');
    const btnIcon = btn.querySelector('i');
    
    const loader = document.getElementById('loader');
    const preview = document.getElementById('previewImage');
    const empty = document.getElementById('emptyState');

    if (!prompt) {
        // Simple shake animation for visual feedback if empty
        const input = document.getElementById('promptInput');
        input.style.borderColor = '#f43f5e';
        setTimeout(() => input.style.borderColor = 'rgba(255,255,255,0.1)', 1000);
        return;
    }

    // UI Loading State
    btn.disabled = true;
    btnSpan.textContent = 'Dreaming...';
    btnIcon.className = 'fas fa-spinner fa-spin'; // Change icon to spinner
    
    loader.style.display = 'block';
    empty.style.display = 'none';
    preview.style.display = 'none';

    fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt, style: style, aspect_ratio: ratio })
    })
    .then(response => response.json())
    .then(data => {
        if(data.image) {
            preview.src = data.image;
            preview.onload = () => {
                preview.style.display = 'block';
                loader.style.display = 'none';
            };
            loadHistory(); // Refresh history
        } else {
            handleError(empty, loader);
        }
    })
    .catch(err => {
        console.error(err);
        handleError(empty, loader);
    })
    .finally(() => {
        // Reset Button
        btn.disabled = false;
        btnSpan.textContent = 'Generate Art';
        btnIcon.className = 'fas fa-wand-magic-sparkles';
    });
}

function handleError(emptyState, loader) {
    alert("Generation failed. Please try again.");
    emptyState.style.display = 'block';
    loader.style.display = 'none';
}

function loadHistory() {
    const grid = document.getElementById('historyGrid');
    const countBadge = document.getElementById('historyCount');
    
    fetch('/api/history')
    .then(res => res.json())
    .then(data => {
        grid.innerHTML = '';
        if(countBadge) countBadge.textContent = data.length;
        
        data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'history-item';
            div.onclick = () => {
                const preview = document.getElementById('previewImage');
                const empty = document.getElementById('emptyState');
                
                // Show loader briefly to make it feel responsive
                preview.style.opacity = '0.5';
                preview.src = item.image_data;
                
                preview.onload = () => {
                    preview.style.opacity = '1';
                    preview.style.display = 'block';
                }
                
                empty.style.display = 'none';
            };
            div.innerHTML = `<img src="${item.image_data}" alt="Art" loading="lazy">`;
            grid.appendChild(div);
        });
    });
}

function scrollToHistory() {
    const section = document.querySelector('.history-section');
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
        // Also flash the background slightly
        section.style.backgroundColor = 'rgba(255,255,255,0.05)';
        setTimeout(() => section.style.backgroundColor = 'transparent', 500);
    }
}

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
});