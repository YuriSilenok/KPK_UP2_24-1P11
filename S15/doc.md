# 15. Load Assignment Service (Сервис распределения нагрузки)

## LoadAssignment
| Поле | Тип | Обязательность | Ограничение | Пояснение |
|------|-----|----------------|-------------|-----------|
| id | Integer | Да | PK | Идентификатор |
| teacher_id | Integer | Да | FK -> Teacher.id | ID преподавателя |
| discipline_id | Integer | Да | FK -> Discipline.id | ID дисциплины |
| group_id | Integer | Да | FK -> Group.id | ID группы |
| semester | Integer | Да | CHECK (1-8) | Номер семестра |
| load_hours | Decimal(5,2) | Да | CHECK (>0) | Часы |

## Teacher
| Поле | Тип | Обязательность | Ограничение | Пояснение |
|------|-----|----------------|-------------|-----------|
| id | Integer | Да | PK | Идентификатор |
| full_name | Varchar(200) | Да | NOT NULL, UNIQUE | ФИО |
| position | Varchar(100) | Да | NOT NULL | Должность |

## Discipline
| Поле | Тип | Обязательность | Ограничение | Пояснение |
|------|-----|----------------|-------------|-----------|
| id | Integer | Да | PK | Идентификатор |
| name | Varchar(200) | Да | NOT NULL, UNIQUE | Название |
| hours_total | Integer | Да | NOT NULL | Часы |

## Group
| Поле | Тип | Обязательность | Ограничение | Пояснение |
|------|-----|----------------|-------------|-----------|
| id | Integer | Да | PK | Идентификатор |
| group_number | Varchar(20) | Да | NOT NULL, UNIQUE | Номер |
| specialty_id | Integer | Да | NOT NULL | Специальность |

## Student
| Поле | Тип | Обязательность | Ограничение | Пояснение |
|------|-----|----------------|-------------|-----------|
| id | Integer | Да | PK | Идентификатор |
| student_number | Varchar(50) | Нет | UNIQUE | Номер студента |
| current_group_id | Integer | Нет | FK -> Group.id | ID группы |
| status | Varchar(50) | Да | NOT NULL | Статус |

## Добавить LoadAssignment

### Параметры запроса
| Параметр | Тип | Обязательность | Ограничение | Пояснение |
|----------|-----|----------------|-------------|-----------|
| teacher_id | int | Да | FK -> Teacher.id | ID преподавателя |
| discipline_id | int | Да | FK -> Discipline.id | ID дисциплины |
| group_id | int | Да | FK -> Group.id | ID группы |
| semester | int | Да | 1-8 | Номер семестра |
| load_hours | Decimal(5,2) | Да | >0 | Часы |

### Уникальные комбинации параметров
- (teacher_id, discipline_id, group_id, semester)

### Возвращаемые данные при успешном создании
| Параметр | Тип |
|----------|-----|
| id | int |
| teacher_id | int |
| discipline_id | int |
| group_id | int |
| semester | int |
| load_hours | Decimal(5,2) |

### При ошибке
| Параметр | Тип | Пояснение |
|----------|-----|-----------|
| error | string | Тип ошибки |
| message | string | Описание ошибки |

## Изменить LoadAssignment по ID

### Параметры запроса
| Параметр | Тип | Обязательность | Ограничение | Пояснение |
|----------|-----|----------------|-------------|-----------|
| id | int | Да | PK | ID изменяемой записи |
| teacher_id | int | Нет | FK -> Teacher.id | ID преподавателя |
| discipline_id | int | Нет | FK -> Discipline.id | ID дисциплины |
| group_id | int | Нет | FK -> Group.id | ID группы |
| semester | int | Нет | 1-8 | Номер семестра |
| load_hours | Decimal(5,2) | Нет | >0 | Часы |

### Возвращаемые данные при успешном изменении
| Параметр | Тип |
|----------|-----|
| id | int |
| teacher_id | int |
| discipline_id | int |
| group_id | int |
| semester | int |
| load_hours | Decimal(5,2) |

### При ошибке
| Параметр | Тип | Пояснение |
|----------|-----|-----------|
| error | string | Тип ошибки |
| message | string | Описание ошибки |

## Удалить LoadAssignment по ID

### Параметры запроса
| Параметр | Тип | Обязательность | Ограничение | Пояснение |
|----------|-----|----------------|-------------|-----------|
| id | int | Да | PK | ID записи |

### Возвращаемые данные
True — при успехе, False — при ошибке

## Получить LoadAssignment по ID

### Параметры запроса
| Параметр | Тип | Обязательность | Ограничение | Пояснение |
|----------|-----|----------------|-------------|-----------|
| id | int | Да | PK | ID записи |

### Возвращаемые данные
| Параметр | Тип |
|----------|-----|
| id | int |
| teacher_id | int |
| discipline_id | int |
| group_id | int |
| semester | int |
| load_hours | Decimal(5,2) |

### При ошибке
| Параметр | Тип | Пояснение |
|----------|-----|-----------|
| error | string | Тип ошибки |
| message | string | Описание ошибки |

## Получить список LoadAssignment

### Параметры запроса
| Параметр | Тип | Обязательность | Ограничение | Пояснение |
|----------|-----|----------------|-------------|-----------|
| teacher_id | int | Нет | FK -> Teacher.id | Фильтр по преподавателю |
| discipline_id | int | Нет | FK -> Discipline.id | Фильтр по дисциплине |
| group_id | int | Нет | FK -> Group.id | Фильтр по группе |
| semester | int | Нет | 1-8 | Фильтр по семестру |
| limit | int | Нет | >0 | Лимит записей (по умолчанию 100) |
| offset | int | Нет | >=0 | Сдвиг (по умолчанию 0) |

### Возвращаемые данные (массив)
| Параметр | Тип |
|----------|-----|
| id | int |
| teacher_id | int |
| discipline_id | int |
| group_id | int |
| semester | int |
| load_hours | Decimal(5,2) |

### При ошибке
| Параметр | Тип | Пояснение |
|----------|-----|-----------|
| error | string | Тип ошибки |
| message | string | Описание ошибки |

## Уникальные комбинации параметров для других сущностей
- Teacher: full_name
- Discipline: name
- Group: group_number
- Student: student_number

### ER-диаграмма
![ER-диаграмма](erd.png)
