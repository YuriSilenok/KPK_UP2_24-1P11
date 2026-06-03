# Employee Status Service

## ER-диаграмма

```mermaid
erDiagram

    Position {
        int id PK
        string name
        boolean is_active
    }

    EmployeeStatus {
        int id PK
        int employee_id
        int position_id FK
        float rate
        boolean is_part_time
        date start_date
        date end_date
        boolean is_active
    }

    Vacation {
        int id PK
        int employee_id
        date start_date
        date end_date
        string vacation_type
        boolean is_active
    }

    SickLeave {
        int id PK
        int employee_id
        date start_date
        date end_date
        string document_number
        boolean is_active
    }

    Position ||--o{ EmployeeStatus : "id -> position_id"
```

# Position

## 1. Добавить сущность

### Информация для создания

| Параметр (англ.) | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
|---|---|---|---|---|---|
| name | Наименование должности | Да | string | ≤255 символов | - |

### Уникальные комбинации параметров

| Параметр |
|---|
| name |

### Информация при успешном создании

| Параметр (англ.) | Тип |
|---|---|
| id | integer |

## 2. Изменить сущность по ID

### Информация для изменения

| Параметр (англ.) | Пояснение | Обязательность | Тип | Ограничение |
|---|---|---|---|---|
| name | Наименование должности | Нет | string | ≤255 символов |

### Информация при успешном изменении

| Параметр (англ.) | Тип |
|---|---|
| result | boolean |

...
