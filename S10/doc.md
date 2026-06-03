# Сервис статуса сотрудника (Employee Status Service) – Вариант 10

## Список функций
- `create_employee` – создание записи о сотруднике
- `update_employee` – изменение статусной информации сотрудника
- `delete_employee` – мягкое удаление (is_active = False)
- `get_employee` – получение сотрудника по ID
- `list_employees` – получение списка сотрудников с фильтрацией и пагинацией

---

## Сущность «Сотрудник»

### 1. Создание сотрудника (`create_employee`)

**Информация, требуемая для создания сотрудника**


| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|-----------|----------------|-----|-------------|-----------------------|
| `user_id` | ID сотрудника из Profile Service | Да | int | уникальный | – |
| `hire_date` | Дата найма | Да | date | не раньше 1900-01-01 | – |
| `status` | Текущий статус | Нет | string | active / on_vacation / sick_leave / fired | `'active'` |

**Уникальные комбинации:** `user_id` (глобально уникален)

**Информация, возвращаемая при успешном создании**


| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| `id` | Внутренний ID записи (PK) | int |
| `user_id` | ID из Profile Service | int |
| `hire_date` | Дата найма | date |
| `status` | Текущий статус | string |
| `updated_at` | Дата и время создания | datetime |

---

### 2. Изменение сотрудника по ID (`update_employee`)

**Информация, требуемая для изменения** (все поля опциональны)


| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|-----------|----------------|-----|-------------|-----------------------|
| `hire_date` | Дата найма | Нет | date | не раньше 1900-01-01 | – |
| `status` | Статус | Нет | string | active / on_vacation / sick_leave / fired | – |

**Информация, возвращаемая при успешном изменении**


| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| `id` | Внутренний ID записи | int |
| `user_id` | ID из Profile Service | int |
| `hire_date` | Дата найма | date |
| `status` | Текущий статус | string |
| `updated_at` | Дата и время последнего обновления | datetime |

---

### 3. Удаление сотрудника по ID (`delete_employee`)

> Метод производит логическое (мягкое) удаление путем перевода флага `is_active` в `False`. Физического зачищения строк в БД не происходит.

**Возвращаемое значение:** `True / False` (bool)

---

### 4. Получение сотрудника по ID (`get_employee`)

**Информация, возвращаемая при успешном поиске**


| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| `id` | Внутренний ID записи | int |
| `user_id` | ID из Profile Service | int |
| `hire_date` | Дата найма | date |
| `status` | Текущий статус | string |
| `is_active` | Статус активности записи | boolean |
| `updated_at` | Дата и время последнего обновления | datetime |
| `positions` | Список должностей (Вычисляемое свойство ORM-модели на основе JOIN) | list |

*Примечание:* Параметр `positions` не является физическим столбцом таблицы `employees`. Это динамическое вычисляемое свойство (property) уровня приложения, агрегирующее данные из связанных таблиц `employee_positions` и `positions`. Structure: `[{"position_title": string, "start_date": string, "end_date": string, "load_factor": float}]`.

---

### 5. Получение списка сотрудников по заданным параметрам (`list_employees`)

**Параметры для получения списка**


| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|-----------|----------------|-----|-------------|-----------------------|
| `user_id` | ID сотрудника | Нет | int | точное совпадение | – |
| `status` | Статус | Нет | string | точное совпадение | – |
| `position_id` | Должность | Нет | int | фильтрация через транзитивную таблицу | – |
| `hire_date_from` | Дата найма от | Нет | date | диапазон (`>=`) | – |
| `hire_date_to` | Дата найма до | Нет | date | диапазон (`<=`) | – |
| `limit` | Лимит записей | Нет | int | пагинация | `100` |
| `offset` | Смещение | Нет | int | для пагинации | – |

**Информация, возвращаемая в виде списка сотрудников**


| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| `id` | Внутренний ID записи | int |
| `user_id` | ID из Profile Service | int |
| `hire_date` | Дата найма | date |
| `status` | Текущий статус | string |
| `is_active` | Статус активности записи | boolean |
| `position_id` | Идентификатор связанной должности (из транзитивной таблицы) | int |

---

## Дополнительное описание API сопутствующих таблиц

### 6. Управление должностями (`positions`)
Позволяет просматривать базовые справочные данные должностей, используемые транзитивной таблицей.
- **Входные данные:** `id` (int), `title` (string), `description` (text).
- **Выходные данные:** Полный объект должности.

### 7. Управление назначениями (`employee_positions`)
Обеспечивает связь сотрудников с должностями для построения сложных структур.
- **Входные данные:** `employee_id` (int), `position_id` (int), `start_date` (date), `end_date` (date), `load_factor` (float).
- **Выходные данные:** Объект связи параметров назначения.

### 8. Логирование отпусков (`vacations`)
Учет периодов отдыха, привязанных к сотруднику.
- **Входные данные:** `employee_id` (int), `start_date` (date), `end_date` (date), `type` (string).
- **Выходные данные:** Запись лога отпуска.

### 9. Логирование больничных (`sick_leaves`)
Учет периодов нетрудоспособности, привязанных к сотруднику.
- **Входные данные:** `employee_id` (int), `start_date` (date), `end_date` (date), `diagnosis` (text).
- **Выходные данные:** Запись лога больничного листа.

---

## ER-диаграмма

```mermaid
erDiagram
    employees {
        int id PK
        int user_id FK "NOT NULL"
        date hire_date "NOT NULL"
        string status "NOT NULL"
        boolean is_active "DEFAULT true"
        datetime updated_at "NOT NULL"
    }
    positions {
        int id PK
        string title "NOT NULL"
        text description "NOT NULL"
    }
    employee_positions {
        int id PK
        int employee_id FK "NOT NULL"
        int position_id FK "NOT NULL"
        date start_date "NOT NULL"
        date end_date "NULL"
        float load_factor "NOT NULL"
    }
    vacations {
        int id PK
        int employee_id FK "NOT NULL"
        date start_date "NOT NULL"
        date end_date "NOT NULL"
        string type "NOT NULL"
    }
    sick_leaves {
        int id PK
        int employee_id FK "NOT NULL"
        date start_date "NOT NULL"
        date end_date "NOT NULL"
        text diagnosis "NOT NULL"
    }

    employees ||--o{ employee_positions : "employee_positions.employee_id -> employees.id"
    positions ||--o{ employee_positions : "employee_positions.position_id -> positions.id"
    employees ||--o{ vacations : "vacations.employee_id -> employees.id"
    employees ||--o{ sick_leaves : "sick_leaves.employee_id -> employees.id"
```

### Список реляционных связей
- Связь между таблицами **`employees`** и **`employee_positions`** осуществляется по полям: `employee_positions.employee_id` (int, FK) ➔ `employees.id` (int, PK).
- Связь между таблицами **`positions`** и **`employee_positions`** осуществляется по полям: `employee_positions.position_id` (int, FK) ➔ `positions.id` (int, PK).
- Связь между таблицами **`employees`** и **`vacations`** осуществляется по полям: `vacations.employee_id` (int, FK) ➔ `employees.id` (int, PK).
- Связь между таблицами **`employees`** и **`sick_leaves`** осуществляется по полям: `sick_leaves.employee_id` (int, FK) ➔ `employees.id` (int, PK).
- Внешняя логическая связь с **Profile Service**: `employees.user_id` (int, FK) ➔ `profiles.id` (int, PK) внешнего сервиса.
