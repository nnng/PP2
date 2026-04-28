# PhoneBook TSIS1 — Extended Contact Management

Приложение для управления контактами с поддержкой расширенной модели данных: несколько телефонов на контакт, email, дата рождения, группы и полнотекстовый поиск.

## Содержание

- [Установка](#установка)
- [Структура проекта](#структура-проекта)
- [Использование](#использование)
- [Просмотр данных в pgAdmin](#просмотр-данных-в-pgadmin)
- [SQL-запросы](#sql-запросы)
- [Меню программы](#меню-программы)

---

## Установка

### 1. Подготовка БД

Откройте pgAdmin или подключитесь к PostgreSQL и выполните скрипты в этом порядке:

```bash
psql -U postgres -d phonebook_db -f create_table.sql
psql -U postgres -d phonebook_db -f procedures.sql
psql -U postgres -d phonebook_db -f functions.sql
```

Или в pgAdmin:
1. Откройте базу данных `phonebook_db`
2. Откройте Query Tool (Ctrl+Shift+Q)
3. Скопируйте содержимое `create_table.sql` → выполните (F5)
4. Повторите для `procedures.sql` и `functions.sql`

### 2. Настройка подключения

Отредактируйте `database.ini`:

```ini
[postgresql]
host=localhost
database=phonebook_db
user=postgres
password=ВАШ_ПАРОЛЬ
port=5432
```

### 3. Запуск программы

```bash
python main.py
```

---

## Структура проекта

```
PhoneBook/
├── main.py                      # Главное меню
├── database.ini                 # Параметры подключения
├── create_table.sql             # Схема БД (contacts, phones, groups)
├── procedures.sql               # Хранимые процедуры
├── functions.sql                # Функции поиска и пагинации
├── data.csv                     # Пример CSV для импорта
├── README.md                    # Этот файл
├── db/
│   └── connection.py            # Модуль подключения
├── services/
│   └── phonebook_service.py     # Бизнес-логика
└── utils/
    └── csv_loader.py            # CSV-импорт
```

---

## Использование

Запустите программу:

```bash
python main.py
```

Откроется меню:

```
========= PHONEBOOK MENU =========
1. Add or update contact
2. Load contacts from CSV
3. Search contacts by text
4. Filter / sort / paginate contacts
5. Update contact manually
6. Delete contact by name, surname, or phone
7. Add phone to contact
8. Move contact to group
9. Export contacts to JSON
10. Import contacts from JSON
11. Exit
```

### Примеры использования

#### 1️⃣ Добавить контакт

```
Choose: 1
Name: Иван
Surname: Иванов
Phone (optional): +7-777-123-4567
Phone type home / work / mobile [mobile]: work
Email (optional): ivan@example.com
Birthday YYYY-MM-DD (optional): 1990-05-15
Group Family / Work / Friend / Other (optional): Work
Contact saved successfully.
```

#### 2️⃣ Импортировать из CSV

Файл `data.csv`:
```csv
name,surname,phone,phone_type,email,birthday,group
Ainur,Kazbekova,87070001122,mobile,ainur@mail.com,1995-03-20,Friend
Ruslan,Toktarov,87789876543,work,ruslan@company.kz,1988-07-10,Work
```

```
Choose: 2
CSV path: data.csv
Contacts loaded from CSV.
```

#### 3️⃣ Поиск контактов

Поиск по имени, фамилии, email, телефону:

```
Choose: 3
Search text (name, surname, email, or phone): gmail
1. John Smith | group: Friend | email: john@gmail.com | birthday: - | added: 2026-04-28 12:34:56
   phones: mobile: +1-234-567-8900, work: +1-987-654-3210
```

#### 4️⃣ Фильтрация и пагинация

```
Choose: 4
Search text (leave empty for all): 
Filter by group (leave empty for all): Work
Sort by name / birthday / date added [name]: name
Page size [5]: 5

Page 1 of 2 | total contacts: 8
1. Alex Johnson | group: Work | email: alex@work.com | birthday: 1992-01-15 | added: 2026-04-28 12:10:00
   phones: work: +1-555-0100

next / prev / quit: next
```

#### 5️⃣ Добавить телефон к контакту

```
Choose: 7
Contact name or full name: Иван Иванов
Phone: +7-777-999-8888
Phone type home / work / mobile [mobile]: home
Phone added successfully.
```

#### 6️⃣ Переместить контакт в группу

```
Choose: 8
Contact name or full name: Иван Иванов
New group: Family
Contact moved successfully.
```

#### 7️⃣ Экспорт в JSON

```
Choose: 9
JSON export path: contacts_backup.json
Contacts exported successfully.
```

Результат в `contacts_backup.json`:
```json
[
  {
    "id": 1,
    "name": "Иван",
    "surname": "Иванов",
    "email": "ivan@example.com",
    "birthday": "1990-05-15",
    "group": "Work",
    "created_at": "2026-04-28 12:30:00",
    "phones": [
      {"phone": "+7-777-123-4567", "type": "work"},
      {"phone": "+7-777-999-8888", "type": "home"}
    ]
  }
]
```

---

## Просмотр данных в pgAdmin

### Способ 1: Быстрый просмотр таблиц

1. Откройте **pgAdmin** → Базы данных → `phonebook_db`
2. Разверните **Schemas** → **public** → **Tables**
3. Кликните правой кнопкой на таблицу (`contacts`, `phones`, `groups`):
   - **View/Edit Data** → **All Rows** (или First 100)

### Способ 2: Query Tool (РЕКОМЕНДУЕТСЯ)

1. Откройте **pgAdmin** → базу `phonebook_db`
2. Нажмите **Ctrl+Shift+Q** (Query Tool) или откройте через меню
3. Скопируйте запрос из раздела ниже
4. Нажмите **F5** или кнопку **Execute**

---

## SQL-запросы

### 📋 Все контакты со всеми телефонами

```sql
SELECT
    c.id,
    c.name,
    c.surname,
    c.email,
    c.birthday,
    g.name AS "group",
    c.created_at,
    p.phone,
    p.type AS phone_type
FROM contacts c
LEFT JOIN groups g ON g.id = c.group_id
LEFT JOIN phones p ON p.contact_id = c.id
ORDER BY c.name, c.surname, p.id;
```

**Результат**: каждый номер телефона на отдельной строке, удобно для анализа.

---

### 👥 Контакты с объединённым списком телефонов (РЕКОМЕНДУЕТСЯ)

```sql
SELECT
    c.id,
    c.name,
    c.surname,
    c.email,
    c.birthday,
    g.name AS "group",
    c.created_at,
    string_agg(p.phone || ' (' || p.type || ')', ', ') AS all_phones
FROM contacts c
LEFT JOIN groups g ON g.id = c.group_id
LEFT JOIN phones p ON p.contact_id = c.id
GROUP BY c.id, c.name, c.surname, c.email, c.birthday, g.name, c.created_at
ORDER BY c.name, c.surname;
```

**Результат**: один контакт на одну строку, все номера в одной ячейке (например: `+7-777-123-4567 (work), +7-777-999-8888 (home)`).

---

### 🔍 Поиск контакта по имени и все его телефоны

```sql
SELECT
    c.id,
    c.name,
    c.surname,
    c.email,
    c.birthday,
    g.name AS "group",
    p.phone,
    p.type AS phone_type,
    c.created_at
FROM contacts c
LEFT JOIN groups g ON g.id = c.group_id
LEFT JOIN phones p ON p.contact_id = c.id
WHERE LOWER(c.name) LIKE '%иван%' OR LOWER(c.surname) LIKE '%иван%'
ORDER BY c.name, c.surname, p.id;
```

Измените `'%иван%'` на имя/фамилию, которую ищете.

---

### 👨‍👩‍👧‍👦 Все контакты конкретной группы

```sql
SELECT
    c.id,
    c.name,
    c.surname,
    c.email,
    c.birthday,
    c.created_at,
    string_agg(p.phone || ' (' || p.type || ')', ', ') AS phones
FROM contacts c
LEFT JOIN groups g ON g.id = c.group_id
LEFT JOIN phones p ON p.contact_id = c.id
WHERE g.name = 'Work'
GROUP BY c.id, c.name, c.surname, c.email, c.birthday, c.created_at
ORDER BY c.name, c.surname;
```

Измените `'Work'` на нужную группу: `Family`, `Friend`, `Other`.

---

### 📞 Все номера телефонов по типам

```sql
SELECT
    p.type,
    COUNT(*) AS count,
    string_agg(p.phone, ', ') AS all_phones
FROM phones p
GROUP BY p.type
ORDER BY p.type;
```

---

### 🎂 Контакты с днями рождения в этом месяце

```sql
SELECT
    c.id,
    c.name,
    c.surname,
    c.birthday,
    c.email,
    g.name AS "group",
    string_agg(p.phone || ' (' || p.type || ')', ', ') AS phones
FROM contacts c
LEFT JOIN groups g ON g.id = c.group_id
LEFT JOIN phones p ON p.contact_id = c.id
WHERE EXTRACT(MONTH FROM c.birthday) = EXTRACT(MONTH FROM NOW())
GROUP BY c.id, c.name, c.surname, c.birthday, c.email, g.name
ORDER BY EXTRACT(DAY FROM c.birthday);
```

---

### 📊 Статистика по группам

```sql
SELECT
    COALESCE(g.name, 'No Group') AS "group",
    COUNT(DISTINCT c.id) AS contact_count,
    COUNT(p.id) AS phone_count,
    ROUND(COUNT(p.id) * 1.0 / COUNT(DISTINCT c.id), 2) AS avg_phones_per_contact
FROM groups g
LEFT JOIN contacts c ON c.group_id = g.id
LEFT JOIN phones p ON p.contact_id = c.id
GROUP BY g.name
ORDER BY contact_count DESC;
```

---

### 🔗 Контакты без телефонов

```sql
SELECT
    c.id,
    c.name,
    c.surname,
    c.email,
    c.birthday,
    g.name AS "group",
    c.created_at
FROM contacts c
LEFT JOIN groups g ON g.id = c.group_id
WHERE NOT EXISTS (SELECT 1 FROM phones WHERE contact_id = c.id)
ORDER BY c.name, c.surname;
```

---

### ⚡ Последние добавленные контакты

```sql
SELECT
    c.id,
    c.name,
    c.surname,
    c.email,
    c.birthday,
    g.name AS "group",
    c.created_at,
    string_agg(p.phone || ' (' || p.type || ')', ', ') AS phones
FROM contacts c
LEFT JOIN groups g ON g.id = c.group_id
LEFT JOIN phones p ON p.contact_id = c.id
GROUP BY c.id, c.name, c.surname, c.email, c.birthday, g.name, c.created_at
ORDER BY c.created_at DESC
LIMIT 10;
```

---

## Меню программы (подробно)

### Команда 1: Добавить или обновить контакт
- Вводите: имя, фамилия, номер (опционально), тип номера, email, день рождения, группа
- Если контакт существует → обновится
- Если новый → добавится в "Other"

### Команда 2: Импортировать из CSV
- **Обязательно**: `name, surname, phone`
- **Опционально**: `phone_type, email, birthday, group_name`
- Заголовок пропускается автоматически

### Команда 3: Поиск контактов
- Ищет по: имени, фамилии, email, телефону
- Поиск регистронезависимый

### Команда 4: Фильтрация, сортировка и пагинация
- **Сортировка**: `name`, `birthday`, `date added`
- **Фильтр**: по группе (опционально)
- **Навигация**: `next`, `prev`, `quit`

### Команда 5: Обновить контакт вручную
- Найти по: текущему имени и фамилии
- Обновить: имя, фамилию, номер, email, день рождения, группу

### Команда 6: Удалить контакт
- По имени, фамилии, полному имени или номеру

### Команда 7: Добавить телефон
- К существующему контакту

### Команда 8: Переместить в группу
- Если группы нет → создастся автоматически

### Команда 9: Экспорт в JSON
- Все контакты с деталями в JSON файл

### Команда 10: Импорт из JSON
- При совпадении → `skip` или `overwrite`

---

## Требования

```
Python 3.10+
PostgreSQL 12+
psycopg2-binary
```

Установка:
```bash
pip install psycopg2-binary
```

---

## Резервная копия

### Экспорт БД
```bash
pg_dump -U postgres phonebook_db > backup.sql
```

### Через программу
```
Choose: 9
JSON export path: backup_2026_04_28.json
```

---

**PhoneBook TSIS1** — учебный проект для Programming Principles 2
