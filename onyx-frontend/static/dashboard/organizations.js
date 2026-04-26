'use strict';

const PAGE_SIZE  = 6;
let allLicenses  = [];
let currentPage  = 1;
let currentKeyId = null;

async function loadLicenses() {
  try {
    const response = await fetchWithRefresh('/licenses/?limit=100');
    if (!response.ok) { showTableError('Не удалось загрузить данные'); return; }
    allLicenses = await response.json();
    currentPage = 1;
    updateStats(allLicenses);
    renderPage();
  } catch (err) {
    showTableError('Ошибка соединения с сервером');
  }
}

function renderPage() {
  const filtered = getFiltered();
  const total    = filtered.length;
  const pages    = Math.ceil(total / PAGE_SIZE);

  if (currentPage > pages && pages > 0) currentPage = pages;

  const start = (currentPage - 1) * PAGE_SIZE;
  const slice = filtered.slice(start, start + PAGE_SIZE);

  renderTable(slice);
  renderPagination(total, pages);

  const shown = Math.min(start + PAGE_SIZE, total);
  document.getElementById('paginationInfo').textContent =
    total ? `Показано ${shown} из ${total}` : 'Нет данных';
}


function renderTable(licenses) {
  const tbody = document.getElementById('licenseTableBody');

  if (!licenses.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center;color:var(--text-muted);padding:2rem;">
          Нет данных
        </td>
      </tr>`;
    return;
  }

  tbody.innerHTML = licenses.map(lic => `
    <tr data-id="${lic.id}">
      <td data-label="Организация">
        <strong>${escHtml(lic.name)}</strong>
        <small>${escHtml(lic.email)}</small>
      </td>
      <td data-label="ИНН">${escHtml(lic.inn)}</td>
      <td data-label="Хост">${escHtml(lic.hostname)}</td>
      <td data-label="Тариф">
        <span class="badge ${tariffBadge(lic.tariff)}">${escHtml(lic.tariff)}</span>
      </td>
      <td data-label="Статус">
        <span class="badge ${statusBadge(lic.disabled, lic.end_date)}">
          ${statusLabel(lic.disabled, lic.end_date)}
        </span>
      </td>
      <td data-label="Окончание">${formatDate(lic.end_date)}</td>
      <td data-label="Действия">
        <div class="table-actions">
          <button class="icon-btn" title="Редактировать" onclick="openEditModal(${lic.id})">✏️</button>
          <button class="icon-btn" title="Сгенерировать ключ" onclick="openKeyModal(${lic.id})">🔑</button>
        </div>
      </td>
    </tr>
  `).join('');
}

function renderPagination(total, pages) {
  const container = document.querySelector('.page-btns');
  if (pages <= 1) { container.innerHTML = ''; return; }

  let html = `<button class="page-btn ${currentPage === 1 ? 'disabled' : ''}"
    onclick="goToPage(${currentPage - 1})">‹</button>`;

  getPageRange(currentPage, pages).forEach(p => {
    if (p === '…') {
      html += `<button class="page-btn disabled" disabled>…</button>`;
    } else {
      html += `<button class="page-btn ${p === currentPage ? 'active' : ''}"
        onclick="goToPage(${p})">${p}</button>`;
    }
  });

  html += `<button class="page-btn ${currentPage === pages ? 'disabled' : ''}"
    onclick="goToPage(${currentPage + 1})">›</button>`;

  container.innerHTML = html;
}

function getPageRange(current, total) {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  if (current <= 4)         return [1, 2, 3, 4, 5, '…', total];
  if (current >= total - 3) return [1, '…', total-4, total-3, total-2, total-1, total];
  return [1, '…', current-1, current, current+1, '…', total];
}

function goToPage(page) {
  const pages = Math.ceil(getFiltered().length / PAGE_SIZE);
  if (page < 1 || page > pages) return;
  currentPage = page;
  renderPage();
}

function openEditModal(id) {
  const lic = allLicenses.find(l => l.id === id);
  if (!lic) return;

  document.getElementById('editId').value       = lic.id;
  document.getElementById('editName').value     = lic.name     || '';
  document.getElementById('editInn').value      = lic.inn      || '';
  document.getElementById('editEmail').value    = lic.email    || '';
  document.getElementById('editTariff').value   = lic.tariff   || '';
  document.getElementById('editHostname').value = lic.hostname || '';
  document.getElementById('editOs').value       = lic.os       || '';
  document.getElementById('editMac').value      = lic.mac      || '';
  document.getElementById('editUuid').value     = lic.uuid     || '';
  document.getElementById('editComment').value  = lic.comment  || '';
  document.getElementById('editDisabled').value = lic.disabled ? 'true' : 'false';

  if (lic.end_date) {
    const d = new Date(lic.end_date);
    document.getElementById('editExpiry').value = d.toLocaleDateString('ru-RU');
  } else {
    document.getElementById('editExpiry').value = '';
  }

  document.getElementById('editModal').classList.add('open');
}

function closeEditModal() {
  document.getElementById('editModal').classList.remove('open');
}

async function saveEdit() {
  const id   = parseInt(document.getElementById('editId').value);
  const name = document.getElementById('editName').value.trim();
  const inn  = document.getElementById('editInn').value.trim();

  if (!name) { alert('Заполните поле: Название'); return; }
  if (!inn)  { alert('Заполните поле: ИНН');      return; }

  const payload = {
    organization: {
      name,
      inn,
      email:    document.getElementById('editEmail').value.trim(),
      tariff:   document.getElementById('editTariff').value,
      licenses: 0,
      expiry:   document.getElementById('editExpiry').value.trim()
    },
    checksum: {
      algorithm: 'SHA-256',
      value: allLicenses.find(l => l.id === id)?.checksum || ''
    },
    host: {
      hostname: document.getElementById('editHostname').value.trim(),
      os:       document.getElementById('editOs').value,
      mac:      document.getElementById('editMac').value.trim(),
      uuid:     document.getElementById('editUuid').value.trim(),
      comment:  document.getElementById('editComment').value.trim()
    }
  };

  try {
    const res = await fetchWithRefresh(`/licenses/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert('Ошибка: ' + (err.detail || res.statusText));
      return;
    }

    const updated = await res.json();
    const idx = allLicenses.findIndex(l => l.id === id);
    if (idx !== -1) allLicenses[idx] = updated;

    updateStats(allLicenses);
    renderPage();
    closeEditModal();
  } catch {
    alert('Не удалось соединиться с сервером');
  }
}

