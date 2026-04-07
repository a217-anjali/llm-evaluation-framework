// LLM Eval Hub - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
  initializeIntersectionObserver();
  initializeHamburgerMenu();
  initializeAnchorLinks();
  initializeActiveNavLink();
  initializeBackToTopButton();
});

// Intersection Observer for Scroll Animations
function initializeIntersectionObserver() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe all elements with animation classes
  const animatedElements = document.querySelectorAll(
    '.fade-in, .slide-up, .slide-left, .slide-right, .scale-in, .fade-in-blur'
  );

  animatedElements.forEach(function(element) {
    observer.observe(element);
  });

  // Observe cards for animation
  const cards = document.querySelectorAll('.card');
  cards.forEach(function(card) {
    card.classList.add('fade-in');
    observer.observe(card);
  });

  // Observe timeline items
  const timelineItems = document.querySelectorAll('.timeline-item');
  timelineItems.forEach(function(item) {
    item.classList.add('slide-up');
    observer.observe(item);
  });
}

// Mobile Hamburger Menu Toggle
function initializeHamburgerMenu() {
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', function() {
      hamburger.classList.toggle('active');
      navLinks.classList.toggle('active');
    });

    // Close menu when a link is clicked
    const links = navLinks.querySelectorAll('a');
    links.forEach(function(link) {
      link.addEventListener('click', function() {
        hamburger.classList.remove('active');
        navLinks.classList.remove('active');
      });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
      const isClickInsideNav = hamburger.contains(event.target) || navLinks.contains(event.target);
      if (!isClickInsideNav && navLinks.classList.contains('active')) {
        hamburger.classList.remove('active');
        navLinks.classList.remove('active');
      }
    });
  }
}

// Smooth Scroll for Anchor Links
function initializeAnchorLinks() {
  const anchorLinks = document.querySelectorAll('a[href^="#"]');

  anchorLinks.forEach(function(link) {
    link.addEventListener('click', function(e) {
      const href = link.getAttribute('href');

      if (href === '#') {
        return;
      }

      const targetElement = document.querySelector(href);

      if (targetElement) {
        e.preventDefault();
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
}

// Active Nav Link Highlighting on Scroll
function initializeActiveNavLink() {
  const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');
  const sections = document.querySelectorAll('section[id]');

  function updateActiveLink() {
    let current = '';

    sections.forEach(function(section) {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;

      if (window.scrollY >= sectionTop - 100) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(function(link) {
      link.classList.remove('active');
      if (link.getAttribute('href') === '#' + current) {
        link.classList.add('active');
      }
    });
  }

  window.addEventListener('scroll', updateActiveLink);
  window.addEventListener('load', updateActiveLink);
}

// Back to Top Button
function initializeBackToTopButton() {
  const backToTopBtn = document.querySelector('.back-to-top');

  if (!backToTopBtn) {
    // Create the button if it doesn't exist
    const button = document.createElement('button');
    button.className = 'back-to-top';
    button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"></polyline></svg>';
    document.body.appendChild(button);

    window.addEventListener('scroll', function() {
      if (window.scrollY > 300) {
        button.classList.add('visible');
      } else {
        button.classList.remove('visible');
      }
    });

    button.addEventListener('click', function() {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  } else {
    // Use existing button
    window.addEventListener('scroll', function() {
      if (window.scrollY > 300) {
        backToTopBtn.classList.add('visible');
      } else {
        backToTopBtn.classList.remove('visible');
      }
    });

    backToTopBtn.addEventListener('click', function() {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }
}

// Glossary Toggle Functionality
function initializeGlossary() {
  const glossaryItems = document.querySelectorAll('.glossary-item');

  glossaryItems.forEach(function(item) {
    const term = item.querySelector('.glossary-term');

    if (term) {
      term.addEventListener('click', function() {
        item.classList.toggle('open');
      });

      // Allow keyboard navigation
      term.setAttribute('role', 'button');
      term.setAttribute('tabindex', '0');

      term.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          item.classList.toggle('open');
        }
      });
    }
  });
}

// Initialize glossary on load
document.addEventListener('DOMContentLoaded', initializeGlossary);

// Utility function to check if element is visible in viewport
function isElementInViewport(el) {
  const rect = el.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
}

// Utility function to add animation classes dynamically
function addScrollAnimation(selector, animationClass, delay = 0) {
  const elements = document.querySelectorAll(selector);

  elements.forEach(function(el, index) {
    setTimeout(function() {
      el.classList.add(animationClass);
    }, delay * index);
  });
}

// Utility function to get query parameters
function getQueryParameter(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

// Utility function to set query parameter
function setQueryParameter(param, value) {
  const url = new URL(window.location);
  url.searchParams.set(param, value);
  window.history.replaceState({}, document.title, url);
}

// Debounce function for scroll/resize events
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Throttle function for frequent events
function throttle(func, limit) {
  let inThrottle;
  return function() {
    if (!inThrottle) {
      func.apply(this, arguments);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

// Initialize on page load
window.addEventListener('load', function() {
  // Add fade-in animation to all cards
  const cards = document.querySelectorAll('.card');
  cards.forEach(function(card, index) {
    setTimeout(function() {
      card.classList.add('fade-in', 'in-view');
    }, index * 100);
  });
});

// Handle dynamic content updates
function reinitializeAnimations() {
  // Re-run intersection observer for any newly added elements
  const animatedElements = document.querySelectorAll(
    '.fade-in:not(.in-view), .slide-up:not(.in-view), .slide-left:not(.in-view), .slide-right:not(.in-view)'
  );

  if ('IntersectionObserver' in window && animatedElements.length > 0) {
    const observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    animatedElements.forEach(function(element) {
      observer.observe(element);
    });
  }
}

// Export functions for external use
window.LLMEvalHub = {
  isElementInViewport: isElementInViewport,
  addScrollAnimation: addScrollAnimation,
  getQueryParameter: getQueryParameter,
  setQueryParameter: setQueryParameter,
  debounce: debounce,
  throttle: throttle,
  reinitializeAnimations: reinitializeAnimations
};
