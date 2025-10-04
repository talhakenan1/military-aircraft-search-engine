// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const topKSelect = document.getElementById('topKSelect');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultsInfo = document.getElementById('resultsInfo');
const resultsText = document.getElementById('resultsText');
const errorMessage = document.getElementById('errorMessage');
const resultsContainer = document.getElementById('resultsContainer');
const imageModal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const modalCaption = document.getElementById('modalCaption');
const modalClose = document.querySelector('.modal-close');

// Popular tags
const popularTags = document.querySelectorAll('.popular-tag');
const popularSection = document.getElementById('popularSection');
const resultsHeader = document.getElementById('resultsHeader');
const resultsCount = document.getElementById('resultsCount');
const resultsCountText = document.getElementById('resultsCountText');

// Event Listeners
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch();
    }
});

searchInput.addEventListener('input', () => {
    if (searchInput.value.trim()) {
        performSearch();
    }
});

// Popular tag click handlers
popularTags.forEach(tag => {
    tag.addEventListener('click', () => {
        const query = tag.getAttribute('data-query');
        searchInput.value = query;
        performSearch();
    });
});

// Modal close handlers
modalClose.addEventListener('click', closeModal);
imageModal.addEventListener('click', (e) => {
    if (e.target === imageModal) {
        closeModal();
    }
});

// Keyboard handler for modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && imageModal.style.display === 'block') {
        closeModal();
    }
});

/**
 * Perform search operation
 */
async function performSearch() {
    const query = searchInput.value.trim();
    
    // Validate query
    if (!query) {
        showError('Lütfen bir arama terimi girin.');
        return;
    }
    
    // Get top_k value
    const topK = parseInt(topKSelect.value);
    
    // Show loading, hide previous results
    showLoading();
    hideError();
    hideResults();
    
    try {
        // Make API request
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                top_k: topK
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Arama başarısız oldu.');
        }
        
        if (data.success) {
            displayResults(data);
        } else {
            throw new Error(data.message || 'Beklenmeyen bir hata oluştu.');
        }
        
    } catch (error) {
        console.error('Search error:', error);
        showError(error.message || 'Arama sırasında bir hata oluştu. Lütfen tekrar deneyin.');
    } finally {
        hideLoading();
    }
}

/**
 * Display search results
 */
function displayResults(data) {
    const { query, results, total_results } = data;
    
    // Hide popular section and show results header
    popularSection.style.display = 'none';
    resultsHeader.style.display = 'block';
    
    // Show results count
    resultsCountText.textContent = `Yaklaşık ${total_results} sonuç bulundu`;
    resultsCount.style.display = 'block';
    
    // Clear previous results
    resultsContainer.innerHTML = '';
    
    if (total_results === 0) {
        resultsContainer.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 4rem; background: var(--card-bg); border-radius: 12px; box-shadow: var(--shadow);">
                <p style="font-size: 1.1rem; color: var(--text-secondary);">
                    Sonuç bulunamadı. Farklı bir arama terimi deneyin.
                </p>
            </div>
        `;
        return;
    }
    
    // Create result cards
    results.forEach(result => {
        const card = createResultCard(result);
        resultsContainer.appendChild(card);
    });
}

/**
 * Create a result card element
 */
function createResultCard(result) {
    const card = document.createElement('div');
    card.className = 'result-card';
    
    // Format similarity score as percentage
    const scorePercent = (result.similarity_score * 100).toFixed(1);
    
    card.innerHTML = `
        <div class="result-image-container">
            <img 
                src="${result.image_url}" 
                alt="${result.filename}"
                class="result-image"
                loading="lazy"
                onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22%3E%3Crect fill=%22%23f1f5f9%22 width=%22100%22 height=%22100%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%2394a3b8%22%3EImage%20not%20found%3C/text%3E%3C/svg%3E'"
            >
        </div>
        <div class="result-info">
            <div class="result-filename" title="${result.filename}">${result.filename}</div>
            <div>
                <span class="result-score">📊 ${scorePercent}%</span>
                <span class="result-rank">#${result.rank}</span>
            </div>
        </div>
    `;
    
    // Add click handler to open modal
    card.addEventListener('click', () => {
        openModal(result);
    });
    
    return card;
}

/**
 * Open image modal
 */
function openModal(result) {
    modalImage.src = result.image_url;
    modalCaption.innerHTML = `
        <strong>${result.filename}</strong><br>
        Similarity Score: ${(result.similarity_score * 100).toFixed(1)}% | Rank: #${result.rank}
    `;
    imageModal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

/**
 * Close image modal
 */
function closeModal() {
    imageModal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

/**
 * Show loading indicator
 */
function showLoading() {
    loadingIndicator.style.display = 'block';
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    loadingIndicator.style.display = 'none';
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.style.display = 'none';
}

/**
 * Hide results
 */
function hideResults() {
    resultsInfo.style.display = 'none';
    resultsContainer.innerHTML = '';
}

// Auto-focus on search input when page loads
window.addEventListener('load', () => {
    searchInput.focus();
});
