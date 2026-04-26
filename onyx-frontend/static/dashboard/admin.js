'use strict';

const PAGE_SIZE = 8;
let allUsers    = [];
let currentPage = 1;

/* ─── Load users ─── */
async function loadUsers() {
  try {
    const res = await fetchWithRefresh('/users/');
    if (res && res.ok) {
      allUsers = await res.json();
    } else {
      throw new Error('API unavailable');
    }
  } catch {
    allUsers = [];
  }
  currentPage = 1;
  updateStats();
  renderPage();
}

/* ─── Filtering ─── */
function getFiltered() {
  const q    = (document.getElementById('searchInput')?.value || '').toLowerCase();
  const role = document.getElementById('roleFilter')?.value || '';
  return allUsers.filter(u => {
    const txt = [u.username, u.name, u.email].join(' ').toLowerCase();
    return txt.includes(q) && (!role || u.role === role);
  });
}

/* ─── Stats ─── */
function updateStats() {
  const total  = allUsers.length;
  const active = allUsers.filter(u => !u.disabled).length;
  const admins = allUsers.filter(u => u.role === 'admin').length;
  setText('statTotal',  total);
  setText('statActive', active);
  setText('statAdmins', admins);
  const el = document.getElementById('activeCount');
  if (el) el.textContent = active + ' активных';
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

/* ─── Render ─── */
function renderPage() {
  const filtered   = getFiltered();
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  if (currentPage > totalPages && totalPages > 0) currentPage = totalPages;

  const start = (currentPage - 1) * PAGE_SIZE;
  const slice = filtered.slice(start, start + PAGE_SIZE);

  renderTable(slice);
  renderPagination(filtered.length, totalPages);

  const shown = Math.min(start + PAGE_SIZE, filtered.length);
  setText('paginationInfo', filtered.length ? `Показано ${shown} из ${filtered.length}` : 'Нет данных');
}

function roleLabel(r)  { return { admin:'Администратор', operator:'Оператор', viewer:'Наблюдатель' }[r] || r; }
function roleColor(r)  { return { admin:'var(--red)', operator:'var(--purple)', viewer:'var(--muted)' }[r] || 'var(--muted)'; }
function roleBg(r)     { return { admin:'var(--red-dim)', operator:'var(--purple-dim2)', viewer:'rgba(255,255,255,0.05)' }[r] || 'rgba(255,255,255,0.05)'; }

function renderTable(users) {
  const tbody = document.getElementById('usersTableBody');
  if (!users.length) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:2rem">Нет данных</td></tr>';
    return;
  }
  tbody.innerHTML = users.map(u => `
    <tr>
      <td>
        <div style="display:flex;align-items:center;gap:10px">
          <div class="user-avatar" style="background:${roleBg(u.role)};border:1px solid rgba(255,255,255,0.06);color:${roleColor(u.role)}">
            ${(u.name || '?')[0].toUpperCase()}
          </div>
          <strong style="font-weight:500">${escHtml(u.name)}</strong>
        </div>
      </td>
      <td style="font-family:monospace;font-size:12px;color:var(--muted)">${escHtml(u.username)}</td>
      <td style="color:var(--muted)">${escHtml(u.email)}</td>
      <td><span class="badge" style="background:${roleBg(u.role)};color:${roleColor(u.role)}">${roleLabel(u.role)}</span></td>
      <td>
        <span class="badge" style="background:${!u.disabled?'var(--green-dim)':'rgba(255,255,255,0.05)'};color:${!u.disabled?'var(--green)':'var(--muted)'}">
          ${!u.disabled ? 'Активен' : 'Отключён'}
        </span>
      </td>
      <td style="color:var(--muted);font-size:12px">${formatDate(u.created)}</td>
      <td>
        <div class="table-actions">
          <button class="icon-btn" title="Редактировать" onclick="openEditModal(${u.id})">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
          <button class="icon-btn ${!u.disabled ? 'warn' : ''}" title="${!u.disabled ? 'Отключить' : 'Включить'}" onclick="toggleActive(${u.id})">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
              ${!u.disabled
                ? '<path d="M18.364 18.364A9 9 0 0 0 5.636 5.636m12.728 12.728A9 9 0 0 1 5.636 5.636m12.728 12.728L5.636 5.636"/>'
                : '<path d="M20 6L9 17l-5-5"/>'}
            </svg>
          </button>
          <button class="icon-btn del" title="Удалить" onclick="deleteUser(${u.id})" ${u.id === 1 ? 'disabled style="opacity:.3;cursor:not-allowed"' : ''}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
      </td>
    </tr>
  `).join('');
}

function renderPagination(total, pages) {
  const container = document.getElementById('pageBtns');
  if (!container || pages <= 1) { if(container) container.innerHTML = ''; return; }
  let html = '';
  for (let i = 1; i <= pages; i++) {
    html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
  }
  container.innerHTML = html;
}

