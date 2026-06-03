# Employee Status Service

## Назначение

Сервис хранит информацию о статусе сотрудников:

- должности;
- ставки;
- совместительство;
- отпуска;
- больничные.

Данные о сотруднике хранятся в другом сервисе, поэтому используется только поле `employee_id`.

## ER-диаграмма

```mermaid
erDiagram

    POSITION {
        int id PK
        string name
    }

    EMPLOYEE_STATUS {
        int id PK
        int employee_id
        int position_id FK
        float rate
        boolean is_part_time
        date start_date
        date end_date
    }

    VACATION {
        int id PK
        int employee_status_id FK
        date start_date
        date end_date
        string vacation_type
    }

    SICK_LEAVE {
        int id PK
        int employee_status_id FK
        date start_date
        date end_date
        string document_number
    }

    POSITION ||--o{ EMPLOYEE_STATUS : assigned
    EMPLOYEE_STATUS ||--o{ VACATION : has
    EMPLOYEE_STATUS ||--o{ SICK_LEAVE : has
