# OnyX Frontend

Редизайн фронтенда в стиле OnyX. Структура полностью совместима с оригинальным проектом.

## Структура

```
onyx-frontend/
├── static/
│   ├── css/
│   │   ├── onyx.css          ← общая дизайн-система (токены, компоненты)
│   │   ├── login.css         ← стили страницы входа
│   │   ├── dashboard.css     ← стили панели администратора
│   │   └── updates.css       ← стили портала оператора
│   ├── auth/
│   │   └── script.js         ← логика входа (POST /jwt/login)
│   ├── api/
│   │   └── script.js         ← fetchWithRefresh + logout handler
│   ├── dashboard/
│   │   ├── licenses.js       ← загрузка .enc файлов, форма лицензии
│   │   ├── organizations.js  ← таблица организаций, CRUD, генерация ключей
│   │   ├── settings.js       ← профиль /users/me, табы настроек
│   │   └── admin.js          ← управление пользователями /users/
│   └── updates/
│       └── script.js         ← logout для портала оператора
│
└── templates/
    ├── partials/
    │   └── _sidebar_admin.html   ← Jinja2 include-partial для сайдбара
    ├── auth/
    │   └── login.html
    ├── dashboard/
    │   ├── licenses.html         ← /main  (загрузка лицензии)
    │   ├── organizations.html    ← /organizations
    │   ├── admin.html            ← /admin (управление пользователями)
    │   └── settings.html        ← /settings
    └── update/
        ├── updates.html          ← /updates
        ├── license.html          ← /license
        └── support.html          ← /support
```

## API endpoints (без изменений)

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/jwt/login` | Вход (form-urlencoded) |
| POST | `/jwt/refresh` | Обновление токена |
| POST | `/login/logout` | Выход |
| GET/PATCH | `/users/me` | Профиль текущего пользователя |
| GET/POST | `/users/` | Список пользователей / создание |
| PATCH/DELETE | `/users/{id}` | Редактирование / удаление |
| GET | `/licenses/?limit=100` | Список лицензий |
| POST | `/licenses` | Создать лицензию |
| PATCH | `/licenses/{id}` | Обновить лицензию |
| POST | `/licenses/upload-enc` | Загрузить .enc файл |

## Подключение в FastAPI / Jinja2

1. Скопируйте папку `static/` в ваш проект
2. Скопируйте папку `templates/` в ваш проект
3. В роутах замените ссылки на старые CSS → новые:
   - `login.css` → `onyx.css` + `login.css`
   - `organizations.css` → `onyx.css` + `dashboard.css`
   - и т.д.

## Роли

- `admin` → после входа попадает на `/main/` (панель администратора)
- остальные → после входа попадают на `/updates/` (портал оператора)