function openKeyModal(id) {
  const lic = allLicenses.find(l => l.id === id);
  if (!lic) return;
  currentKeyId = id;

  document.getElementById('keyModalSubtitle').textContent = lic.name || '—';
  generateKeyData(lic);
  document.getElementById('keyModal').classList.add('open');
}

function closeKeyModal() {
  document.getElementById('keyModal').classList.remove('open');
  currentKeyId = null;
}

function regenerateKey() {
  const lic = allLicenses.find(l => l.id === currentKeyId);
  if (lic) generateKeyData(lic);
}

function generateKeyData(lic) {
  const salt    = crypto.getRandomValues(new Uint8Array(16));
  const saltHex = Array.from(salt).map(b => b.toString(16).padStart(2, '0')).join('');
  const raw     = `${lic.id}|${lic.inn}|${lic.name}|${lic.mac}|${saltHex}`;

  crypto.subtle.digest('SHA-256', new TextEncoder().encode(raw)).then(hashBuffer => {
    const hashHex = Array.from(new Uint8Array(hashBuffer))
      .map(b => b.toString(16).padStart(2, '0')).join('');
    document.getElementById('keyHash').value = hashHex;
  });

  document.getElementById('keyLogin').value    = generateLogin(lic.name, lic.inn);
  document.getElementById('keyPassword').value = generatePassword();
}

