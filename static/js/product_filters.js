JavaScript File (product_filters.js)
// ================================
// LUXURY PRODUCT FILTERS
// ================================

document.addEventListener('DOMContentLoaded', function() {
  
  // ================================
  // MOBILE SIDEBAR TOGGLE
  // ================================
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.overlay');
  const filterToggle = document.querySelector('.filter-toggle');
  const closeMobile = document.querySelector('.btn-close-mobile');

  if (filterToggle) {
    filterToggle.addEventListener('click', () => {
      sidebar.classList.add('open');
      overlay.classList.add('show');
      document.body.style.overflow = 'hidden';
    });
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('show');
    document.body.style.overflow = '';
  }

  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  if (closeMobile) {
    closeMobile.addEventListener('click', closeSidebar);
  }

  // ================================
  // DUAL RANGE SLIDER
  // ================================
  const minPriceInput = document.getElementById('minPrice');
  const maxPriceInput = document.getElementById('maxPrice');
  const minPriceLabel = document.getElementById('minPriceLabel');
  const maxPriceLabel = document.getElementById('maxPriceLabel');

  function formatPrice(value) {
    return parseInt(value).toLocaleString() + ' TZS';
  }

  function updatePriceLabels() {
    let minVal = parseInt(minPriceInput.value);
    let maxVal = parseInt(maxPriceInput.value);

    // Prevent overlap
    if (minVal > maxVal - 5000) {
      minVal = maxVal - 5000;
      minPriceInput.value = minVal;
    }

    minPriceLabel.textContent = formatPrice(minVal);
    maxPriceLabel.textContent = formatPrice(maxVal);
  }

  if (minPriceInput && maxPriceInput) {
    minPriceInput.addEventListener('input', updatePriceLabels);
    maxPriceInput.addEventListener('input', updatePriceLabels);
    
    // Auto-submit on desktop
    if (window.innerWidth >= 1024) {
      let debounceTimer;
      function autoSubmit() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          document.getElementById('filterForm').submit();
        }, 500);
      }
      minPriceInput.addEventListener('change', autoSubmit);
      maxPriceInput.addEventListener('change', autoSubmit);
    }

    // Initialize
    updatePriceLabels();
  }

  // ================================
  // QUICK SELECT BUTTONS
  // ================================
  const quickSelectButtons = document.querySelectorAll('.btn-quick-select');
  
  quickSelectButtons.forEach(button => {
    button.addEventListener('click', function() {
      const min = this.dataset.min;
      const max = this.dataset.max;
      
      minPriceInput.value = min;
      maxPriceInput.value = max;
      updatePriceLabels();

      // Auto-submit on desktop
      if (window.innerWidth >= 1024) {
        setTimeout(() => {
          document.getElementById('filterForm').submit();
        }, 300);
      }
    });
  });

  // ================================
  // AUTO-SUBMIT CHECKBOXES (Desktop)
  // ================================
  if (window.innerWidth >= 1024) {
    const checkboxes = document.querySelectorAll('.category-checkbox');
    checkboxes.forEach(checkbox => {
      checkbox.addEventListener('change', function() {
        setTimeout(() => {
          document.getElementById('filterForm').submit();
        }, 300);
      });
    });
  }

  // ================================
  // PRODUCT IMAGE CAROUSEL
  // ================================
  window.imageIndex = {};

  window.showImage = function(productId, index) {
    const images = document.querySelectorAll('.product-' + productId);
    images.forEach(img => img.classList.remove('active'));
    if (images[index]) {
      images[index].classList.add('active');
      window.imageIndex[productId] = index;
    }
  };

  window.nextImage = function(productId) {
    const images = document.querySelectorAll('.product-' + productId);
    let index = window.imageIndex[productId] ?? 0;
    window.showImage(productId, (index + 1) % images.length);
  };

  window.prevImage = function(productId) {
    const images = document.querySelectorAll('.product-' + productId);
    let index = window.imageIndex[productId] ?? 0;
    window.showImage(productId, (index - 1 + images.length) % images.length);
  };

});