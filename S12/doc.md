# Вариант №12. Сервис учебного плана (Curriculum Plan Service)

#### Создание учебного плана

Информация требуемая для создания учебного плана

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| name | Yes | string | not empty | — |
| speciality_id | Yes | integer | exists in service 6 | — |
| year | Yes | integer | > 2000 | — |

Unique combinations: —

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| name | string |
| speciality_id | integer |
| year | integer |
| is_active | boolean |

---

#### Получение учебного плана по ID

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| id | Yes | integer | exists in DB | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| name | string |
| speciality_id | integer |
| year | integer |
| is_active | boolean |

---

#### Получение списка учебных планов

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| year | No | integer | > 2000 | — |
| speciality_id | No | integer | — | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| name | string |
| speciality_id | integer |
| year | integer |
| is_active | boolean |

---

#### Обновление учебного плана

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| id | Yes | integer | exists in DB | — |
| name | No | string | not empty | — |
| speciality_id | No | integer | exists in service 6 | — |
| year | No | integer | > 2000 | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| name | string |
| speciality_id | integer |
| year | integer |
| is_active | boolean |

---

#### Удаление учебного плана

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| id | Yes | integer | exists in DB | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| success | boolean |

*Мягкое удаление (is_active = false). Возвращает true если запись найдена и деактивирована, false если уже неактивна или не найдена.*

---

#### Добавление дисциплины

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| curriculum_plan_id | Yes | integer | exists in DB | — |
| name | Yes | string | not empty | — |
| semester | Yes | integer | 1–12 | — |

Unique combinations: —

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| name | string |
| semester | integer |
| is_active | boolean |

---

#### Получение дисциплины по ID

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| id | Yes | integer | exists in DB | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| name | string |
| semester | integer |
| is_active | boolean |

---

#### Получение списка дисциплин

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| curriculum_plan_id | No | integer | — | — |
| semester | No | integer | 1–12 | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| name | string |
| semester | integer |
| is_active | boolean |

---

#### Обновление дисциплины

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| id | Yes | integer | exists in DB | — |
| name | No | string | not empty | — |
| semester | No | integer | 1–12 | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| name | string |
| semester | integer |
| is_active | boolean |

---

#### Удаление дисциплины

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| id | Yes | integer | exists in DB | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| success | boolean |

---

#### Добавление часов

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| subject_id | Yes | integer | exists in DB | — |
| lecture_hours | Yes | integer | >= 0 | 0 |
| practice_hours | Yes | integer | >= 0 | 0 |

Unique combinations: subject_id (у одной дисциплины может быть только один набор часов)

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| lecture_hours | integer |
| practice_hours | integer |
| is_active | boolean |

---

#### Получение часов по ID

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| id | Yes | integer | exists in DB | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| lecture_hours | integer |
| practice_hours | integer |
| is_active | boolean |

---

#### Получение часов по дисциплине

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| subject_id | Yes | integer | exists in DB | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| lecture_hours | integer |
| practice_hours | integer |
| is_active | boolean |

---

#### Обновление часов

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| id | Yes | integer | exists in DB | — |
| lecture_hours | No | integer | >= 0 | — |
| practice_hours | No | integer | >= 0 | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| lecture_hours | integer |
| practice_hours | integer |
| is_active | boolean |

---

#### Удаление часов

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| id | Yes | integer | exists in DB | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| success | boolean |

---

#### Добавление формы контроля

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| subject_id | Yes | integer | exists in DB | — |
| type | Yes | enum | exam / zachet | — |

Unique combinations: (subject_id, type) — у одной дисциплины не может быть двух одинаковых типов контроля

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| type | enum |
| is_active | boolean |

---

#### Получение формы контроля по ID

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| id | Yes | integer | exists in DB | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| type | enum |
| is_active | boolean |

---

#### Получение форм контроля по дисциплине

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| subject_id | Yes | integer | exists in DB | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| type | enum |
| is_active | boolean |

---

#### Обновление формы контроля

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| id | Yes | integer | exists in DB | — |
| type | No | enum | exam / zachet | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| type | enum |
| is_active | boolean |

---

#### Удаление формы контроля

Входные параметры

| Parameter | Required | Type | Constraint | Default |
|-----------|----------|------|------------|---------|
| id | Yes | integer | exists in DB | — |

Выходные данные

| Parameter | Type |
|-----------|------|
| success | boolean |

---

## ER-диаграмма

```mermaid
erDiagram
    CURRICULUM_PLAN {
        int id PK
        string name
        int speciality_id
        int year
        bool is_active
    }

    SUBJECT {
        int id PK
        int curriculum_plan_id FK
        string name
        int semester
        bool is_active
    }

    HOURS {
        int id PK
        int subject_id FK
        int lecture_hours
        int practice_hours
        bool is_active
    }

    ASSESSMENT {
        int id PK
        int subject_id FK
        string type
        bool is_active
    }

    CURRICULUM_PLAN ||--o{ SUBJECT : contains
    SUBJECT ||--o{ HOURS : has
    SUBJECT ||--o{ ASSESSMENT : has