# Вариант №10. Сервис статуса сотрудника (Employee Status Service)

## 1. Общие положения

*   **Формат дат:** Все даты передаются и возвращаются в формате `YYYY-MM-DD`.
*   **Удаление данных:** Для всех сущностей применяется **Soft Delete** (логическое удаление).
    *   Поле `is_active` указывает на актуальность записи.
    *   При запросе на "удаление" поле `is_active` устанавливается в `False`.
    *   Физическое удаление записей из базы данных не производится.
*   **Совместительство:** Реализуется через множественные записи `EmployeePosition` для одного `profile_id`.
    *   `is_primary = True`: Основная ставка.
    *   `is_primary = False`: Внутреннее совместительство (дополнительная ставка).

## 2. Справочник должностей (Position)

Сущность, описывающая штатные должности компании.

### 2.1. Создать должность (Create Position)

**Входные параметры:**

| Параметр | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|----------------|-----|-------------|----------------------|
| title | Да | string | Название должности, не пустое | — |
| code | Да | string | Уникальный код (например, `DEV-SEN`) | — |
| department | Нет | string | Название подразделения | — |

**Ответ при успехе (201 Created):**

| Параметр | Тип | Описание |
|----------|-----|----------|
| id | int | ID должности |
| title | string | Название |
| code | string | Код |
| department | string | Подразделение |
| is_active | bool | Статус активности (`true`) |
| created_at | str | Timestamp создания |
| updated_at | str | Timestamp обновления |

### 2.2. Изменить должность (Update Position)

**Входные параметры:** (Все необязательные)

| Параметр | Тип | Ограничение |
|----------|-----|-------------|
| title | string | Не пустое |
| code | string | Уникальное в рамках системы |
| department | string | — |

**Ответ при успехе (200 OK):** Полный объект `Position`.

### 2.3. Удалить должность (Delete Position)

*   Выполняет Soft Delete (`is_active = False`).
*   **Ограничение:** Нельзя деактивировать должность, если существуют активные ставки сотрудников (`EmployeePosition` с `is_active=true`), ссылающиеся на неё.
*   Возвращает `True` при успехе, `False` если запись не найдена или заблокирована связями.

### 2.4. Получить должность по ID (Get Position)

Возвращает объект `Position`. Если `is_active = false`, запись все равно возвращается (с соответствующим флагом).

### 2.5. Список должностей (List Positions)

**Параметры фильтрации:**
*   `title` (string): Поиск по подстроке.
*   `code` (string): Точное совпадение или подстрока.
*   `is_active` (bool): По умолчанию `true`.

**Ответ:** Список объектов `Position`.

## 3. Ставка сотрудника (EmployeePosition)

Связывает сотрудника (`Profile`) с должностью (`Position`). Определяет основную работу или внутреннее совместительство.

### 3.1. Создать ставку (Create EmployeePosition)

**Бизнес-правила:**
1.  У одного сотрудника (`profile_id`) может быть только **одна** активная ставка с `is_primary = True`.
2.  Если создается новая ставка с `is_primary = True`, у предыдущей основной ставки этого сотрудника флаг автоматически сбрасывается в `False` (она становится совместительством).
3.  `start_date` не может быть в будущем.

**Входные параметры:**

| Параметр | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|----------------|-----|-------------|----------------------|
| profile_id | Да | int | ID сотрудника (внешняя система) | — |
| position_id | Да | int | ID должности (из таблицы Position) | — |
| rate | Да | float | Диапазон [0.1; 2.0] | 1.0 |
| is_primary | Да | bool | `True` — основная, `False` — совместительство | False |
| start_date | Да | date | Не может быть > текущей даты | — |
| end_date | Нет | date | Должна быть > start_date | None |

**Ответ при успехе (201 Created):**

| Параметр | Тип | Описание |
|----------|-----|----------|
| id | int | ID записи |
| profile_id | int | ID сотрудника |
| position_id | int | ID должности |
| rate | float | Размер ставки |
| is_primary | bool | Признак основного места |
| start_date | str | Дата начала |
| end_date | str | Дата окончания (или null) |
| is_active | bool | `true` |
| created_at | str | Timestamp |
| updated_at | str | Timestamp |

### 3.2. Изменить ставку (Update EmployeePosition)

**Бизнес-правила:**
*   При установке `is_primary = True` срабатывает логика переключения основной ставки (см. п. 3.1).
*   Нельзя изменить `position_id`, если есть активные отпуска/больничные на текущей позиции (опциональное ограничение).

**Входные параметры:**

| Параметр | Обязательность | Тип | Ограничение |
|----------|----------------|-----|-------------|
| rate | Нет | float | [0.1; 2.0] |
| is_primary | Нет | bool | — |
| end_date | Нет | date | > start_date |
| position_id | Нет | int | ID новой должности |

