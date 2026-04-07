// LLM Eval Hub - Search and Filter JavaScript

document.addEventListener('DOMContentLoaded', function() {
  initializeBenchmarkFilters();
  initializeCategoryToggle();
  initializeSearch();
});

// Initialize benchmark category filters
function initializeBenchmarkFilters() {
  const filterButtons = document.querySelectorAll('[data-filter]');
  const benchmarkCards = document.querySelectorAll('[data-category]');

  if (filterButtons.length === 0 || benchmarkCards.length === 0) {
    return;
  }

  filterButtons.forEach(function(button) {
    button.addEventListener('click', function() {
      const filter = button.getAttribute('data-filter');

      // Update active state
      filterButtons.forEach(function(btn) {
        btn.classList.remove('active');
      });
      button.classList.add('active');

      // Filter cards
      filterCards(benchmarkCards, 'data-category', filter);
    });
  });
}

// Initialize category toggle buttons
function initializeCategoryToggle() {
  const categoryButtons = document.querySelectorAll('[data-category-toggle]');
  const categoryCards = document.querySelectorAll('[data-category]');

  if (categoryButtons.length === 0 || categoryCards.length === 0) {
    return;
  }

  categoryButtons.forEach(function(button) {
    button.addEventListener('click', function() {
      const category = button.getAttribute('data-category-toggle');

      // Toggle active state
      button.classList.toggle('active');

      // Get all active categories
      const activeCategories = Array.from(categoryButtons)
        .filter(function(btn) {
          return btn.classList.contains('active');
        })
        .map(function(btn) {
          return btn.getAttribute('data-category-toggle');
        });

      // Filter cards based on active categories
      filterCardsByMultiple(categoryCards, 'data-category', activeCategories);
    });
  });
}

// Initialize search functionality
function initializeSearch() {
  const searchInput = document.querySelector('[data-search]');
  const searchableCards = document.querySelectorAll('[data-searchable]');

  if (!searchInput || searchableCards.length === 0) {
    return;
  }

  searchInput.addEventListener('input', function() {
    const searchTerm = searchInput.value.toLowerCase().trim();

    if (searchTerm === '') {
      // Show all cards when search is empty
      searchableCards.forEach(function(card) {
        card.style.display = '';
        card.classList.add('fade-in', 'in-view');
      });
      return;
    }

    // Filter cards based on search term
    searchableCards.forEach(function(card) {
      const cardText = card.textContent.toLowerCase();
      const matches = cardText.includes(searchTerm);

      if (matches) {
        card.style.display = '';
        card.classList.add('fade-in', 'in-view');
      } else {
        card.style.display = 'none';
      }
    });

    // Announce search results to screen readers
    const visibleCount = Array.from(searchableCards).filter(function(card) {
      return card.style.display !== 'none';
    }).length;

    announceToScreenReader(`Found ${visibleCount} results for "${searchTerm}"`);
  });

  // Clear search on button click (if exists)
  const clearButton = document.querySelector('[data-search-clear]');
  if (clearButton) {
    clearButton.addEventListener('click', function() {
      searchInput.value = '';
      searchInput.dispatchEvent(new Event('input'));
      searchInput.focus();
    });
  }
}

// Filter cards by single attribute value
function filterCards(cards, attribute, value) {
  let visibleCount = 0;

  cards.forEach(function(card) {
    const cardValue = card.getAttribute(attribute);

    if (value === 'all' || cardValue === value) {
      card.style.display = '';
      card.classList.add('fade-in', 'in-view');
      visibleCount++;
    } else {
      card.style.display = 'none';
    }
  });

  announceToScreenReader(`Showing ${visibleCount} results`);
}

// Filter cards by multiple attribute values
function filterCardsByMultiple(cards, attribute, values) {
  let visibleCount = 0;

  cards.forEach(function(card) {
    const cardValue = card.getAttribute(attribute);

    // If no active filters, show all
    if (values.length === 0) {
      card.style.display = '';
      card.classList.add('fade-in', 'in-view');
      visibleCount++;
    } else if (values.includes(cardValue)) {
      card.style.display = '';
      card.classList.add('fade-in', 'in-view');
      visibleCount++;
    } else {
      card.style.display = 'none';
    }
  });

  announceToScreenReader(`Showing ${visibleCount} results`);
}

// Advanced search with multiple criteria
function advancedSearch(cards, criteria) {
  let visibleCount = 0;

  cards.forEach(function(card) {
    let matches = true;

    // Check each criterion
    for (const key in criteria) {
      if (criteria.hasOwnProperty(key)) {
        const value = criteria[key];
        const cardValue = card.getAttribute(`data-${key}`);

        if (value && cardValue !== value) {
          matches = false;
          break;
        }
      }
    }

    if (matches) {
      card.style.display = '';
      card.classList.add('fade-in', 'in-view');
      visibleCount++;
    } else {
      card.style.display = 'none';
    }
  });

  announceToScreenReader(`Found ${visibleCount} matching results`);
  return visibleCount;
}

