# Система аутентификации и авторизации на Django REST Framework

Полнофункциональная система с JWT токенами, ролями и гранулярными правами доступа (RBAC).

---

## Что умеет система

**Аутентификация:**
- Регистрация, вход, выход
- JWT токены (24 часа)
- Безопасные пароли (bcrypt)
- Обновление профиля
- Мягкое удаление аккаунта

**Авторизация:**
- 4 роли: admin, manager, user, guest
- 7 типов прав для каждого ресурса
- Разделение "свои/все" объекты
- Admin API для управления правами
- Автоматическая проверка прав

**Безопасность:**
- 401 - нет токена
- 403 - нет прав
- Проверка активности пользователя

---

## Быстрый старт

### 1. Установка
```bash
# Виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Зависимости
pip install -r requirements.txt
```

### 2. PostgreSQL
```bash
psql -U postgres

CREATE DATABASE auth_system_db;
CREATE USER auth_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE auth_system_db TO auth_user;
\q
```

### 3. Конфигурация (.env файл)
```env
DB_NAME=auth_system_db
DB_USER=auth_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key
DEBUG=True
```

### 4. База данных
```bash
python manage.py migrate
python manage.py loaddata initial_data.json
python populate_data.py
```

### 5. Запуск
```bash
python manage.py runserver
```

Готово! → http://localhost:8000

---

## Тестовые пользователи

| Email | Пароль | Роль | Возможности |
|-------|--------|------|-------------|
| admin@example.com | admin123 | admin | Всё |
| manager@example.com | manager123 | manager | Управление контентом |
| user@example.com | user123 | user | Свои заказы |
| guest@example.com | guest123 | guest | Только просмотр товаров |

---

## API Endpoints

### Аутентификация `/api/auth/`
```bash
# Регистрация
POST /api/auth/register/
{
  "first_name": "Иван",
  "last_name": "Иванов",
  "email": "ivan@example.com",
  "password": "pass123",
  "password_confirm": "pass123"
}

# Вход (получить токен)
POST /api/auth/login/
{
  "email": "ivan@example.com",
  "password": "pass123"
}
→ Вернёт токен!

# Профиль
GET    /api/auth/me/              # Просмотр
PUT    /api/auth/me/              # Обновление
DELETE /api/auth/me/delete/       # Удаление

# Выход
POST /api/auth/logout/
```

### Admin API `/api/admin/` (только admin)
```bash
# Роли
GET    /api/admin/roles/                      # Список
POST   /api/admin/roles/                      # Создать
GET    /api/admin/roles/{id}/                 # Детали
PUT    /api/admin/roles/{id}/                 # Обновить
DELETE /api/admin/roles/{id}/                 # Удалить
GET    /api/admin/roles/{id}/access-rules/    # Правила роли

# Бизнес-элементы
GET    /api/admin/business-elements/          # Список
POST   /api/admin/business-elements/          # Создать
GET    /api/admin/business-elements/{id}/     # Детали
PUT    /api/admin/business-elements/{id}/     # Обновить
DELETE /api/admin/business-elements/{id}/     # Удалить

# Правила доступа
GET    /api/admin/access-rules/               # Список (фильтры: ?role_id=1&element_id=2)
POST   /api/admin/access-rules/               # Создать
GET    /api/admin/access-rules/{id}/          # Детали
PUT    /api/admin/access-rules/{id}/          # Обновить
PATCH  /api/admin/access-rules/{id}/          # Частичное обновление
DELETE /api/admin/access-rules/{id}/          # Удалить
```

### Бизнес-объекты `/api/`
```bash
# Товары
GET    /api/products/           # Список (с проверкой прав)
POST   /api/products/           # Создать
GET    /api/products/{id}/      # Детали
PUT    /api/products/{id}/      # Обновить
DELETE /api/products/{id}/      # Удалить

# Заказы (аналогично)
GET    /api/orders/
POST   /api/orders/
GET    /api/orders/{id}/
PUT    /api/orders/{id}/
DELETE /api/orders/{id}/
```

---

## Примеры использования

### Базовый flow
```bash
# 1. Вход
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"user123"}'

# Ответ:
{
  "token": "eyJhbGciOiJIUzI1NiIs...", 
  "user": {...}
}

# 2. Используйте токен
TOKEN="eyJhbGciOiJIUzI1NiIs..."

# 3. Запросы с токеном
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer $TOKEN"

curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN"
```