**Ответ при успехе (200 OK):** Полный объект `EmployeePosition`.

### 3.3. Удалить ставку (Delete EmployeePosition)

*   Soft Delete (`is_active = False`).
*   Возвращает `True` при успехе, `False` если не найдено.
*   *Примечание:* При деактивации ставки рекомендуется проверять наличие активных отпусков/больничных.

### 3.4. Получить ставку по ID (Get EmployeePosition)

Возвращает полный объект, включая `is_active`.

### 3.5. Список ставок (List EmployeePositions)

**Параметры фильтрации:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| profile_id | int | Фильтр по сотруднику |
| position_id | int | Фильтр по должности |
| is_primary | bool | `True` — только основные, `False` — только совместители |
| is_active | bool | По умолчанию `true` |
| start_date_from | date | Начало периода старта (>=) |
| start_date_to | date | Конец периода старта (<=) |

**Ответ:** Список объектов `EmployeePosition`.

## 4. Отпуск (Leave)

Привязан к конкретной ставке (`EmployeePosition`).

### 4.1. Создать отпуск (Create Leave)

**Входные параметры:**

| Параметр | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|----------------|-----|-------------|----------------------|
| employee_position_id | Да | int | Ссылка на активную ставку | — |
| start_date | Да | date | < end_date | — |
| end_date | Да | date | > start_date | — |
| leave_type | Да | str | Enum: `annual`, `unpaid`, `study` | `annual` |
| status | Да | str | Enum: `pending`, `approved`, `rejected` | `pending` |

**Ответ при успехе (201 Created):**

| Параметр | Тип |
|----------|-----|
| id | int |
| employee_position_id | int |
| start_date | str |
| end_date | str |
| leave_type | str |
| status | str |
| is_active | bool |
| created_at | str |
| updated_at | str |

### 4.2. Изменить отпуск (Update Leave)

**Входные параметры:**

| Параметр | Обязательность | Тип | Ограничение |
|----------|----------------|-----|-------------|
| start_date | Нет | date | < end_date |
| end_date | Нет | date | > start_date |
| status | Нет | str | `pending`, `approved`, `rejected` |

**Ответ при успехе (200 OK):** Полный объект `Leave`.

### 4.3. Удалить отпуск (Delete Leave)

*   Soft Delete (`is_active = False`).
*   Возвращает `True`/`False`.

### 4.4. Получить отпуск по ID (Get Leave)

Возвращает полный объект.

### 4.5. Список отпусков (List Leaves)

**Параметры фильтрации:**
*   `employee_position_id` (int)
*   `leave_type` (str)
*   `status` (str)
*   `is_active` (bool, default `true`)
*   `start_date_from` (date)
*   `start_date_to` (date)

**Ответ:** Список объектов `Leave`.

## 5. Больничный (SickLeave)

Привязан к конкретной ставке (`EmployeePosition`).

### 5.1. Создать больничный (Create SickLeave)

**Входные параметры:**

| Параметр | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|----------------|-----|-------------|----------------------|
| employee_position_id | Да | int | Ссылка на активную ставку | — |
| start_date | Да | date | Не может быть в будущем | — |
| end_date | Да | date | >= start_date | — |
| certificate_number | Да | str | Уникальный номер листа нетрудоспособности | — |
| status | Да | str | Enum: `active`, `closed` | `active` |

**Ответ при успехе (201 Created):**

| Параметр | Тип |
|----------|-----|
| id | int |
| employee_position_id | int |
| start_date | str |
| end_date | str |
| certificate_number | str |
| status | str |
| is_active | bool |
| created_at | str |
| updated_at | str |

### 5.2. Изменить больничный (Update SickLeave)

**Входные параметры:**

| Параметр | Обязательность | Тип | Ограничение |
|----------|----------------|-----|-------------|
| end_date | Нет | date | >= start_date |
| status | Нет | str | `active`, `closed` |

**Ответ при успехе (200 OK):** Полный объект `SickLeave`.

### 5.3. Удалить больничный (Delete SickLeave)

*   Soft Delete (`is_active = False`).
*   Возвращает `True`/`False`.

### 5.4. Получить больничный по ID (Get SickLeave)

Возвращает полный объект.

### 5.5. Список больничных (List SickLeaves)

**Параметры фильтрации:**
*   `employee_position_id` (int)
*   `status` (str)
*   `is_active` (bool, default `true`)
*   `start_date_from` (date)
*   `start_date_to` (date)
*   `certificate_number` (str, поиск по подстроке)

**Ответ:** Список объектов `SickLeave`.

## ER-диаграмма

