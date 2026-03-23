async function loadDistributions() {
  const response = await fetch('/api/distributions');
  const data = await response.json();

  const container = document.getElementById('distributions-container');

  container.innerHTML = '';

  data.forEach(dist => {
    const section = document.createElement('section');
    section.className = 'card infra-card';

    section.innerHTML = `
      <div class="section-header">
        <div>
          <h3>${dist.name}</h3>
          <p>Активен с ${dist.start} по ${dist.end}</p>
        </div>
        <button class="ghost-btn">Обновить</button>
      </div>

      <div class="template-switch">
        <button class="template active">Действителен</button>
        <button class="template">Подробнее</button>
      </div>
    `;

    container.appendChild(section);
  });
}
document.addEventListener('DOMContentLoaded', loadDistributions);