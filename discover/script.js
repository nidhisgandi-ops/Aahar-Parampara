let foodData = [];
let currentIndex = -1;

// Generates a premium heritage-inspired mandala/pattern SVG
function generateHeritageSvg(name) {
    const hash = name.split('').reduce((acc, char) => char.charCodeAt(0) + acc, 0);
    const colorPrimary = '#d4af37';
    const colorSecondary = '#8a6d3b';
    const bgDark = '#0f1014';
    
    // Procedural mandala properties
    const spikes = 8 + (hash % 8);
    const rotation = hash % 360;
    
    let paths = '';
    for(let i = 0; i < spikes; i++) {
        const angle = (i * 360) / spikes;
        paths += `<path d="M200,110 L220,70 L200,20 L180,70 Z" fill="none" stroke="${colorPrimary}" stroke-width="1.5" opacity="0.6" transform="rotate(${angle} 200 110)" />`;
        paths += `<circle cx="200" cy="30" r="4" fill="${colorSecondary}" transform="rotate(${angle} 200 110)" />`;
    }

    return `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 220" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
        <rect width="100%" height="100%" fill="${bgDark}" />
        <g transform="translate(0, 0)">
            <circle cx="200" cy="110" r="90" fill="none" stroke="${colorSecondary}" stroke-width="1" opacity="0.4" stroke-dasharray="4 4"/>
            <circle cx="200" cy="110" r="70" fill="none" stroke="${colorPrimary}" stroke-width="2" opacity="0.5"/>
            <circle cx="200" cy="110" r="80" fill="none" stroke="${colorSecondary}" stroke-width="0.5" opacity="0.3"/>
            <g transform="rotate(${rotation} 200 110)">
                ${paths}
            </g>
            <circle cx="200" cy="110" r="20" fill="none" stroke="${colorPrimary}" stroke-width="2"/>
            <circle cx="200" cy="110" r="10" fill="${colorPrimary}" opacity="0.8"/>
        </g>
    </svg>`;
}

// Generate background particles
function createParticles(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + 'vw';
        particle.style.width = Math.random() * 4 + 1 + 'px';
        particle.style.height = particle.style.width;
        particle.style.animationDuration = (Math.random() * 10 + 5) + 's';
        particle.style.animationDelay = (Math.random() * 5) + 's';
        container.appendChild(particle);
    }
}

// Data fetching
async function loadData() {
    try {
        const response = await fetch('../master_database.json');
        if (!response.ok) throw new Error('Network response was not ok');
        const json = await response.json();
        
        // Flatten the dataset
        const dataset = json.master_dataset;
        for (const region in dataset) {
            dataset[region].forEach(food => {
                foodData.push({ ...food, region: region });
            });
        }
        return true;
    } catch (error) {
        console.error('Error loading data:', error);
        return false;
    }
}

function displayRandomFood() {
    if (foodData.length === 0) return;
    
    let newIndex = currentIndex;
    while (newIndex === currentIndex && foodData.length > 1) {
        newIndex = Math.floor(Math.random() * foodData.length);
    }
    currentIndex = newIndex;
    const food = foodData[currentIndex];
    
    document.getElementById('food-image-container').innerHTML = generateHeritageSvg(food.recipe_name || 'Traditional Food');
    document.getElementById('food-name').innerText = food.recipe_name || 'Lost Recipe';
    document.getElementById('food-region').innerText = food.region || 'Unknown Region';
    document.getElementById('food-heritage').innerText = food.cultural_context || 'Ancient history of this recipe has been lost to time.';
    
    const ingredientsList = document.getElementById('food-ingredients');
    ingredientsList.innerHTML = '';
    if (food.input_ingredients && food.input_ingredients.length > 0) {
        food.input_ingredients.forEach(ing => {
            const li = document.createElement('li');
            li.innerText = ing;
            ingredientsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.innerText = 'Ingredients unrecorded';
        ingredientsList.appendChild(li);
    }
    
    document.getElementById('food-status').innerText = food.source_status || 'Unverified Artifact';
}

function handleNextFood() {
    const card = document.getElementById('food-card');
    card.classList.add('transition-out');
    
    setTimeout(() => {
        displayRandomFood();
        window.scrollTo({ top: 0, behavior: 'smooth' });
        card.classList.remove('transition-out');
        card.classList.add('transition-in');
        
        setTimeout(() => card.classList.remove('transition-in'), 500);
    }, 500);
}

// App Initialization Router
window.addEventListener('DOMContentLoaded', async () => {
    
    // If we are on the landing page
    if (document.body.classList.contains('desktop-landing')) {
        createParticles('particles');
        
        // Generate QR code pointing to reveal.html
        const currentUrl = window.location.href;
        const targetUrl = currentUrl.replace('index.html', '').replace(/\/$/, '') + '/reveal.html';
        
        // Using qrserver API for dynamic QR generation
        const qrImage = document.getElementById('dynamic-qr');
        qrImage.src = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(targetUrl)}&color=000000&bgcolor=ffffff`;
    } 
    
    // If we are on the mobile app
    else if (document.body.classList.contains('mobile-app')) {
        createParticles('loading-particles');
        
        const dataLoaded = await loadData();
        
        // Cinematic delay (3.5s total animation sequence)
        setTimeout(() => {
            const loadingSeq = document.getElementById('loading-sequence');
            loadingSeq.style.opacity = '0';
            
            setTimeout(() => {
                loadingSeq.classList.add('hidden');
                
                const revealContainer = document.getElementById('reveal-container');
                revealContainer.classList.remove('hidden');
                
                if (dataLoaded) {
                    displayRandomFood();
                } else {
                    document.getElementById('food-name').innerText = 'Data Artifact Missing';
                }
            }, 1500); // Wait for fade out
        }, 3000); // Wait for cinematic reveal

        // Button listener
        document.getElementById('btn-discover').addEventListener('click', handleNextFood);
    }
});
