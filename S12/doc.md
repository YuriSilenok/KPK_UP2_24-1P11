# Вариант №12. Сервис учебного плана (Curriculum Plan Service)

#### Создание учебного плана

Information required for creating a curriculum plan

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| name | Curriculum plan name | Yes | string | not empty | — |
| speciality_id | Specialty ID from service 6 | Yes | integer | exists in service 6 | — |
| year | Curriculum plan year | Yes | integer | > 2000 | — |

**Unique combinations:** —

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| name | string |
| speciality_id | integer |
| year | integer |
| is_active | boolean |

---

#### Получение учебного плана по ID

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| id | Curriculum plan ID | Yes | integer | exists in DB | — |

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| name | string |
| speciality_id | integer |
| year | integer |
| is_active | boolean |

---

#### Получение списка учебных планов

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| year | Filter by year | No | integer | > 2000 | — |
| speciality_id | Filter by specialty | No | integer | — | — |

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| name | string |
| speciality_id | integer |
| year | integer |
| is_active | boolean |

---

#### Обновление учебного плана

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| id | Curriculum plan ID | Yes | integer | exists in DB | — |
| name | Curriculum plan name | No | string | not empty | — |
| speciality_id | Specialty ID from service 6 | No | integer | exists in service 6 | — |
| year | Curriculum plan year | No | integer | > 2000 | — |

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| name | string |
| speciality_id | integer |
| year | integer |
| is_active | boolean |

---

#### Удаление учебного плана

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| id | Curriculum plan ID | Yes | integer | exists in DB | — |

**Response**

| Parameter | Type |
|-----------|------|
| success | boolean |

*Soft delete (is_active = false). Returns true if record was found and deactivated, false if already inactive or not found.*

---

#### Добавление дисциплины

**Information required for creating a subject**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| curriculum_plan_id | Curriculum plan ID | Yes | integer | exists in DB | — |
| name | Subject name | Yes | string | not empty | — |
| semester | Semester number | Yes | integer | 1–12 | — |

**Unique combinations:** —

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| curriculum_plan_id | integer |
| name | string |
| semester | integer |
| is_active | boolean |

---

#### Получение дисциплины по ID

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| id | Subject ID | Yes | integer | exists in DB | — |

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| curriculum_plan_id | integer |
| name | string |
| semester | integer |
| is_active | boolean |

---

#### Получение списка дисциплин

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| curriculum_plan_id | Filter by curriculum plan | No | integer | — | — |
| semester | Filter by semester | No | integer | 1–12 | — |

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| curriculum_plan_id | integer |
| name | string |
| semester | integer |
| is_active | boolean |

---

#### Обновление дисциплины

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| id | Subject ID | Yes | integer | exists in DB | — |
| name | Subject name | No | string | not empty | — |
| semester | Semester number | No | integer | 1–12 | — |

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| curriculum_plan_id | integer |
| name | string |
| semester | integer |
| is_active | boolean |

---

#### Удаление дисциплины

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| id | Subject ID | Yes | integer | exists in DB | — |

**Response**

| Parameter | Type |
|-----------|------|
| success | boolean |

---

#### Добавление часов

**Information required for adding hours**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| subject_id | Subject ID | Yes | integer | exists in DB | — |
| lecture_hours | Lecture hours | Yes | integer | >= 0 | 0 |
| practice_hours | Practice hours | Yes | integer | >= 0 | 0 |

**Unique combinations:** `subject_id` (one subject can have only one hours record)

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| lecture_hours | integer |
| practice_hours | integer |
| is_active | boolean |

---

#### Получение часов по ID

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| id | Hours ID | Yes | integer | exists in DB | — |

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| lecture_hours | integer |
| practice_hours | integer |
| is_active | boolean |

---

#### Получение часов по дисциплине

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| subject_id | Subject ID | Yes | integer | exists in DB | — |

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| lecture_hours | integer |
| practice_hours | integer |
| is_active | boolean |

---

#### Обновление часов

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| id | Hours ID | Yes | integer | exists in DB | — |
| lecture_hours | Lecture hours | No | integer | >= 0 | — |
| practice_hours | Practice hours | No | integer | >= 0 | — |

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| lecture_hours | integer |
| practice_hours | integer |
| is_active | boolean |

---

#### Удаление часов

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| id | Hours ID | Yes | integer | exists in DB | — |

**Response**

| Parameter | Type |
|-----------|------|
| success | boolean |

---

#### Добавление формы контроля

**Information required for adding an assessment**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| subject_id | Subject ID | Yes | integer | exists in DB | — |
| type | Assessment type | Yes | enum | exam / zachet | — |

**Unique combinations:** `(subject_id, type)` — one subject cannot have two assessments of the same type

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| type | enum |
| is_active | boolean |

---

#### Получение формы контроля по ID

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| id | Assessment ID | Yes | integer | exists in DB | — |

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| type | enum |
| is_active | boolean |

---

#### Получение форм контроля по дисциплине

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| subject_id | Subject ID | Yes | integer | exists in DB | — |

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| type | enum |
| is_active | boolean |

---

#### Обновление формы контроля

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| id | Assessment ID | Yes | integer | exists in DB | — |
| type | Assessment type | No | enum | exam / zachet | — |

**Response**

| Parameter | Type |
|-----------|------|
| id | integer |
| subject_id | integer |
| type | enum |
| is_active | boolean |

---

#### Удаление формы контроля

**Input parameters**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| id | Assessment ID | Yes | integer | exists in DB | — |

**Response**

| Parameter | Type |
|-----------|------|
| success | boolean |

---

### ER-диаграмма

```mermaid
erDiagram
    CURRICULUM_PLAN {
        int id PK
        string name
        int speciality_id FK
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