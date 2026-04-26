'use strict';

/* ─── Settings tabs ─── */
function showTab(name, el) {
  document.querySelectorAll('.settings-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.settings-nav-item').forEach(i => i.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  el.classList.add('active');
}

/* ─── Load profile ─── */
async function loadProfile() {
  try {
    const res = await fetchWithRefresh('/users/me');
    if (!res || !res.ok) return;
    const user = await res.json();
    document.getElementById('inputName').value  = user.first_name || '';
    document.getElementById('inputEmail').value = user.email      || '';
    document.getElementById('inputRole').value  = user.role       || '';
    const avatar = document.getElementById('avatarInitial');
    if (avatar) avatar.textContent = (user.first_name || 'А')[0].toUpperCase();
  } catch (err) {
    console.error('Ошибка загрузки профиля:', err);
  }
}

/* ─── Save profile ─── */
async function saveProfile() {
  const btn    = document.querySelector('#tab-profile .btn-primary');
  const msgEl  = document.getElementById('saveMsg');
  const payload = {
    first_name: document.getElementById('inputName').value.trim(),
    email:      document.getElementById('inputEmail').value.trim(),
  };

  btn.disabled    = true;
  btn.textContent = 'Сохранение…';

  try {
    const res = await fetchWithRefresh('/users/me', {
      method:  'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    if (res && res.ok) {
      showSaveMsg('✓ Сохранено', 'var(--green)');
    } else {
      const err = await res.json().catch(() => ({}));
      showSaveMsg('Ошибка: ' + (err.detail || res.statusText), 'var(--red)');
    }
  } catch {
    showSaveMsg('Ошибка соединения', 'var(--red)');
  } finally {
    btn.textContent = 'Сохранить изменения';
    btn.disabled    = false;
  }
}

function showSaveMsg(text, color) {
  const el = document.getElementById('saveMsg');
  if (!el) return;
  el.textContent   = text;
  el.style.color   = color;
  el.style.display = 'inline';
  setTimeout(() => { el.style.display = 'none'; }, 3000);
}

document.addEventListener('DOMContentLoaded', loadProfile);
