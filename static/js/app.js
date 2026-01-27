// State
let currentTab = 'generate';

document.addEventListener('DOMContentLoaded', () => {
    // 1. Attach Generate Button Listener
    const genBtn = document.getElementById('genBtn');
    if (genBtn) {
        // Fix: Remove legacy onclick to prevent double-firing
        genBtn.removeAttribute('onclick');
        genBtn.removeEventListener('click', generateImage);
        genBtn.addEventListener('click', generateImage);
    }

    // 2. Load History
    loadHistory();
});

function generateImage() {
    const btn = document.getElementById('genBtn');
    
    if (btn && btn.disabled) return;
    
    const promptInput = document.getElementById('promptInput');
    const styleSelect = document.getElementById('styleSelect');
    const ratioSelect = document.getElementById('ratioSelect');
    
    if (!promptInput || !styleSelect || !ratioSelect) return;

    const prompt = promptInput.value;
    const style = styleSelect.value;
    const ratio = ratioSelect.value;
    
    // UI Updates
    const btnSpan = btn.querySelector('span');
    const btnIcon = btn.querySelector('i');
    const loader = document.getElementById('loader');
    const preview = document.getElementById('previewImage');
    const empty = document.getElementById('emptyState');

    if (!prompt) {
        promptInput.style.borderColor = '#f43f5e';
        setTimeout(() => promptInput.style.borderColor = 'rgba(255,255,255,0.1)', 1000);
        return;
    }

    // Loading State
    btn.disabled = true;
    btnSpan.textContent = 'Dreaming...';
    btnIcon.className = 'fas fa-spinner fa-spin'; 
    
    loader.style.display = 'block';
    empty.style.display = 'none';
    preview.style.display = 'none';  

    fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            prompt: prompt, 
            style: style, 
            aspect_ratio: ratio
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.image) {
            preview.src = data.image;
            preview.onload = () => {
                preview.style.display = 'block';
                loader.style.display = 'none';
            };
            loadHistory();
        } else {
            handleError(empty, loader, data.error);
        }
    })
    .catch(err => {
        console.error("Fetch error:", err);
        handleError(empty, loader, "Network error");
    })
    .finally(() => {
        btn.disabled = false;
        btnSpan.textContent = 'Generate Art';
        btnIcon.className = 'fas fa-wand-magic-sparkles';
    });
}

function enhancePrompt() {
    const promptInput = document.getElementById('promptInput');
    const enhancers = [
        "highly detailed", "8k resolution", "masterpiece", 
        "cinematic lighting", "sharp focus", "intricate details"
    ];
    
    let currentVal = promptInput.value.trim();
    if(currentVal) {
        if(!currentVal.toLowerCase().includes("8k")) {
            promptInput.value = currentVal + ", " + enhancers.join(", ");
        }
    } else {
        promptInput.placeholder = "Enter a basic idea first, then click Enhance!";
    }
}

function toggleEditProfile() {
    const section = document.getElementById('editProfileSection');
    if (section) {
        if (section.style.display === 'none' || !section.style.display) {
            section.style.display = 'block';
            section.style.animation = 'slideDown 0.3s ease-out';
            section.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            section.style.display = 'none';
        }
    }
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