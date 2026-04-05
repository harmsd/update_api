'use strict';

/* ── Состояние ── */
let uploadedFile = null;

/* ── Drag & Drop ── */

function onDragOver(e) {
  e.preventDefault();
  document.getElementById('dropzone').classList.add('drag-over');
}

function onDragLeave() {
  document.getElementById('dropzone').classList.remove('drag-over');
}

function onDrop(e) {
  e.preventDefault();
  onDragLeave();
  const file = e.dataTransfer.files[0];
  if (file) handleSelectedFile(file);
}

function handleFile(e) {
  const file = e.target.files[0];
  if (file) handleSelectedFile(file);
}

/* ── Основная логика загрузки ── */

function handleSelectedFile(file) {
  uploadedFile = file;
  document.getElementById('fileName').textContent = file.name;
  document.getElementById('fileChosen').classList.add('visible');
  document.getElementById('dropzone').classList.add('has-file');
  uploadAndParseLicense(file);
}

async function uploadAndParseLicense(file) {
  setUploadStatus('loading', 'Отправка на сервер…');

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('/licenses/upload-enc', {
      method: 'POST',
      body: formData
      // Content-Type НЕ задаём вручную — браузер сам добавит boundary для multipart
    });

    const result = await response.json();

    if (!response.ok) {
      const message = result.detail || result.error || 'Ошибка валидации файла';
      setUploadStatus('error', message);
      removeFile();
      return;
    }

    fillFormFromLicense(result);
    setUploadStatus('success', 'Файл успешно проверен, поля заполнены');
    setChecksumStatus('neutral', 'Файл принят сервером');

  } catch (err) {
    setUploadStatus('error', 'Не удалось соединиться с сервером');
    removeFile();
  }
}

/* ── Заполнение формы данными из .enc ── */

function fillFormFromLicense(data) {
  if (data.organization) {
    setField('orgName',     data.organization.name);
    setField('orgInn',      data.organization.inn);
    setField('orgEmail',    data.organization.email);
    setField('orgTariff',   data.organization.tariff);
    setField('orgLicCount', data.organization.licenses);
    setField('orgExpiry',   data.organization.expiry);
  }

  if (data.checksum) {
    setField('checksumAlgo',  data.checksum.algorithm);
    setField('checksumValue', data.checksum.value);
  }

  if (data.host) {
    setField('hostName',    data.host.hostname);
    setField('hostOs',      data.host.os);
    setField('hostMac',     data.host.mac);
    setField('hostUuid',    data.host.uuid);
    setField('hostComment', data.host.comment);
  }
}

/* Устанавливает значение поля только если оно не null/undefined/''.
   Для select автоматически ищет совпадающий option. */
function setField(id, value) {
  if (value === null || value === undefined || value === '') return;
  const el = document.getElementById(id);
  if (!el) return;
  el.value = value;
}

/* ── Удалить файл ── */

function removeFile() {
  uploadedFile = null;
  document.getElementById('fileChosen').classList.remove('visible');
  document.getElementById('dropzone').classList.remove('has-file');
  document.getElementById('fileInput').value = '';
  document.getElementById('fileName').textContent = '—';
}

/* ── Статус загрузки файла (под дропзоной) ── */

function setUploadStatus(type, message) {
  const el = document.getElementById('uploadStatus');
  if (!el) return;
  el.className = 'upload-status' + (type ? ' upload-status--' + type : '');
  el.textContent = message;
}

/* ── Контрольная сумма ── */

function copyChecksum() {
  const val = document.getElementById('checksumValue').value;
  if (val) {
    navigator.clipboard.writeText(val).catch(() => {});
  }
}

function verifyChecksum() {
  const val = document.getElementById('checksumValue').value.trim();
  if (!val) {
    setChecksumStatus('neutral', 'Введите значение');
    return;
  }
  // Проверка формата SHA-256 (64 hex-символа)
  const isSha256 = /^[0-9a-fA-F]{64}$/.test(val);
  if (isSha256) {
    setChecksumStatus('ok', 'Формат SHA-256 корректен');
  } else {
    setChecksumStatus('fail', 'Не соответствует формату SHA-256');
  }
}

function setChecksumStatus(type, message) {
  const dot  = document.querySelector('.cs-dot');
  const text = document.getElementById('csText');
  if (!dot || !text) return;
  dot.className = 'cs-dot ' + (
    type === 'ok'   ? 'cs-ok'   :
    type === 'fail' ? 'cs-fail' :
    'cs-neutral'
  );
  text.textContent = message;
}

/* ── Сброс формы ── */

function resetForm() {
  const textFields = [
    'orgName', 'orgInn', 'orgEmail', 'orgLicCount', 'orgExpiry',
    'checksumValue', 'hostName', 'hostMac', 'hostUuid', 'hostComment'
  ];
  textFields.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });

  const selectFields = ['orgTariff', 'checksumAlgo', 'hostOs'];
  selectFields.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.selectedIndex = 0;
  });

  removeFile();
  setChecksumStatus('neutral', 'Не проверено');
  setUploadStatus('', '');
}

/* ── Отправка формы на сервер ── */

async function submitForm() {
  const name = document.getElementById('orgName').value.trim();
  const inn  = document.getElementById('orgInn').value.trim();

  if (!name) {
    alert('Заполните обязательное поле: Название');
    document.getElementById('orgName').focus();
    return;
  }
  if (!inn) {
    alert('Заполните обязательное поле: ИНН');
    document.getElementById('orgInn').focus();
    return;
  }

  const payload = {
    organization: {
      name,
      inn,
      email:    document.getElementById('orgEmail').value.trim(),
      tariff:   document.getElementById('orgTariff').value,
      licenses: document.getElementById('orgLicCount').value,
      expiry:   document.getElementById('orgExpiry').value.trim()
    },
    checksum: {
      algorithm: document.getElementById('checksumAlgo').value,
      value:     document.getElementById('checksumValue').value.trim()
    },
    host: {
      hostname: document.getElementById('hostName').value.trim(),
      os:       document.getElementById('hostOs').value,
      mac:      document.getElementById('hostMac').value.trim(),
      uuid:     document.getElementById('hostUuid').value.trim(),
      comment:  document.getElementById('hostComment').value.trim()
    }
  };

  try {
    const response = await fetch('/licenses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      alert('Ошибка сохранения: ' + (err.detail || response.statusText));
      return;
    }

    // Успех — редирект на список лицензий
    window.location.href = '/organizations';

  } catch (err) {
    alert('Не удалось соединиться с сервером');
  }
}