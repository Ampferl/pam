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

  function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value}; expires=${date.toUTCString()}; path=/`;
  }

  function subgroupCookieKey(sourceKey, subgroupKey) {
    return `${sourceKey}::${subgroupKey}`;
  }

  const hiddenSources = new Set((getCookie('calendarHiddenSources') || '').split(',').filter(Boolean));
  const hiddenSubgroups = new Set((getCookie('calendarHiddenSubgroups') || '').split(',').filter(Boolean));

  function applyVisibility() {
    document.querySelectorAll('[data-source]').forEach(el => {
      const sourceKey = el.dataset.source;
      const subgroupKey = el.dataset.subgroup;
      const sourceHidden = hiddenSources.has(sourceKey);
      const subgroupHidden = !!subgroupKey && hiddenSubgroups.has(subgroupCookieKey(sourceKey, subgroupKey));
      el.style.display = (sourceHidden || subgroupHidden) ? 'none' : '';
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.source-toggle').forEach(cb => {
      const key = cb.dataset.sourceKey;
      cb.checked = !hiddenSources.has(key);

      const children = document.querySelectorAll(`.subgroup-toggle[data-source-key="${key}"]`);
      children.forEach(c => { c.disabled = !cb.checked; });

      cb.addEventListener('change', () => {
        cb.checked ? hiddenSources.delete(key) : hiddenSources.add(key);
        setCookie('calendarHiddenSources', Array.from(hiddenSources).join(','), 365);
        children.forEach(c => { c.disabled = !cb.checked; });
        applyVisibility();
      });
    });

    document.querySelectorAll('.subgroup-toggle').forEach(cb => {
      const sourceKey = cb.dataset.sourceKey;
      const subKey = cb.dataset.subgroupKey;
      const cookieKey = subgroupCookieKey(sourceKey, subKey);
      cb.checked = !hiddenSubgroups.has(cookieKey);

      cb.addEventListener('change', () => {
        cb.checked ? hiddenSubgroups.delete(cookieKey) : hiddenSubgroups.add(cookieKey);
        setCookie('calendarHiddenSubgroups', Array.from(hiddenSubgroups).join(','), 365);
        applyVisibility();
      });
    });

    applyVisibility();
  });
})();
