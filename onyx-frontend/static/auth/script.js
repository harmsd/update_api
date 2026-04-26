'use strict';

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  const btn  = document.getElementById('submitBtn');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('login').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!username || !password) {
      showError('Введите логин и пароль');
      return;
    }

    btn.disabled    = true;
    btn.textContent = 'Вход…';

    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch('/jwt/login', {
        method:  'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body:    formData,
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Ошибка авторизации');
      }

      if (data.role === 'admin') {
        window.location.href = '/main/';
      } else {
        window.location.href = '/updates/';
      }

    } catch (error) {
      showError(error.message || 'Неверное имя пользователя или пароль');
      btn.disabled    = false;
      btn.textContent = 'Войти';
    }
  });
});

function showError(msg) {
  const el = document.getElementById('errorAlert');
  if (!el) return;
  el.textContent = msg;
  el.style.display = 'flex';
}
