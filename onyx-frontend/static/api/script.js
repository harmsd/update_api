/* api/script.js — fetch wrapper with JWT refresh */
async function fetchWithRefresh(url, options = {}) {
  let res = await fetch(url, { ...options, credentials: 'include' });

  if (res.status === 401) {
    const refresh = await fetch('/jwt/refresh', {
      method:      'POST',
      credentials: 'include',
    });

    if (refresh.ok) {
      res = await fetch(url, { ...options, credentials: 'include' });
    } else {
      window.location.href = '/login/';
      return null;
    }
  }

  return res;
}

/* Global logout handler — works on any page that has #logout-btn */
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('logout-btn');
  if (!btn) return;

  btn.addEventListener('click', async () => {
    try {
      const response = await fetch('/login/logout', {
        method:      'POST',
        credentials: 'include',
      });
      window.location.href = response.redirected ? response.url : '/login/';
    } catch {
      window.location.href = '/login/';
    }
  });
});
