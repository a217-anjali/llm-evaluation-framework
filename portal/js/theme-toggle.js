// LLM Eval Hub - Theme Toggle JavaScript

document.addEventListener('DOMContentLoaded', function() {
  initializeThemeToggle();
});

function initializeThemeToggle() {
  const html = document.documentElement;
  const themeToggleBtn = document.querySelector('.theme-toggle');
  const storageKey = 'llm-eval-hub-theme';
  const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

  // Get current theme preference
  function getCurrentTheme() {
    // Check localStorage first
    const savedTheme = localStorage.getItem(storageKey);
    if (savedTheme) {
      return savedTheme;
    }

    // Check system preference
    if (darkModeQuery.matches) {
      return 'dark';
    }

    return 'light';
  }

  // Set theme
  function setTheme(theme) {
    if (theme === 'light') {
      html.setAttribute('data-theme', 'light');
      localStorage.setItem(storageKey, 'light');
      updateThemeIcon('light');
    } else {
      html.removeAttribute('data-theme');
      localStorage.setItem(storageKey, 'dark');
      updateThemeIcon('dark');
    }
  }

  // Toggle theme
  function toggleTheme() {
    const currentTheme = html.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
  }

  // Update theme icon
  function updateThemeIcon(theme) {
    if (!themeToggleBtn) return;

    const sunIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
    const moonIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';

    if (theme === 'light') {
      themeToggleBtn.innerHTML = moonIcon;
      themeToggleBtn.setAttribute('aria-label', 'Switch to dark mode');
      themeToggleBtn.title = 'Dark mode';
    } else {
      themeToggleBtn.innerHTML = sunIcon;
      themeToggleBtn.setAttribute('aria-label', 'Switch to light mode');
      themeToggleBtn.title = 'Light mode';
    }
  }

  // Initialize theme
  const initialTheme = getCurrentTheme();
  setTheme(initialTheme);

  // Setup theme toggle button
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function(e) {
      e.preventDefault();
      toggleTheme();
    });

    // Keyboard shortcut: Ctrl/Cmd + Shift + T
    document.addEventListener('keydown', function(e) {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        toggleTheme();
      }
    });

    // Add accessibility attributes
    themeToggleBtn.setAttribute('role', 'button');
    themeToggleBtn.setAttribute('tabindex', '0');
    themeToggleBtn.setAttribute('aria-pressed', initialTheme === 'light' ? 'false' : 'true');

    // Keyboard support for toggle button
    themeToggleBtn.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggleTheme();
      }
    });
  }

  // Listen for system theme changes
  darkModeQuery.addEventListener('change', function(e) {
    const savedTheme = localStorage.getItem(storageKey);
    // Only auto-update if no user preference is saved
    if (!savedTheme) {
      setTheme(e.matches ? 'dark' : 'light');
    }
  });

  // Export theme functions globally
  window.ThemeToggle = {
    setTheme: setTheme,
    getCurrentTheme: getCurrentTheme,
    toggleTheme: toggleTheme
  };
}

// Expose a function to set theme from external scripts
window.setAppTheme = function(theme) {
  if (window.ThemeToggle) {
    window.ThemeToggle.setTheme(theme);
  }
};

// Expose a function to get theme from external scripts
window.getAppTheme = function() {
  if (window.ThemeToggle) {
    return window.ThemeToggle.getCurrentTheme();
  }
  return 'dark';
};

// Add smooth transition for theme change
const style = document.createElement('style');
style.textContent = `
  html {
    transition: background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                color 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
`;
document.head.appendChild(style);
