# Вариант №12. Curriculum Service

## Group

... [здесь содержимое без изменений] ...

---

## Discipline

... [здесь содержимое без изменений] ...

---

## Semester

... [здесь содержимое без изменений] ...

---

## Curriculum

#### Создание Curriculum

| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **group_id** | ID группы | Обязательно | Целое | > 0 | — |
| **discipline_id** | ID дисциплины | Обязательно | Целое | > 0 | — |
| **semester_id** | ID семестра | Обязательно | Целое | > 0 | — |
| **theory_hours** | Часы теории | Обязательно | Целое | ≥ 0 | — |
| **practice_hours** | Часы практики | Обязательно | Целое | ≥ 0 | — |
| **assessment_form** | Форма отчетности | Обязательно | Строка | exam / credit | — |

Уникальные комбинации: (group_id, discipline_id, semester_id)

Выходные данные

| Параметр | Тип |
| :--- | :--- |
| **id** | Целое |
| **group_id** | Целое |
| **discipline_id** | Целое |
| **semester_id** | Целое |
| **theory_hours** | Целое |
| **practice_hours** | Целое |
| **assessment_form** | Строка |
| **is_active** | Логический |

#### Получение Curriculum по ID

Входные параметры

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
| :--- | :--- | :--- | :--- | :--- |
| **id** | ID записи | Обязательно | Целое | > 0 |

Выходные данные

| Параметр | Тип |
| :--- | :--- |
| **id** | Целое |
| **group_id** | Целое |
| **discipline_id** | Целое |
| **semester_id** | Целое |
| **theory_hours** | Целое |
| **practice_hours** | Целое |
| **assessment_form** | Строка |
| **is_active** | Логический |

#### Получение списка Curriculum

Входные параметры

| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **group_id** | Фильтр по группе | Необязательно | Целое | > 0 | — |
| **discipline_id** | Фильтр по дисциплине | Необязательно | Целое | > 0 | — |
| **semester_id** | Фильтр по семестру | Необязательно | Целое | > 0 | — |
| **assessment_form** | Фильтр по форме | Необязательно | Строка | exam / credit | — |
| **theory_hours_min** | Мин. часов теории | Необязательно | Целое | ≥ 0 | — |
| **theory_hours_max** | Макс. часов теории | Необязательно | Целое | ≥ 0 | — |
| **practice_hours_min** | Мин. часов практики | Необязательно | Целое | ≥ 0 | — |
| **practice_hours_max** | Макс. часов практики | Необязательно | Целое | ≥ 0 | — |
| **is_active** | Фильтр по активности | Необязательно | Логический | — | true |
| **page** | Номер страницы | Необязательно | Целое | ≥ 1 | 1 |
| **page_size** | Размер страницы | Необязательно | Целое | 1-100 | 20 |

Выходные данные

| Параметр | Тип |
| :--- | :--- |
| **id** | Целое |
| **group_id** | Целое |
| **discipline_id** | Целое |
| **semester_id** | Целое |
| **theory_hours** | Целое |
| **practice_hours** | Целое |
| **assessment_form** | Строка |
| **is_active** | Логический |

#### Обновление Curriculum

Входные параметры

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
| :--- | :--- | :--- | :--- | :--- |
| **id** | ID записи | Обязательно | Целое | > 0 |
| **theory_hours** | Новые часы теории | Необязательно | Целое | ≥ 0 |
| **practice_hours** | Новые часы практики | Необязательно | Целое | ≥ 0 |
| **assessment_form** | Новая форма отчетности | Необязательно | Строка | exam / credit |

> **Примечание:** Поля **group_id**, **discipline_id**, **semester_id** и **is_active** изменять запрещено. Они отсутствуют в списке входных параметров.

Выходные данные

| Параметр | Тип |
| :--- | :--- |
| **id** | Целое |
| **group_id** | Целое |
| **discipline_id** | Целое |
| **semester_id** | Целое |
| **theory_hours** | Целое |
| **practice_hours** | Целое |
| **assessment_form** | Строка |
| **is_active** | Логический |

#### Удаление Curriculum

Входные параметры

| Параметр | Пояснение | Обязательность | Тип | Ограничение |
| :--- | :--- | :--- | :--- | :--- |
| **id** | ID записи | Обязательно | Целое | > 0 |

Выходные данные

| Параметр | Тип |
| :--- | :--- |
| **success** | Логический |

*Мягкое удаление (is_active = false). Возвращает true если запись найдена и деактивирована, false если уже неактивна или не найдена.*

---
## ER-диаграмма и список связей

### Список реляционных связей:
*   `groups.id` → `curriculum.group_id`
*   `disciplines.id` → `curriculum.discipline_id`
*   `semesters.id` → `curriculum.semester_id`

```mermaid
erDiagram
    groups {
        int id PK
        string name
        bool is_active
    }
    
    disciplines {
        int id PK
        string name
        bool is_active
    }
    
    semesters {
        int id PK
        int semester_number
        string academic_year
        bool is_active
    }
    
    curriculum { # ИСПРАВЛЕНА ОПЕЧАТКА: curriculum вместо curriculum
        int id PK
        int group_id FK
        int discipline_id FK
        int semester_id FK
        int theory_hours
        int practice_hours
        string assessment_form
        bool is_active
    }
    
    // Связи с указанием кардинальности (один ко многим)
    groups ||--o{ curriculum : "Учебная группа"
    disciplines ||--o{ curriculum : "Дисциплина"
    semesters ||--o{ curriculum : "Семестр"