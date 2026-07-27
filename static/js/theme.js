document.addEventListener('DOMContentLoaded', () => {
  const htmlElement = document.documentElement;
  const themeToggleBtn = document.getElementById('themeToggle');

  const icon = themeToggleBtn.querySelector('i');
  const styleTag = document.getElementById('theme-styles');
  const colorSelectors = document.querySelectorAll('.color-selector');
  const savedTheme = localStorage.getItem('theme') || 'light';

  htmlElement.setAttribute('data-bs-theme', savedTheme);
  updateThemeIcon(savedTheme);

  themeToggleBtn.addEventListener('click', () => {
    const currentTheme = htmlElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    htmlElement.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
    if(window.myChart) { updateChartTheme(newTheme); }
  });

  function updateThemeIcon(theme) {
    if (theme === 'dark') {
      icon.classList.replace('bi-moon-stars-fill', 'bi-sun-fill');
      icon.classList.add('text-warning'); icon.classList.remove('text-muted');
    } else {
      icon.classList.replace('bi-sun-fill', 'bi-moon-stars-fill');
      icon.classList.remove('text-warning'); icon.classList.add('text-muted');
    }
  }

  const defaultColor = { hex: '#6366f1', rgb: '99, 102, 241' }; // Indigo Standard
  const savedHex = localStorage.getItem('accentColorHex') || defaultColor.hex;
  const savedRgb = localStorage.getItem('accentColorRgb') || defaultColor.rgb;
  applyAccentColor(savedHex, savedRgb);

  colorSelectors.forEach(selector => {
    selector.addEventListener('click', () => {
      const hex = selector.getAttribute('data-color');
      const rgb = selector.getAttribute('data-rgb');
      applyAccentColor(hex, rgb);
      localStorage.setItem('accentColorHex', hex);
      localStorage.setItem('accentColorRgb', rgb);
      if(window.myChart) {
        window.myChart.data.datasets[0].backgroundColor = `rgba(${rgb}, 0.2)`;
        window.myChart.data.datasets[0].borderColor = hex;
        window.myChart.data.datasets[0].pointBackgroundColor = hex;
        window.myChart.update();
      }
    });
  });

  function applyAccentColor(hex, rgb) {
    const root = document.documentElement;
    root.style.setProperty('--bs-primary', hex);
    root.style.setProperty('--bs-primary-rgb', rgb);
    colorSelectors.forEach(btn => btn.style.border = '2px solid transparent');

    const activeBtn = Array.from(colorSelectors).find(btn => btn.getAttribute('data-color') === hex);
    if (activeBtn) {
      activeBtn.style.border = '2px solid var(--bs-body-color)';
    }
  }
});
