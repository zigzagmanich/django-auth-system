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

http://localhost:8000

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

### 1. Первый запуск и регистрация
```bash
# Зарегистрировать нового пользователя
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Петр",
    "last_name": "Петров",
    "middle_name": "Петрович",
    "email": "petr@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'

# Ответ:
{
  "id": 5,
  "email": "petr@example.com",
  "first_name": "Петр",
  "last_name": "Петров",
  "middle_name": "Петрович",
  "role": "user",
  "is_active": true,
  "created_at": "2026-02-11T12:00:00Z"
}
```

### 2. Вход и сохранение токена
```bash
# Вход
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "petr@example.com",
    "password": "securepass123"
  }'

# Ответ с токеном:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 5,
    "email": "petr@example.com",
    "role": "user",
    ...
  },
  "expires_at": "2026-02-12T12:00:00Z"
}

# Сохраните токен в переменную для удобства
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Работа с профилем
```bash
# Просмотр своего профиля
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer $TOKEN"

# Обновить имя
curl -X PATCH http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Пётр"}'

# Полное обновление профиля
curl -X PUT http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Пётр",
    "last_name": "Петров-Водкин",
    "middle_name": "Петрович"
  }'
```

### 4. User: Работа с товарами и заказами
```bash
# Просмотр всех товаров (user может видеть все)
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN"

# Ответ:
{
  "count": 5,
  "results": [
    {"id": 1, "name": "Ноутбук", "price": 50000, "owner_id": 2},
    {"id": 2, "name": "Телефон", "price": 30000, "owner_id": 2},
    ...
  ]
}

# Создать заказ
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'

# Ответ:
{
  "id": 5,
  "product_id": 1,
  "quantity": 2,
  "status": "pending",
  "owner_id": 5
}

# Просмотр своих заказов (автоматическая фильтрация)
curl -X GET http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer $TOKEN"

# Обновить свой заказ
curl -X PUT http://localhost:8000/api/orders/5/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "quantity": 3
  }'

# Попытка изменить ЧУЖОЙ заказ (получим 403)
curl -X PUT http://localhost:8000/api/orders/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# Ответ:
{
  "error": "Forbidden",
  "detail": "Access denied - not owner"
}
```

### 5. Manager: Управление товарами
```bash
# Вход как manager
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"manager@example.com","password":"manager123"}'

MANAGER_TOKEN="полученный_токен"

# Создать товар
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Монитор",
    "price": 15000
  }'

# Изменить ЛЮБОЙ товар (manager имеет update_all)
curl -X PUT http://localhost:8000/api/products/1/ \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ноутбук Pro",
    "price": 75000
  }'

# Удалить товар
curl -X DELETE http://localhost:8000/api/products/3/ \
  -H "Authorization: Bearer $MANAGER_TOKEN"

# Просмотр ВСЕХ заказов (manager видит все)
curl -X GET http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer $MANAGER_TOKEN"
```

### 6. Guest: Ограниченный доступ
```bash
# Вход как guest
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"guest@example.com","password":"guest123"}'

GUEST_TOKEN="полученный_токен"

# Просмотр товаров (разрешено)
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $GUEST_TOKEN"

# Попытка создать товар (403)
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $GUEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Мышка", "price": 500}'

# Ответ:
{
  "error": "Forbidden",
  "detail": "Access denied"
}

# Попытка посмотреть заказы (403)
curl -X GET http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer $GUEST_TOKEN"

# Ответ:
{
  "error": "Forbidden",
  "detail": "No access rule for role \"guest\" and element \"orders\""
}
```

### 7. Admin: Управление системой прав
```bash
# Вход как admin
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

ADMIN_TOKEN="полученный_токен"

# Просмотр всех ролей
curl -X GET http://localhost:8000/api/admin/roles/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Создать новую роль
curl -X POST http://localhost:8000/api/admin/roles/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "support",
    "description": "Служба поддержки клиентов"
  }'

# Ответ:
{
  "id": 5,
  "name": "support",
  "description": "Служба поддержки клиентов",
  "created_at": "2026-02-11T12:00:00Z"
}

# Создать новый бизнес-элемент
curl -X POST http://localhost:8000/api/admin/business-elements/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "tickets",
    "description": "Тикеты поддержки",
    "endpoint": "/api/tickets/"
  }'