// Sort cards by attribute
function sortCards(container, attribute, direction = 'asc') {
  const cards = Array.from(container.querySelectorAll('[data-sortable]'));

  cards.sort(function(a, b) {
    const aValue = a.getAttribute(`data-${attribute}`);
    const bValue = b.getAttribute(`data-${attribute}`);

    // Try to parse as numbers
    const aNum = parseFloat(aValue);
    const bNum = parseFloat(bValue);

    if (!isNaN(aNum) && !isNaN(bNum)) {
      return direction === 'asc' ? aNum - bNum : bNum - aNum;
    }

    // String comparison
    if (direction === 'asc') {
      return aValue.localeCompare(bValue);
    } else {
      return bValue.localeCompare(aValue);
    }
  });

  // Reorder cards in DOM
  cards.forEach(function(card) {
    container.appendChild(card);
  });
}

// Get active filters
function getActiveFilters() {
  const filterButtons = document.querySelectorAll('[data-filter].active');
  const filters = {};

  filterButtons.forEach(function(button) {
    filters[button.getAttribute('data-filter')] = true;
  });

  return filters;
}

// Reset all filters
function resetFilters() {
  // Clear active classes
  document.querySelectorAll('[data-filter].active').forEach(function(button) {
    button.classList.remove('active');
  });

  document.querySelectorAll('[data-category-toggle].active').forEach(function(button) {
    button.classList.remove('active');
  });

  // Clear search
  const searchInput = document.querySelector('[data-search]');
  if (searchInput) {
    searchInput.value = '';
    searchInput.dispatchEvent(new Event('input'));
  }

  // Show all cards
  document.querySelectorAll('[data-category], [data-searchable]').forEach(function(card) {
    card.style.display = '';
  });

  announceToScreenReader('Filters cleared');
}

// Text search with regex support
function advancedTextSearch(cards, pattern, flags = 'gi') {
  let visibleCount = 0;

  try {
    const regex = new RegExp(pattern, flags);

    cards.forEach(function(card) {
      const cardText = card.textContent;

      if (regex.test(cardText)) {
        card.style.display = '';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    announceToScreenReader(`Found ${visibleCount} results`);
  } catch (e) {
    console.error('Invalid regex pattern:', e);
    announceToScreenReader('Invalid search pattern');
  }

  return visibleCount;
}

// Highlight search terms in cards
function highlightSearchTerms(cards, term) {
  const regex = new RegExp(`(${term})`, 'gi');

  cards.forEach(function(card) {
    if (card.style.display !== 'none') {
      const elements = card.querySelectorAll('h3, p, .card-title, .card-description');

      elements.forEach(function(element) {
        const text = element.textContent;
        if (regex.test(text)) {
          element.innerHTML = text.replace(regex, '<mark style="background-color: rgba(255, 255, 0, 0.3);">$1</mark>');
        }
      });
    }
  });
}

// Clear highlights
function clearHighlights(cards) {
  cards.forEach(function(card) {
    const marks = card.querySelectorAll('mark');
    marks.forEach(function(mark) {
      const parent = mark.parentNode;
      parent.replaceChild(document.createTextNode(mark.textContent), mark);
      parent.normalize();
    });
  });
}

// Announce to screen readers
function announceToScreenReader(message) {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.style.position = 'absolute';
  announcement.style.left = '-10000px';
  announcement.style.width = '1px';
  announcement.style.height = '1px';
  announcement.style.overflow = 'hidden';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  setTimeout(function() {
    document.body.removeChild(announcement);
  }, 1000);
}

// Get search results count
function getSearchResultsCount() {
  const visibleCards = document.querySelectorAll('[data-searchable]:not([style*="display: none"])');
  return visibleCards.length;
}

// Debounced search for performance
function createDebouncedSearch(delay = 300) {
  let timeout;

  return function(searchFunction) {
    return function() {
      clearTimeout(timeout);
      timeout = setTimeout(searchFunction, delay);
    };
  };
}

// Export functions globally
window.BenchmarkSearch = {
  filterCards: filterCards,
  filterCardsByMultiple: filterCardsByMultiple,
  advancedSearch: advancedSearch,
  sortCards: sortCards,
  getActiveFilters: getActiveFilters,
  resetFilters: resetFilters,
  advancedTextSearch: advancedTextSearch,
  highlightSearchTerms: highlightSearchTerms,
  clearHighlights: clearHighlights,
  getSearchResultsCount: getSearchResultsCount,
  createDebouncedSearch: createDebouncedSearch
};