function generateLogin(name, inn) {
  const translit = {
    'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'zh',
    'з':'z','и':'i','й':'j','к':'k','л':'l','м':'m','н':'n','о':'o',
    'п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'kh','ц':'ts',
    'ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya'
  };
  const words  = name.replace(/[«»"']/g, '').trim().split(/\s+/);
  const word   = (words[0] || 'org').toLowerCase();
  const slug   = word.split('').map(c => translit[c] ?? c).join('').replace(/[^a-z0-9]/g, '');
  const suffix = String(inn || '').slice(-4);
  return (slug.slice(0, 10) + suffix) || 'user' + suffix;
}

function generatePassword() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789!@#$%';
  const arr   = crypto.getRandomValues(new Uint8Array(16));
  return Array.from(arr).map(b => chars[b % chars.length]).join('');
}

function copyField(id) {
  const val = document.getElementById(id).value;
  if (val) navigator.clipboard.writeText(val).catch(() => {});
}

function getFiltered() {
  const search = document.querySelector('input[type="search"]').value.toLowerCase();
  const status = document.querySelector('.topbar-actions select').value;

  return allLicenses.filter(lic => {
    const text        = [lic.name, lic.inn, lic.hostname, lic.email].join(' ').toLowerCase();
    const matchText   = text.includes(search);
    const licStatus   = statusLabel(lic.disabled, lic.end_date);
    const matchStatus = status === 'Все статусы' || licStatus === status;
    return matchText && matchStatus;
  });
}

function updateStats(licenses) {
  const total    = licenses.length;
  const active   = licenses.filter(l => !l.disabled && !isExpired(l.end_date)).length;
  const expiring = licenses.filter(l => isExpiringSoon(l.end_date)).length;

  setStatCard(0, total,    'всего записей');
  setStatCard(1, active,   `Из ${total} выдано`);
  setStatCard(2, expiring, 'В течение 30 дней');

  const el = document.getElementById('activeCount');
  if (el) el.textContent = `${active} активных`;
}

function setStatCard(index, value, hint) {
  const cards = document.querySelectorAll('.stat-card');
  if (!cards[index]) return;
  const valEl  = cards[index].querySelector('.stat-value');
  const hintEl = cards[index].querySelector('.stat-hint');
  if (valEl)  valEl.textContent  = value;
  if (hintEl) hintEl.textContent = hint;
}

function escHtml(str) {
  if (!str) return '—';
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('ru-RU');
}

function isExpired(endDate) {
  return endDate && new Date(endDate) < new Date();
}

function isExpiringSoon(endDate) {
  if (!endDate) return false;
  const diff = new Date(endDate) - new Date();
  return diff > 0 && diff < 30 * 24 * 60 * 60 * 1000;
}

function statusLabel(disabled, endDate) {
  if (disabled)                return 'Заблокирована';
  if (isExpired(endDate))      return 'Просрочена';
  if (isExpiringSoon(endDate)) return 'Истекает';
  return 'Активна';
}

function statusBadge(disabled, endDate) {
  if (disabled)                return 'badge-danger';
  if (isExpired(endDate))      return 'badge-danger';
  if (isExpiringSoon(endDate)) return 'badge-warn';
  return 'badge-active';
}

function tariffBadge(tariff) {
  const map = { 'Enterprise':'badge-purple', 'Pro':'badge-active', 'Starter':'badge-neutral' };
  return map[tariff] || 'badge-neutral';
}

function showTableError(message) {
  document.getElementById('licenseTableBody').innerHTML = `
    <tr>
      <td colspan="7" style="text-align:center;color:var(--danger);padding:2rem;">
        ⚠️ ${message}
      </td>
    </tr>`;
}

document.addEventListener('DOMContentLoaded', () => {
  loadLicenses();

  document.querySelector('input[type="search"]')
    .addEventListener('input', () => { currentPage = 1; renderPage(); });

  document.querySelector('.topbar-actions select')
    .addEventListener('change', () => { currentPage = 1; renderPage(); });

  ['editModal', 'keyModal'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('click', function(e) {
      if (e.target === this) this.classList.remove('open');
    });
  });
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
