

**Связи:**
- teacher_id ссылается на Teacher.id (внешний сервис)
- discipline_id ссылается на Discipline.id (внешний сервис)
- group_id ссылается на Group.id (внешний сервис)

**Транзитивные таблицы:** отсутствуют

## API Description

### 1. Add LoadAssignment

**Request body:**

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|------------|---------|
| teacher_id | Teacher ID | Yes | int | - | - |
| discipline_id | Discipline ID | Yes | int | - | - |
| group_id | Group ID | Yes | int | - | - |

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
| teacher_id | Teacher ID | No | int | - |
| discipline_id | Discipline ID | No | int | - |
| group_id | Group ID | No | int | - |

**Response (200):**

| Parameter | Type |
|-----------|------|
| id | int |
| teacher_id | int |
| discipline_id | int |
| group_id | int |
| is_active | bool |

### 3. Delete LoadAssignment by ID (Soft Delete)

При удалении `is_active` устанавливается в `False`.

**Response:**

| Parameter | Type |
|-----------|------|
| success | bool |

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
# LOAD_ASSIGNMENT Service (Вариант №15)

## ER-Diagram

```mermaid
erDiagram
    LOAD_ASSIGNMENT {
        int id PK
        int teacher_id
        int discipline_id
        int group_id
        bool is_active
    }
