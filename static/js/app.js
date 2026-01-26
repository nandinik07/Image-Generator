// State
let currentTab = 'generate';

document.addEventListener('DOMContentLoaded', () => {
    // 1. Attach Generate Button Listener
    const genBtn = document.getElementById('genBtn');
    if (genBtn) {
        // CRITICAL FIX: Remove legacy onclick from HTML if present to prevent double-firing
        genBtn.removeAttribute('onclick');
        
        // Remove old listener if we are re-initializing
        genBtn.removeEventListener('click', generateImage);
        genBtn.addEventListener('click', generateImage);
    }

    // 2. Load History on startup
    loadHistory();
});

// Functions
function generateImage() {
    const btn = document.getElementById('genBtn');
    
    // CRITICAL FIX: If button is already disabled (processing), stop immediately.
    // This prevents double-clicks or duplicate events from firing two requests.
    if (btn && btn.disabled) {
        console.log("Button disabled, skipping duplicate click.");
        return;
    }

    console.log("Generate button clicked");
    
    const promptInput = document.getElementById('promptInput');
    const styleSelect = document.getElementById('styleSelect');
    const ratioSelect = document.getElementById('ratioSelect');
    
    // Safety check
    if (!promptInput || !styleSelect || !ratioSelect) {
        console.error("Missing input elements");
        return;
    }

    const prompt = promptInput.value;
    const style = styleSelect.value;
    const ratio = ratioSelect.value;
    
    // Elements for UI updates
    const btnSpan = btn.querySelector('span');
    const btnIcon = btn.querySelector('i');
    
    const loader = document.getElementById('loader');
    const preview = document.getElementById('previewImage');
    const empty = document.getElementById('emptyState');

    if (!prompt) {
        // Simple shake animation for visual feedback if empty
        promptInput.style.borderColor = '#f43f5e';
        setTimeout(() => promptInput.style.borderColor = 'rgba(255,255,255,0.1)', 1000);
        return;
    }

    // UI Loading State
    btn.disabled = true;
    btnSpan.textContent = 'Dreaming...';
    btnIcon.className = 'fas fa-spinner fa-spin'; 
    
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
            handleError(empty, loader, data.error);
        }
    })
    .catch(err => {
        console.error("Fetch error:", err);
        handleError(empty, loader, "Network error");
    })
    .finally(() => {
        // Reset Button
        btn.disabled = false;
        btnSpan.textContent = 'Generate Art';
        btnIcon.className = 'fas fa-wand-magic-sparkles';
    });
}

function handleError(emptyState, loader, msg) {
    alert("Generation failed: " + (msg || "Unknown error"));
    emptyState.style.display = 'block';
    loader.style.display = 'none';
}

function loadHistory() {
    const grid = document.getElementById('historyGrid');
    const countBadge = document.getElementById('historyCount');
    
    if (!grid) return;

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
        section.style.backgroundColor = 'rgba(255,255,255,0.05)';
        setTimeout(() => section.style.backgroundColor = 'transparent', 500);
    }
} 