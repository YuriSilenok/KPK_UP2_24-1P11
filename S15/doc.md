
**Связи:**
- Teacher (1) ----< LoadAssignment (M)
- Discipline (1) ----< LoadAssignment (M)
- Group (1) ----< LoadAssignment (M)

**Транзитивные таблицы:** отсутствуют (связи многие-ко-многим не требуются)

## API Description

### 1. Add LoadAssignment

**Request body:**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| teacher_id | Teacher ID | Yes | int | Foreign Key | - |
| discipline_id | Discipline ID | Yes | int | Foreign Key | - |
| group_id | Group ID | Yes | int | Foreign Key | - |

**Unique combination:** (teacher_id, discipline_id, group_id)

**Response (201):**

| Parameter | Type |
|-----------|------|
| id | int |
| teacher_id | int |
| discipline_id | int |
| group_id | int |
| is_active | bool |

### 2. Update LoadAssignment by ID

**Request body:**

| Parameter | Description | Required | Type | Constraint |
|-----------|-------------|----------|------|------------|
| teacher_id | Teacher ID | No | int | Foreign Key |
| discipline_id | Discipline ID | No | int | Foreign Key |
| group_id | Group ID | No | int | Foreign Key |

**Response (200):**

| Parameter | Type |
|-----------|------|
| id | int |
| teacher_id | int |
| discipline_id | int |
| group_id | int |
| is_active | bool |

### 3. Delete LoadAssignment by ID (Soft Delete)

Returns: `true` if found and marked as deleted, otherwise `false`

### 4. Get LoadAssignment by ID

**Response (200):**

| Parameter | Description | Type |
|-----------|-------------|------|
| id | Record ID | int |
| teacher_id | Teacher ID | int |
| discipline_id | Discipline ID | int |
| group_id | Group ID | int |
| is_active | Active flag | bool |

### 5. Get LoadAssignments by filters

**Query parameters:**

| Parameter | Description | Type |
|-----------|-------------|------|
| teacher_id | Filter by teacher | int |
| discipline_id | Filter by discipline | int |
| group_id | Filter by group | int |
| is_active | Filter by active status | bool |

**Response (200):**

| Parameter | Type |
|-----------|------|
| id | int |
| teacher_id | int |
| discipline_id | int |
| group_id | int |
| is_active | bool |
# Сервис распределения нагрузки (Load Assignment Service)
Вариант №15

## ER-диаграмма (Mermaid)

```mermaid
erDiagram
    Teacher {
        int id PK
    }
    Discipline {
        int id PK
    }
    Group {
        int id PK
    }
    LoadAssignment {
        int id PK
        int teacher_id FK
        int discipline_id FK
        int group_id FK
        bool is_active
    }
    Teacher ||--o{ LoadAssignment : has
    Discipline ||--o{ LoadAssignment : has
    Group ||--o{ LoadAssignment : has
