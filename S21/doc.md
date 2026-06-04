### Вариант №21. Сервис каникул и праздников (Holiday)

### Инициализация БД

При первом запуске приложения функция `init_db()` создаёт таблицы и добавляет начальные данные в справочник HolidayType:
- name='Праздник', code='holiday'
- name='Каникулы', code='vacation'

### Работа с праздниками (Holiday)

#### Добавление Holiday

Информация требуемая для создания Holiday

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| name | Название праздника | Да | string | Не пустое, до 100 символов |
| date | Дата праздника | Да | date | Конкретная дата |
| type | Тип (ссылка на HolidayType) | Да | integer | Ссылка на HolidayType |
| is_active | Статус активности | Нет | boolean | — |

Информация возвращаемая в случае удачного создания Holiday

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| date | date |
| type | integer |
| is_active | boolean |

#### Изменение Holiday по ID

Обновляются только переданные поля, остальные остаются без изменений.

Информация требуемая для изменения Holiday по ID

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| id | Идентификатор | Да | integer | Существует в БД |
| name | Название праздника | Нет | string | Не пустое, до 100 символов |
| date | Дата праздника | Нет | date | Не пустое |
| type | Тип (ссылка на HolidayType) | Нет | integer | Ссылка на HolidayType |
| is_active | Статус активности | Нет | boolean | — |

Информация возвращаемая в случае удачного изменения Holiday

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| date | date |
| type | integer |
| is_active | boolean |

#### Удаление Holiday по ID

Запись фактически из БД не удаляется, а реализуется через булевое поле is_active. Вернет True, если Holiday был закрыт (удален), иначе вернет False.

#### Получить Holiday по ID

Информация возвращаемая в случае удачного поиска Holiday по ID

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| date | date |
| type | integer |
| is_active | boolean |

#### Получить список Holiday по заданным параметрам

Информация требуемая для получения списка Holiday

| Параметр | Пояснение | Обязательность | Тип |
|----------|-----------|----------------|-----|
| date_from | Дата начала периода | Нет | date |
| date_to | Дата окончания периода | Нет | date |
| type | Тип праздника (ссылка на HolidayType) | Нет | integer |

Информация возвращается в виде списка Holiday

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| date | date |
| type | integer |
| is_active | boolean |

### Работа с периодами каникул (VacationPeriod)

#### Добавление VacationPeriod

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| name | Название периода | Да | string | Не пустое, до 100 символов |
| start_date | Дата начала каникул | Да | date | Дата начала |
| end_date | Дата окончания каникул | Да | date | >= start_date |
| type | Тип (ссылка на HolidayType) | Да | integer | Ссылка на HolidayType |
| is_active | Статус активности | Нет | boolean | — |

Информация возвращаемая в случае удачного создания VacationPeriod

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| start_date | date |
| end_date | date |
| type | integer |
| is_active | boolean |

#### Изменение VacationPeriod по ID

Обновляются только переданные поля, остальные остаются без изменений.

Информация требуемая для изменения VacationPeriod по ID

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| id | Идентификатор | Да | integer | Существует в БД |
| name | Название периода | Нет | string | Не пустое, до 100 символов |
| start_date | Дата начала каникул | Нет | date | Не пустое |
| end_date | Дата окончания каникул | Нет | date | Не пустое, >= start_date |
| type | Тип (ссылка на HolidayType) | Нет | integer | Ссылка на HolidayType |
| is_active | Статус активности | Нет | boolean | — |

Информация возвращаемая в случае удачного изменения VacationPeriod

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| start_date | date |
| end_date | date |
| type | integer |
| is_active | boolean |

#### Удаление VacationPeriod по ID

Запись фактически из БД не удаляется, а реализуется через булевое поле is_active. Вернет True, если VacationPeriod был закрыт (удален), иначе вернет False.

#### Получить VacationPeriod по ID

Информация возвращаемая в случае удачного поиска VacationPeriod по ID

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| start_date | date |
| end_date | date |
| type | integer |
| is_active | boolean |

#### Получить список VacationPeriod

Информация требуемая для получения списка VacationPeriod

| Параметр | Пояснение | Обязательность | Тип |
|----------|-----------|----------------|-----|
| type | Тип периода (ссылка на HolidayType) | Нет | integer |
| is_active | Фильтр по статусу активности (True — активные, False — неактивные) | Нет | boolean |

Информация возвращается в виде списка VacationPeriod

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| start_date | date |
| end_date | date |
| type | integer |
| is_active | boolean |

### Работа с типами праздников (HolidayType)

#### Добавление HolidayType

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| name | Название типа | Да | string | Не пустое, до 50 символов |
| code | Код типа | Да | string | Уникальное, не пустое, до 8 символов |
| is_active | Статус активности | Нет | boolean | — |

Информация возвращаемая в случае удачного создания HolidayType

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| code | string |
| is_active | boolean |

#### Изменение HolidayType по ID

Обновляются только переданные поля, остальные остаются без изменений.

Информация требуемая для изменения HolidayType по ID

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| id | Идентификатор | Да | integer | Существует в БД |
| name | Название типа | Нет | string | Не пустое, до 50 символов |
| code | Код типа | Нет | string | Уникальное, не пустое, до 8 символов |
| is_active | Статус активности | Нет | boolean | — |

Информация возвращаемая в случае удачного изменения HolidayType

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| code | string |
| is_active | boolean |

#### Удаление HolidayType по ID

Запись фактически из БД не удаляется, а реализуется через булевое поле is_active. Вернет True, если HolidayType был закрыт (удален), иначе вернет False.

#### Получить HolidayType по ID

Информация возвращаемая в случае удачного поиска HolidayType по ID

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| code | string |
| is_active | boolean |

#### Получить список HolidayType

Информация требуемая для получения списка HolidayType

| Параметр | Пояснение | Обязательность | Тип |
|----------|-----------|----------------|-----|
| is_active | Фильтр по статусу активности (True — активные, False — неактивные) | Нет | boolean |

Информация возвращается в виде списка HolidayType

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| code | string |
| is_active | boolean |

### ER-диаграмма

```mermaid
erDiagram
    HOLIDAY_TYPE {
        int id PK
        string name
        string code
        boolean is_active
    }
    
    HOLIDAY {
        int id PK
        string name
        date date
        int type_id FK
        boolean is_active
    }
    
    VACATION_PERIOD {
        int id PK
        string name
        date start_date
        date end_date
        int type_id FK
        boolean is_active
    }
    
    HOLIDAY_TYPE ||--o{ HOLIDAY : "has_type"
    HOLIDAY_TYPE ||--o{ VACATION_PERIOD : "has_type"
