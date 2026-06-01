# Вариант №2. Сервис статуса сотрудника (Employee Status Service)

## Номер варианта и название сервиса

**Вариант №2** - **Сервис статуса сотрудника (Employee Status Service)**

## Сущность 2: EmployeePosition (Ставка сотрудника)

### Информация, требуемая для создания EmployeePosition

| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|-----------|----------------|-----|-------------|----------------------|
| profile_id | ID сотрудника из Profile Service | Обязательно | int | Внешний ключ | — |
| position_id | ID должности | Обязательно | int | Внешний ключ | — |
| rate | Ставка (0.5, 0.75, 1.0 и т.д.) | Обязательно | float | От 0.1 до 2.0 | 1.0 |
| is_primary | Основное место работы | Обязательно | bool | — | False |
| start_date | Дата начала работы | Обязательно | date | Не может быть в будущем | — |
| end_date | Дата окончания работы | Не обязательно | date | Должна быть после start_date | None |

**Уникальные комбинации параметров:**
- `(profile_id, is_primary)` - у сотрудника может быть только одно основное место работы
- `(profile_id, position_id, start_date)` - уникальная комбинация для истории

### Информация, возвращаемая в случае успешного создания EmployeePosition

| Параметр | Тип |
|----------|-----|
| id | int |
| profile_id | int |
| position_id | int |
| rate | float |
| is_primary | bool |
| start_date | str |                                                                             -----
| end_date | str (или None) |                                                                    -----
| is_active | bool |
| created_at | str |
| updated_at | str |

---

### Изменить EmployeePosition по ID

**Информация, требуемая для изменения EmployeePosition по ID**

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| rate | Ставка | Не обязательно | float | От 0.1 до 2.0 |
| is_primary | Основное место работы | Не обязательно | bool | — |
| end_date | Дата окончания | Не обязательно | date | После start_date |

**Информация, возвращаемая в случае успешного изменения EmployeePosition**

| Параметр | Тип |
|----------|-----|
| id | int |
| profile_id | int |
| position_id | int |
| rate | float |
| is_primary | bool |
| start_date | str |
| end_date | str (или None) |
| is_active | bool |
| created_at | str |
| updated_at | str |

---

### Удаление EmployeePosition по ID

Вернет **True**, если ставка была успешно помечена как удаленная (soft delete через поле `is_active=False`), иначе вернет **False**.

### Получить EmployeePosition по ID

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| id | ID ставки | int |
| profile_id | ID сотрудника | int |
| position_id | ID должности | int |
| rate | Ставка | float |
| is_primary | Основное место | bool |
| start_date | Дата начала | str |
| end_date | Дата окончания | str (или None) |
| is_active | Активна ли ставка | bool |
| created_at | Дата создания | str |
| updated_at | Дата обновления | str |

### Получить список EmployeePositions

**Параметры фильтрации:**

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| profile_id | ID сотрудника | int |
| position_id | ID должности | int |
| is_primary | Основное место работы | bool |
| is_active | Активна ли ставка | bool |
| start_date_from | Дата начала от | date |
| start_date_to | Дата начала до | date |

**Возвращаемые данные:** список EmployeePosition (все поля)

---

## Сущность 3: Leave (Отпуск)

### Информация, требуемая для создания Leave

| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|-----------|----------------|-----|-------------|----------------------|
| employee_position_id | ID ставки сотрудника | Обязательно | int | Внешний ключ | — |
| start_date | Дата начала отпуска | Обязательно | date | Не может быть в прошлом | — |
| end_date | Дата окончания отпуска | Обязательно | date | Должна быть после start_date | — |
| leave_type | Тип отпуска | Обязательно | str | annual/sick/unpaid | annual |
| status | Статус отпуска | Обязательно | str | pending/approved/rejected | pending |

**Уникальные комбинации параметров:** нет

### Информация, возвращаемая в случае успешного создания Leave

| Параметр | Тип |
|----------|-----|
| id | int |
| employee_position_id | int |
| start_date | str |
| end_date | str |
| leave_type | str |
| status | str |
| created_at | str |
| updated_at | str |

---

### Изменить Leave по ID

**Информация, требуемая для изменения Leave по ID**

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| start_date | Дата начала | Не обязательно | date | — |
| end_date | Дата окончания | Не обязательно | date | После start_date |
| status | Статус | Не обязательно | str | pending/approved/rejected |

**Информация, возвращаемая в случае успешного изменения Leave**

| Параметр | Тип |
|----------|-----|
| id | int |
| employee_position_id | int |
| start_date | str |
| end_date | str |
| leave_type | str |
| status | str |
| created_at | str |
| updated_at | str |

---

### Удаление Leave по ID

Вернет **True**, если отпуск был успешно удален, иначе вернет **False**.

### Получить Leave по ID

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| id | ID отпуска | int |
| employee_position_id | ID ставки сотрудника | int |
| start_date | Дата начала | str |
| end_date | Дата окончания | str |
| leave_type | Тип отпуска | str |
| status | Статус отпуска | str |
| created_at | Дата создания | str |
| updated_at | Дата обновления | str |

### Получить список Leaves

**Параметры фильтрации:**

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| employee_position_id | ID ставки сотрудника | int |
| leave_type | Тип отпуска | str |
| status | Статус отпуска | str |
| start_date_from | Дата начала от | date |
| start_date_to | Дата начала до | date |

**Возвращаемые данные:** список Leave (все поля)

---

## Сущность 4: SickLeave (Больничный)

### Информация, требуемая для создания SickLeave

| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|-----------|----------------|-----|-------------|----------------------|
| employee_position_id | ID ставки сотрудника | Обязательно | int | Внешний ключ | — |
| start_date | Дата начала больничного | Обязательно | date | Не может быть в будущем | — |
| end_date | Дата окончания больничного | Обязательно | date | Должна быть после start_date | — |
| certificate_number | Номер больничного листа | Обязательно | str | Уникальный, не пустой | — |
| status | Статус | Обязательно | str | active/closed | active |

**Уникальные комбинации параметров:** `certificate_number`

### Информация, возвращаемая в случае успешного создания SickLeave

| Параметр | Тип |
|----------|-----|
| id | int |
| employee_position_id | int |
| start_date | str |
| end_date | str |
| certificate_number | str |
| status | str |
| created_at | str |
| updated_at | str |

---

### Изменить SickLeave по ID

**Информация, требуемая для изменения SickLeave по ID**

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| end_date | Дата окончания | Не обязательно | date | После start_date |
| status | Статус | Не обязательно | str | active/closed |

**Информация, возвращаемая в случае успешного изменения SickLeave**

| Параметр | Тип |
|----------|-----|
| id | int |
| employee_position_id | int |
| start_date | str |
| end_date | str |
| certificate_number | str |
| status | str |
| created_at | str |
| updated_at | str |

---

### Удаление SickLeave по ID

Вернет **True**, если больничный был успешно удален, иначе вернет **False**.

### Получить SickLeave по ID

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| id | ID больничного | int |
| employee_position_id | ID ставки сотрудника | int |
| start_date | Дата начала | str |
| end_date | Дата окончания | str |
| certificate_number | Номер больничного листа | str |
| status | Статус | str |
| created_at | Дата создания | str |
| updated_at | Дата обновления | str |

### Получить список SickLeaves

**Параметры фильтрации:**

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| employee_position_id | ID ставки сотрудника | int |
| status | Статус больничного | str |
| start_date_from | Дата начала от | date |
| start_date_to | Дата начала до | date |

**Возвращаемые данные:** список SickLeave (все поля)

---

## ER-диаграмма