function goToPage(page) {
  const pages = Math.ceil(getFiltered().length / PAGE_SIZE);
  if (page < 1 || page > pages) return;
  currentPage = page;
  renderPage();
}

/* ─── Toggle active ─── */
async function toggleActive(id) {
  const user = allUsers.find(u => u.id === id);
  if (!user) return;
  const newDisabled = !user.disabled;
  try {
    await fetchWithRefresh(`/users/${id}`, {
      method:  'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ disabled: newDisabled }),
    });
  } catch {}
  user.disabled = newDisabled;
  updateStats();
  renderPage();
}

/* ─── Delete user ─── */
async function deleteUser(id) {
  if (!confirm('Удалить пользователя?')) return;
  try {
    await fetchWithRefresh(`/users/${id}`, { method: 'DELETE' });
  } catch {}
  allUsers = allUsers.filter(u => u.id !== id);
  updateStats();
  renderPage();
}

/* ─── Edit modal ─── */
function openEditModal(id) {
  const u = allUsers.find(u => u.id === id);
  if (!u) return;
  document.getElementById('editId').value       = u.id;
  document.getElementById('editName').value     = u.name     || '';
  document.getElementById('editUsername').value = u.username || '';
  document.getElementById('editEmail').value    = u.email      || '';
  document.getElementById('editRole').value     = u.role       || 'viewer';
  document.getElementById('editPassword').value = '';
  document.getElementById('editSubtitle').textContent = u.username || '';
  document.getElementById('editModal').classList.add('open');
}

function closeEditModal() {
  document.getElementById('editModal').classList.remove('open');
}

async function saveEdit() {
  const id      = parseInt(document.getElementById('editId').value);
  const payload = {
    name:  document.getElementById('editName').value.trim(),
    email: document.getElementById('editEmail').value.trim(),
    role:  document.getElementById('editRole').value,
  };
  const pw = document.getElementById('editPassword').value;
  if (pw) payload.password_string = pw;

  try {
    const res = await fetchWithRefresh(`/users/${id}`, {
      method:  'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });
    const updated = res && res.ok ? await res.json() : { ...allUsers.find(u => u.id === id), ...payload };
    const idx = allUsers.findIndex(u => u.id === id);
    if (idx !== -1) allUsers[idx] = { ...allUsers[idx], ...updated };
  } catch {
    const idx = allUsers.findIndex(u => u.id === id);
    if (idx !== -1) allUsers[idx] = { ...allUsers[idx], ...payload };
  }

  updateStats();
  renderPage();
  closeEditModal();
}

/* ─── Create modal ─── */
function openCreateModal() {
  document.getElementById('createName').value     = '';
  document.getElementById('createUsername').value = '';
  document.getElementById('createEmail').value    = '';
  document.getElementById('createRole').value     = 'operator';
  document.getElementById('createPassword').value = '';
  document.getElementById('createModal').classList.add('open');
}

function closeCreateModal() {
  document.getElementById('createModal').classList.remove('open');
}

async function createUser() {
  const username = document.getElementById('createUsername').value.trim();
  const email    = document.getElementById('createEmail').value.trim();
  if (!username) { alert('Заполните логин'); return; }
  if (!email)    { alert('Заполните email'); return; }

  const btn     = document.getElementById('createSubmitBtn');
  btn.disabled  = true;
  btn.textContent = 'Создание…';

  const payload = {
    name:            document.getElementById('createName').value.trim(),
    username,
    email,
    role:            document.getElementById('createRole').value,
    password_string: document.getElementById('createPassword').value,
    organization:    '',
  };

  try {
    const res = await fetchWithRefresh('/users/', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });
    const created = res && res.ok
      ? await res.json()
      : { id: Date.now(), ...payload, active: true, created: new Date().toISOString().slice(0, 10) };
    allUsers.push(created);
  } catch {
    allUsers.push({ id: Date.now(), ...payload, active: true, created: new Date().toISOString().slice(0, 10) });
  }

  updateStats();
  renderPage();
  closeCreateModal();
  btn.disabled    = false;
  btn.textContent = 'Создать пользователя';
}

/* ─── Helpers ─── */
function escHtml(s) {
  if (!s) return '—';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('ru-RU') : '—';
}

/* ─── Init ─── */
document.addEventListener('DOMContentLoaded', () => {
  loadUsers();

  document.getElementById('searchInput')?.addEventListener('input',  () => { currentPage = 1; renderPage(); });
  document.getElementById('roleFilter')?.addEventListener('change',  () => { currentPage = 1; renderPage(); });

  ['editModal','createModal'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('click', e => { if (e.target === el) el.classList.remove('open'); });
  });
});
