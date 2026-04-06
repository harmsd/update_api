function showTab(name, el) {
  document.querySelectorAll('.settings-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.settings-nav-item').forEach(i => i.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  el.classList.add('active');
}

async function loadProfile() {
  try {
    const res = await fetch('/users/me');
    if (!res.ok) return;
    const user = await res.json();

    document.getElementById('inputName').value  = user.first_name || '';
    document.getElementById('inputEmail').value = user.email      || '';
    document.getElementById('inputRole').value  = user.role       || '';

  } catch (err) {
    console.error('Ошибка загрузки профиля:', err);
  }
}

async function saveProfile() {
  const btn = document.querySelector('#tab-profile .primary-btn');

  const payload = {
    first_name: document.getElementById('inputName').value.trim(),
    email:      document.getElementById('inputEmail').value.trim(),
  };

  btn.disabled    = true;
  btn.textContent = 'Сохранение…';

  try {
    const res = await fetch('/users/me', {
      method:  'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload)
    });

    if (res.ok) {
      btn.textContent = '✓ Сохранено';
    } else {
      const err = await res.json().catch(() => ({}));
      btn.textContent = 'Ошибка: ' + (err.detail || res.statusText);
    }
  } catch {
    btn.textContent = 'Ошибка соединения';
  } finally {
    setTimeout(() => {
      btn.textContent = 'Сохранить изменения';
      btn.disabled    = false;
    }, 2500);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadProfile();

  const saveBtn = document.querySelector('#tab-profile .primary-btn');
  if (saveBtn) saveBtn.addEventListener('click', saveProfile);
});

document.getElementById("logout-btn").addEventListener("click", async () => {
    const response = await fetch("/login/logout", {
        method: "POST",
        credentials: "include"
    });

    if (response.redirected) {
        window.location.href = response.url;
    } else {
        window.location.href = "/login/";
    }
});