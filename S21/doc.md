## Вариант №21. Сервис каникул и праздников (Holiday)

### Инициализация БД

При первом запуске приложения функция `init_db()` создаёт таблицы в базе данных.

### Работа с праздниками (Holiday)

#### Добавление Holiday

Информация требуемая для создания Holiday

| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|-----------|----------------|-----|-------------|----------------------|
| name | Название праздника | Да | string | Не пустое, до 100 символов | — |
| date | Дата праздника | Да | date | Конкретная дата | — |
| type_id | Тип (ссылка на HolidayType) | Да | integer | Ссылка на HolidayType | — |
| is_active | Статус активности | Нет | boolean | — | True |

Информация возвращаемая в случае удачного создания Holiday

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| date | date |
| type_id | integer |
| is_active | boolean |

#### Изменение Holiday по ID

Информация требуемая для изменения Holiday по ID

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| id | Идентификатор | Да | integer | Существует в БД |
| name | Название праздника | Нет | string | Не пустое, до 100 символов |
| date | Дата праздника | Нет | date | Не пустое |
| type_id | Тип (ссылка на HolidayType) | Нет | integer | Ссылка на HolidayType |
| is_active | Статус активности | Нет | boolean | — |

Информация возвращаемая в случае удачного изменения Holiday

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| date | date |
| type_id | integer |
| is_active | boolean |

#### Удаление Holiday по ID

Запись фактически из БД не удаляется, а реализуется через булевое поле is_active. Вернет True, если Holiday был закрыт (удален), иначе вернет False.

#### Получить Holiday по ID

Информация возвращаемая в случае удачного поиска Holiday по ID

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| id | Идентификатор | integer |
| name | Название праздника | string |
| date | Дата праздника | date |
| type_id | Тип (ссылка на HolidayType) | integer |
| is_active | Статус активности | boolean |

#### Получить список Holiday по заданным параметрам

Информация требуемая для получения списка Holiday

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| date_from | Дата начала периода поиска | date |
| date_to | Дата окончания периода поиска | date |
| type_id | Тип праздника (ссылка на HolidayType) | integer |

Информация возвращается в виде списка Holiday

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| date | date |
| type_id | integer |
| is_active | boolean |

### Работа с периодами каникул (VacationPeriod)

#### Добавление VacationPeriod

Информация требуемая для создания VacationPeriod

| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|-----------|----------------|-----|-------------|----------------------|
| name | Название периода | Да | string | Не пустое, до 100 символов | — |
| start_date | Дата начала каникул | Да | date | Дата начала | — |
| end_date | Дата окончания каникул | Да | date | >= start_date | — |
| type_id | Тип (ссылка на HolidayType) | Да | integer | Ссылка на HolidayType | — |
| is_active | Статус активности | Нет | boolean | — | True |

Информация возвращаемая в случае удачного создания VacationPeriod

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| start_date | date |
| end_date | date |
| type_id | integer |
| is_active | boolean |

#### Изменение VacationPeriod по ID

Информация требуемая для изменения VacationPeriod по ID

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
|----------|-----------|----------------|-----|-------------|
| id | Идентификатор | Да | integer | Существует в БД |
| name | Название периода | Нет | string | Не пустое, до 100 символов |
| start_date | Дата начала каникул | Нет | date | Не пустое |
| end_date | Дата окончания каникул | Нет | date | Не пустое, >= start_date |
| type_id | Тип (ссылка на HolidayType) | Нет | integer | Ссылка на HolidayType |
| is_active | Статус активности | Нет | boolean | — |

Информация возвращаемая в случае удачного изменения VacationPeriod

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| start_date | date |
| end_date | date |
| type_id | integer |
| is_active | boolean |

#### Удаление VacationPeriod по ID

Запись фактически из БД не удаляется, а реализуется через булевое поле is_active. Вернет True, если VacationPeriod был закрыт (удален), иначе вернет False.

#### Получить VacationPeriod по ID

Информация возвращаемая в случае удачного поиска VacationPeriod по ID

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| id | Идентификатор | integer |
| name | Название периода | string |
| start_date | Дата начала каникул | date |
| end_date | Дата окончания каникул | date |
| type_id | Тип (ссылка на HolidayType) | integer |
| is_active | Статус активности | boolean |

#### Получить список VacationPeriod

Информация требуемая для получения списка VacationPeriod

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| type_id | Тип периода (ссылка на HolidayType) | integer |
| is_active | Фильтр по статусу активности | boolean |
| start_date_from | Начало периода попадает в указанный диапазон (от) | date |
| start_date_to | Начало периода попадает в указанный диапазон (до) | date |
| end_date_from | Конец периода попадает в указанный диапазон (от) | date |
| end_date_to | Конец периода попадает в указанный диапазон (до) | date |

Информация возвращается в виде списка VacationPeriod

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| start_date | date |
| end_date | date |
| type_id | integer |
| is_active | boolean |

### Работа с типами праздников (HolidayType)

#### Добавление HolidayType

Информация требуемая для создания HolidayType

| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|-----------|----------------|-----|-------------|----------------------|
| name | Название типа | Да | string | Не пустое, до 50 символов | — |
| code | Код типа | Да | string | Уникальное, не пустое, до 8 символов | — |
| is_active | Статус активности | Нет | boolean | — | True |

Информация возвращаемая в случае удачного создания HolidayType

| Параметр | Тип |
|----------|-----|
| id | integer |
| name | string |
| code | string |
| is_active | boolean |

#### Изменение HolidayType по ID

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

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| id | Идентификатор | integer |
| name | Название типа | string |
| code | Код типа | string |
| is_active | Статус активности | boolean |

#### Получить список HolidayType

Информация требуемая для получения списка HolidayType

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| is_active | Фильтр по статусу активности | boolean |

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
    
    HOLIDAY_TYPE ||--o{ HOLIDAY : "type_id -> id"
    HOLIDAY_TYPE ||--o{ VACATION_PERIOD : "type_id -> id"
