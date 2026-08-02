(function() {
  function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  }

  const savedTheme = getCookie('theme') || 'light';
  document.documentElement.setAttribute('data-bs-theme', savedTheme);

  const savedHex = getCookie('accentColorHex');
  const savedRgb = getCookie('accentColorRgb');
  if (savedHex && savedRgb) {
    document.documentElement.style.setProperty('--bs-primary', savedHex);
    document.documentElement.style.setProperty('--bs-primary-rgb', savedRgb);
  }
})();

document.addEventListener('DOMContentLoaded', () => {
  const htmlElement = document.documentElement;
  const themeToggle = document.getElementById('themeToggle'); 
  const colorSelectors = document.querySelectorAll('.color-selector');

  // Helper to read cookies for UI sync
  function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  }

  function setCookie(name, value, days) {
    let expires = "";
    if (days) {
      const date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/"; 
  }

  // --- Sync UI on Load ---
  // The actual theme was already applied by the <head> script, 
  // we just need to update the icons and buttons to match.
  const currentTheme = htmlElement.getAttribute('data-bs-theme') || 'light';
  
  if (themeToggle) {
    themeToggle.checked = (currentTheme === 'dark');
    const iconContainer = themeToggle.closest('.d-flex.align-items-center.justify-content-between');
    const icon = iconContainer ? iconContainer.querySelector('i') : null;
    
    updateThemeIcon(currentTheme, icon);

    // Toggle Listener
    themeToggle.addEventListener('change', (e) => {
      const newTheme = e.target.checked ? 'dark' : 'light';
      htmlElement.setAttribute('data-bs-theme', newTheme);
      setCookie('theme', newTheme, 365); 
      updateThemeIcon(newTheme, icon);
      
      if (window.myChart && typeof updateChartTheme === 'function') { 
        updateChartTheme(newTheme); 
      }
    });
  }

  function updateThemeIcon(theme, icon) {
    if (!icon) return;
    if (theme === 'dark') {
      icon.classList.replace('bi-moon-stars-fill', 'bi-sun-fill');
      icon.classList.add('text-warning'); 
      icon.classList.remove('text-secondary');
    } else {
      icon.classList.replace('bi-sun-fill', 'bi-moon-stars-fill');
      icon.classList.remove('text-warning'); 
      icon.classList.add('text-secondary');
    }
  }

  // --- Sync Color UI on Load ---
  const savedHex = getCookie('accentColorHex') || '#6366f1';
  
  // Update the active ring on the correct color circle
  colorSelectors.forEach(btn => btn.classList.remove('active'));
  const activeBtn = Array.from(colorSelectors).find(btn => btn.getAttribute('data-color') === savedHex);
  if (activeBtn) activeBtn.classList.add('active');

  // Color Click Listeners
  colorSelectors.forEach(selector => {
    selector.addEventListener('click', () => {
      const hex = selector.getAttribute('data-color');
      const rgb = selector.getAttribute('data-rgb') || hexToRgb(hex); 
      
      // Apply immediately
      htmlElement.style.setProperty('--bs-primary', hex);
      htmlElement.style.setProperty('--bs-primary-rgb', rgb);
      
      // Update UI
      colorSelectors.forEach(btn => btn.classList.remove('active'));
      selector.classList.add('active');

      // Save to cookies
      setCookie('accentColorHex', hex, 365);
      setCookie('accentColorRgb', rgb, 365);

      // Update charts if they exist
      if (window.myChart) {
        window.myChart.data.datasets[0].backgroundColor = `rgba(${rgb}, 0.2)`;
        window.myChart.data.datasets[0].borderColor = hex;
        window.myChart.data.datasets[0].pointBackgroundColor = hex;
        window.myChart.update();
      }
    });
  });

  function hexToRgb(hex) {
    const bigint = parseInt(hex.replace('#', ''), 16);
    return `${(bigint >> 16) & 255}, ${(bigint >> 8) & 255}, ${bigint & 255}`;
  }
});