### Admin: создать роль и правило
```bash
# Вход как admin
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

ADMIN_TOKEN="..."

# Создать роль
curl -X POST http://localhost:8000/api/admin/roles/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"support","description":"Поддержка"}'

# Создать правило доступа
curl -X POST http://localhost:8000/api/admin/access-rules/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": 5,
    "element": 2,
    "read_all_permission": true,
    "create_permission": false
  }'
```

---

## База данных

### Таблицы

**users** - пользователи
```
id, first_name, last_name, middle_name, email, password_hash,
role_id, is_active, created_at, updated_at
```

**roles** - роли (admin, manager, user, guest)
```
id, name, description, created_at
```

**sessions** - JWT токены
```
id, user_id, session_token, expires_at, created_at, ip_address, user_agent
```

**business_elements** - ресурсы (products, orders, stores, users)
```
id, name, description, endpoint, created_at
```

**access_rules** - правила доступа (кто что может)
```
id, role_id, element_id,
read_permission, read_all_permission,
create_permission,
update_permission, update_all_permission,
delete_permission, delete_all_permission,
created_at, updated_at

Unique: (role_id, element_id)
```

### Связи
```
users → roles
users → sessions
access_rules → roles
access_rules → business_elements
```

---

## Система прав доступа

### 7 типов прав

| Право | Что можно |
|-------|-----------|
| `read_permission` | Читать свои объекты |
| `read_all_permission` | Читать все объекты |
| `create_permission` | Создавать |
| `update_permission` | Менять свои |
| `update_all_permission` | Менять все |
| `delete_permission` | Удалять свои |
| `delete_all_permission` | Удалять все |

### Матрица прав (по умолчанию)

**Товары:**

| Роль | Чтение | Создание | Изменение | Удаление |
|------|--------|----------|-----------|----------|
| admin | Все | ✅ | Все | Все |
| manager | Все | ✅ | Все | Все |
| user | Все | ❌ | ❌ | ❌ |
| guest | Все | ❌ | ❌ | ❌ |

**Заказы:**

| Роль | Чтение | Создание | Изменение | Удаление |
|------|--------|----------|-----------|----------|
| admin | Все | ✅ | Все | Все |
| manager | Все | ✅ | Свои | ❌ |
| user | Свои | ✅ | Свои | Свои |
| guest | ❌ | ❌ | ❌ | ❌ |

### Как работает
```
1. Пользователь → Запрос → Middleware извлекает токен
2. Проверяет сессию в БД → Получает user
3. Декоратор @require_permission проверяет права в access_rules
4. Если read_all=False, но read=True → фильтрует по owner_id
5. Если update_all=False → проверяет владельца объекта
6. Возвращает данные или 403 Forbidden
```

---

## Архитектура
```
CLIENT (Authorization: Bearer TOKEN)
    ↓
CustomAuthMiddleware (извлекает токен, проверяет сессию)
    ↓
@require_permission (проверяет права в access_rules)
    ↓
View (фильтрует по owner если нужно)
    ↓
Response (данные или 401/403)
```

---

## Коды ответов

| Код | Что значит |
|-----|------------|
| 200 | OK |
| 201 | Создано |
| 204 | Удалено |
| 400 | Неверные данные |
| 401 | Нужен токен |
| 403 | Нет прав |
| 404 | Не найдено |

---

## Структура проекта
```
auth_system/
├── README.md
├── manage.py
├── requirements.txt
├── .env
├── initial_data.json
├── populate_data.py
│
├── config/              # Настройки Django
├── authentication/      # Вход, регистрация, профиль
├── authorization/       # Роли, права, Admin API
└── mock_business/       # Товары, заказы (mock данные)
```

---

## Технологии

- Python 3.11+
- Django 4.2.7
- Django REST Framework 3.14.0
- PostgreSQL
- JWT (PyJWT 2.8.0)
- Bcrypt 4.1.1

---

## Production

Для боевого сервера:
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECURE_SSL_REDIRECT = True
```
```bash
# Используйте gunicorn
pip install gunicorn
gunicorn config.wsgi:application
```

---

## Особенности реализации

- **Нет таблиц для товаров/заказов** - используются Mock данные в памяти
- **Система прав применяется** к Mock-объектам через декораторы
- **JWT хранятся в БД** - можно отозвать токен удалив сессию
- **Middleware работает со всеми запросами** - проверка токена автоматическая
- **Admin API защищён** - доступ только для роли admin

---

## Что можно улучшить

- Refresh токены
- Rate limiting
- Двухфакторная аутентификация
- Логирование действий
- Реальные таблицы вместо Mock данных
- Unit тесты
- Docker
- CI/CD

---

**Готово!** Проект полностью функционален и задокументирован.

Создано в учебных целях.