# Просмотр всех правил доступа
curl -X GET http://localhost:8000/api/admin/access-rules/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Создать правило: support может читать все заказы
curl -X POST http://localhost:8000/api/admin/access-rules/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": 5,
    "element": 3,
    "read_permission": false,
    "read_all_permission": true,
    "create_permission": false,
    "update_permission": false,
    "update_all_permission": false,
    "delete_permission": false,
    "delete_all_permission": false
  }'

# Фильтрация правил по роли
curl -X GET "http://localhost:8000/api/admin/access-rules/?role_id=3" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Фильтрация по элементу
curl -X GET "http://localhost:8000/api/admin/access-rules/?element_id=2" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Обновить правило (дать guest права на создание заказов)
curl -X PATCH http://localhost:8000/api/admin/access-rules/12/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "read_permission": true,
    "create_permission": true
  }'

# Просмотр правил конкретной роли
curl -X GET http://localhost:8000/api/admin/roles/3/access-rules/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Удалить правило
curl -X DELETE http://localhost:8000/api/admin/access-rules/15/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 8. Сценарий: Изменение прав
```bash
# Admin дает user права на создание товаров

# 1. Найти правило user -> products
curl -X GET "http://localhost:8000/api/admin/access-rules/?role_id=3&element_id=2" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Ответ покажет ID правила, например: "id": 10

# 2. Обновить правило
curl -X PATCH http://localhost:8000/api/admin/access-rules/10/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"create_permission": true}'

# 3. Теперь user может создавать товары!
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Мышка Gaming",
    "price": 3500
  }'

# Успех! (раньше было бы 403)
```

### 9. Выход и удаление аккаунта
```bash
# Выход (удаление сессии)
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer $TOKEN"

# Попытка использовать токен после выхода
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer $TOKEN"

# Ответ:
{
  "error": "Authentication required",
  "detail": "Invalid or expired token"
}

# Мягкое удаление аккаунта (is_active=False)
curl -X DELETE http://localhost:8000/api/auth/me/delete/ \
  -H "Authorization: Bearer $TOKEN"

# Попытка войти с удаленным аккаунтом
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"petr@example.com","password":"securepass123"}'

# Ответ:
{
  "non_field_errors": ["Аккаунт деактивирован"]
}
```

### 10. Обработка ошибок
```bash
# Неверный пароль (401)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"wrong"}'

# Ответ:
{
  "non_field_errors": ["Неверный email или пароль"]
}

# Пароли не совпадают при регистрации (400)
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "test@test.com",
    "password": "pass123",
    "password_confirm": "different"
  }'

# Ответ:
{
  "password_confirm": ["Пароли не совпадают"]
}

# Email уже существует (400)
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "user@example.com",
    "password": "pass123",
    "password_confirm": "pass123"
  }'

# Ответ:
{
  "email": ["Пользователь с таким email уже существует"]
}

# Запрос без токена (401)
curl -X GET http://localhost:8000/api/orders/

# Ответ:
{
  "error": "Authentication required",
  "detail": "No valid token provided"
}

# Недостаточно прав (403)
curl -X DELETE http://localhost:8000/api/products/1/ \
  -H "Authorization: Bearer $USER_TOKEN"

# Ответ:
{
  "error": "Forbidden",
  "detail": "Access denied"
}

# Объект не найден (404)
curl -X GET http://localhost:8000/api/products/999/ \
  -H "Authorization: Bearer $TOKEN"

# Ответ:
{
  "error": "Product not found"
}
```

### 11. Пакетные операции
```bash
# Создать несколько заказов подряд
for i in {1..3}; do
  curl -X POST http://localhost:8000/api/orders/ \
    -H "Authorization: Bearer $USER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"product_id\": $i, \"quantity\": 1}"
done

# Получить статистику по правам всех ролей
for role_id in {1..4}; do
  echo "=== Роль ID: $role_id ==="
  curl -s -X GET "http://localhost:8000/api/admin/access-rules/?role_id=$role_id" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    | python3 -m json.tool
done
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

### Матрица прав

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

---

## Архитектура
```
CLIENT (Authorization: Bearer TOKEN)
    ↓
CustomAuthMiddleware
    ↓
@require_permission (проверяет права в access_rules)
    ↓
View
    ↓
Response
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