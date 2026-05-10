/**
 * Accessibility Utilities for Traveloop
 * Handles keyboard navigation, ARIA labels, focus management
 */

const Accessibility = {
  /**
   * Initialize accessibility features
   */
  init() {
    this.setupKeyboardNavigation();
    this.setupFocusManagement();
    this.announceToScreenReaders('Page loaded');
  },

  /**
   * Setup keyboard navigation (Tab, Enter, Escape)
   */
  setupKeyboardNavigation() {
    // Allow Escape to close modals
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const modal = document.querySelector('[role="dialog"][aria-modal="true"]');
        if (modal) {
          this.closeModal(modal);
        }
      }

      // Allow Enter on buttons without form submission
      if (e.key === 'Enter' && e.target.hasAttribute('data-action')) {
        e.preventDefault();
        e.target.click();
      }
    });

    // Trap focus within modal dialogs
    document.addEventListener('focus', (e) => {
      const modal = document.querySelector('[role="dialog"][aria-modal="true"]');
      if (modal && !modal.contains(e.target)) {
        const focusableElements = modal.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length > 0) {
          focusableElements[0].focus();
        }
      }
    }, true);
  },

  /**
   * Setup visible focus indicators
   */
  setupFocusManagement() {
    // Show focus styles for keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        document.body.classList.add('keyboard-nav');
      }
    });

    document.addEventListener('mousedown', () => {
      document.body.classList.remove('keyboard-nav');
    });
  },

  /**
   * Close modal and restore focus
   */
  closeModal(modal) {
    const triggerButton = document.querySelector(`[aria-controls="${modal.id}"]`);
    modal.setAttribute('aria-hidden', 'true');
    modal.classList.add('hidden');
    if (triggerButton) {
      triggerButton.focus();
    }
  },

  /**
   * Announce message to screen readers
   */
  announceToScreenReaders(message, priority = 'polite') {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      announcement.remove();
    }, 3000);
  },

  /**
   * Update page title for screen readers
   */
  updatePageTitle(title) {
    document.title = title;
    const heading = document.querySelector('h1');
    if (heading) {
      heading.textContent = title;
    }
  },

  /**
   * Make element focusable
   */
  makeFocusable(element) {
    if (!element.hasAttribute('tabindex')) {
      element.setAttribute('tabindex', '0');
    }
  },

  /**
   * Set error message for form input
   */
  setErrorMessage(input, message) {
    input.setAttribute('aria-invalid', 'true');
    
    let errorId = input.id + '-error';
    let errorElement = document.getElementById(errorId);
    
    if (!errorElement) {
      errorElement = document.createElement('div');
      errorElement.id = errorId;
      errorElement.className = 'text-red-600 text-sm mt-1';
      input.parentNode.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    
    if (!input.getAttribute('aria-describedby')) {
      input.setAttribute('aria-describedby', errorId);
    }
  },

  /**
   * Clear error message
   */
  clearErrorMessage(input) {
    input.setAttribute('aria-invalid', 'false');
    const errorId = input.id + '-error';
    const errorElement = document.getElementById(errorId);
    if (errorElement) {
      errorElement.textContent = '';
    }
  },

  /**
   * Add accessible tooltip
   */
  addTooltip(element, text) {
    element.setAttribute('aria-label', text);
    element.setAttribute('role', 'tooltip');
  },

  /**
   * Make image decorative (hidden from screen readers)
   */
  markAsDecorative(img) {
    img.setAttribute('alt', '');
    img.setAttribute('aria-hidden', 'true');
  },

  /**
   * Initialize skip link for keyboard users
   */
  setupSkipLink() {
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link sr-only focus:not-sr-only';
    document.body.insertBefore(skipLink, document.body.firstChild);
  }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  Accessibility.init();
  Accessibility.setupSkipLink();
});
