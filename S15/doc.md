# 15. Load Assignment Service (Сервис распределения нагрузки)

## Общие коды HTTP-статусов
| Успех | Код | Ошибка | Код |
|-------|-----|--------|-----|
| GET (один) | 200 | Не найдено | 404 |
| GET (список) | 200 | Неверный параметр | 400 |
| POST (создание) | 201 | Конфликт (дубликат) | 409 |
| PUT (обновление) | 200 | Ошибка валидации | 422 |
| DELETE | 204 | Ошибка сервера | 500 |

## Общая структура ошибки
| Параметр | Тип | Пояснение |
|----------|-----|-----------|
| error | string | Тип ошибки |
| message | string | Описание ошибки |

## LoadAssignment
| Поле | Тип | Обязательность | Ограничение | Пояснение |
|------|-----|----------------|-------------|-----------|
| id | integer | Да | PK | Идентификатор |
| teacher_id | integer | Да | FK -> Teacher.id | ID преподавателя |
| discipline_id | integer | Да | FK -> Discipline.id | ID дисциплины |
| group_id | integer | Да | FK -> Group.id | ID группы |
| semester | integer | Да | CHECK (1-8) | Номер семестра |
| load_hours | decimal(5,2) | Да | CHECK (>0) | Часы |
| is_deleted | boolean | Да | default False | Флаг логического удаления |

## Teacher
| Поле | Тип | Обязательность | Ограничение | Пояснение |
|------|-----|----------------|-------------|-----------|
| id | integer | Да | PK | Идентификатор |
| full_name | varchar(200) | Да | NOT NULL, UNIQUE | ФИО |
| position | varchar(100) | Да | NOT NULL | Должность |

## Discipline
| Поле | Тип | Обязательность | Ограничение | Пояснение |
|------|-----|----------------|-------------|-----------|
| id | integer | Да | PK | Идентификатор |
| name | varchar(200) | Да | NOT NULL, UNIQUE | Название |
| hours_total | integer | Да | NOT NULL | Часы |

## Group
| Поле | Тип | Обязательность | Ограничение | Пояснение |
|------|-----|----------------|-------------|-----------|
| id | integer | Да | PK | Идентификатор |
| group_number | varchar(20) | Да | NOT NULL, UNIQUE | Номер |
| specialty_id | integer | Да | NOT NULL | Специальность |

## Student
| Поле | Тип | Обязательность | Ограничение | Пояснение |
|------|-----|----------------|-------------|-----------|
| id | integer | Да | PK | Идентификатор |
| student_number | varchar(50) | Нет | UNIQUE | Номер студента |
| current_group_id | integer | Нет | FK -> Group.id | ID группы |
| status | varchar(50) | Да | NOT NULL | Статус |

## Уникальные комбинации параметров для LoadAssignment
- (teacher_id, discipline_id, group_id, semester)

## Добавить LoadAssignment

### Параметры запроса
| Параметр | Тип | Обязательность | Ограничение | Пояснение |
|----------|-----|----------------|-------------|-----------|
| teacher_id | integer | Да | FK -> Teacher.id | ID преподавателя |
| discipline_id | integer | Да | FK -> Discipline.id | ID дисциплины |
| group_id | integer | Да | FK -> Group.id | ID группы |
| semester | integer | Да | 1-8 | Номер семестра |
| load_hours | decimal(5,2) | Да | >0 | Часы |

### Возвращаемые данные при успешном создании (HTTP 201)
| Параметр | Тип |
|----------|-----|
| id | integer |
| teacher_id | integer |
| discipline_id | integer |
| group_id | integer |
| semester | integer |
| load_hours | decimal(5,2) |

## Изменить LoadAssignment по ID

### Параметры запроса
| Параметр | Тип | Обязательность | Ограничение | Пояснение |
|----------|-----|----------------|-------------|-----------|
| id | integer | Да | PK | ID изменяемой записи |
| teacher_id | integer | Нет | FK -> Teacher.id | ID преподавателя |
| discipline_id | integer | Нет | FK -> Discipline.id | ID дисциплины |
| group_id | integer | Нет | FK -> Group.id | ID группы |
| semester | integer | Нет | 1-8 | Номер семестра |
| load_hours | decimal(5,2) | Нет | >0 | Часы |

**Примечание:** хотя бы один из необязательных параметров должен быть указан.

### Возвращаемые данные при успешном изменении (HTTP 200)
| Параметр | Тип |
|----------|-----|
| id | integer |
| teacher_id | integer |
| discipline_id | integer |
| group_id | integer |
| semester | integer |
| load_hours | decimal(5,2) |

## Удалить LoadAssignment по ID

### Параметры запроса
| Параметр | Тип | Обязательность | Ограничение | Пояснение |
|----------|-----|----------------|-------------|-----------|
| id | integer | Да | PK | ID записи |

### Возвращаемые данные
Вернёт `True`, если LoadAssignment была удалена (логически), иначе вернёт `False`.

## Получить LoadAssignment по ID

### Параметры запроса
| Параметр | Тип | Обязательность | Ограничение | Пояснение |
|----------|-----|----------------|-------------|-----------|
| id | integer | Да | PK | ID записи |

### Возвращаемые данные при успехе (HTTP 200)
| Параметр | Тип |
|----------|-----|
| id | integer |
| teacher_id | integer |
| discipline_id | integer |
| group_id | integer |
| semester | integer |
| load_hours | decimal(5,2) |

## Получить список LoadAssignment

### Параметры запроса
| Параметр | Тип | Обязательность | Ограничение | Пояснение |
|----------|-----|----------------|-------------|-----------|
| teacher_id | integer | Нет | FK -> Teacher.id | Фильтр по преподавателю |
| discipline_id | integer | Нет | FK -> Discipline.id | Фильтр по дисциплине |
| group_id | integer | Нет | FK -> Group.id | Фильтр по группе |
| semester | integer | Нет | 1-8 | Фильтр по семестру |
| limit | integer | Нет | >0 | Лимит записей (по умолчанию 100) |
| offset | integer | Нет | >=0 | Сдвиг (по умолчанию 0) |

### Возвращаемые данные при успехе (HTTP 200) – массив
| Параметр | Тип |
|----------|-----|
| id | integer |
| teacher_id | integer |
| discipline_id | integer |
| group_id | integer |
| semester | integer |
| load_hours | decimal(5,2) |

## ER-диаграмма
![ER-диаграмма](erd.png)

**Ключевые связи:**
- `LoadAssignment.teacher_id` → `Teacher.id` (N:1)
- `LoadAssignment.discipline_id` → `Discipline.id` (N:1)
- `LoadAssignment.group_id` → `Group.id` (N:1)
