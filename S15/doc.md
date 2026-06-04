# Вариант №15. Load Assignment Service

## ER-Diagram

```mermaid
erDiagram
    TEACHERS {
        integer id PK
    }
    DISCIPLINES {
        integer id PK
    }
    GROUPS {
        integer id PK
    }
    LOAD_ASSIGNMENTS {
        integer id PK
        integer teacher_id FK
        integer discipline_id FK
        integer group_id FK
        boolean is_active
    }

    TEACHERS ||--o{ LOAD_ASSIGNMENTS : "assigned"
    DISCIPLINES ||--o{ LOAD_ASSIGNMENTS : "assigned"
    GROUPS ||--o{ LOAD_ASSIGNMENTS : "assigned"
```

**Список реляционных связей:**
* `TEACHERS.id` связывается с `LOAD_ASSIGNMENTS.teacher_id`
* `DISCIPLINES.id` связывается с `LOAD_ASSIGNMENTS.discipline_id`
* `GROUPS.id` связывается с `LOAD_ASSIGNMENTS.group_id`

## API Description

### 1. Add LoadAssignment

**Request body:**


| Parameter | Description | Required | Type | Constraint | Default |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **teacher_id** | Teacher ID | Yes | int | - | - |
| **discipline_id** | Discipline ID | Yes | int | - | - |
| **group_id** | Group ID | Yes | int | - | - |

*Unique combination: (teacher_id, discipline_id, group_id)*

**Response (201):**


| Parameter | Type |
| :--- | :--- |
| **id** | int |
| **teacher_id** | int |
| **discipline_id** | int |
| **group_id** | int |
| **is_active** | bool |

### 2. Update LoadAssignment by ID

**Request body:**


| Parameter | Description | Required | Type | Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **teacher_id** | Teacher ID | No | int | - |
| **discipline_id** | Discipline ID | No | int | - |
| **group_id** | Group ID | No | int | - |

**Информация при успешном изменении (Response 200):**


| Parameter | Type |
| :--- | :--- |
| **id** | int |
| **teacher_id** | int |
| **discipline_id** | int |
| **group_id** | int |
| **is_active** | bool |

### 3. Delete LoadAssignment by ID

**Response (204):**
*Без тела ответа (No Content)*

### 4. Get LoadAssignment by ID

**Response (200):**


| Parameter | Type |
| :--- | :--- |
| **id** | int |
| **teacher_id** | int |
| **discipline_id** | int |
| **group_id** | int |
| **is_active** | bool |

### 5. Get LoadAssignment List

**Request query parameters:**


| Parameter | Description | Required | Type |
| :--- | :--- | :--- | :--- |
| **teacher_id** | Filter by Teacher ID | No | int |
| **discipline_id** | Filter by Discipline ID | No | int |
| **group_id** | Filter by Group ID | No | int |

**Response (200):**
*Массив объектов следующего вида:*


| Parameter | Type |
| :--- | :--- |
| **id** | int |
| **teacher_id** | int |
| **discipline_id** | int |
| **group_id** | int |
| **is_active** | bool |
