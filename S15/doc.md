# 15. Load Assignment Service (Сервис распределения нагрузки):
 # LoadAssignment
| Поле | Тип | Ограничения |
|---|---|---|
|id | Integer | PK|
|teacher_id | Integer | FK -> Teacher.id|
|discipline_id | Integer | FK -> Discipline.id|
|group_id | Integer | FK -> Group.id|
|semester | Integer | 1-8|
|load_hours | Decimal(5,2) | >0 |

  
 # Teacher
| Поле | Тип | Ограничения |
|---|---|---|
|id | Integer | PK|
|full_name | Varchar(200) | NOT NULL, UNIQUE|
|position | Varchar(100) | NOT NULL|


# Discipline
| Поле | Тип | Ограничения |
|---|---|---|
|id | Integer | PK|
|name | Varchar(200) | NOT NULL, UNIQUE|
|hours_total | Integer | NOT NULL |


# Group
| Поле | Тип | Ограничения |
|---|---|---|
|id | Integer | PK|
|group_number | Varchar(20) | NOT NULL, UNIQUE|
|specialty_id | Integer | NOT NULL|

 # Student
| Поле | Тип | Ограничения |
|---|---|---|
| id | Integer | PK |
| student_number | Varchar | UNIQUE |
| current_group_id | Integer | FK -> Group.id |
| status | Varchar | NOT NULL |

## Добавить LoadAssignment
| Параметр | Обязательность | Тип | Ограничение |
|----------|----------------|-----|-------------|
| teacher_id | Да | int | FK -> Teacher.id |
| discipline_id | Да | int | FK -> Discipline.id |
| group_id | Да | int | FK -> Group.id |
| semester | Да | int | 1-8 |
| load_hours | Да | decimal | >0 |

**Уникальная комбинация:** (teacher_id, discipline_id, group_id, semester)

**Возвращаемые данные:**
| Поле | Тип |
|------|-----|
| id | int |
| teacher_id | int |
| discipline_id | int |
| group_id | int |
| semester | int |
| load_hours | decimal |

## Изменить LoadAssignment по ID
| Параметр | Обязательность | Тип | Ограничение |
|----------|----------------|-----|-------------|
| id | Да | int | PK |
| teacher_id | Нет | int | FK -> Teacher.id |
| discipline_id | Нет | int | FK -> Discipline.id |
| group_id | Нет | int | FK -> Group.id |
| semester | Нет | int | 1-8 |
| load_hours | Нет | decimal | >0 |

**Возвращаемые данные:**
| Поле | Тип |
|------|-----|
| id | int |
| teacher_id | int |
| discipline_id | int |
| group_id | int |
| semester | int |
| load_hours | decimal |

## Удалить LoadAssignment по ID
| Параметр | Обязательность | Тип | Ограничение |
|----------|----------------|-----|-------------|
| id | Да | int | PK |

**Возвращаемые данные:**
| Поле | Тип |
|------|-----|
| success | bool |
| message | string |

## Получить LoadAssignment по ID
| Параметр | Обязательность | Тип | Ограничение |
|----------|----------------|-----|-------------|
| id | Да | int | PK |

**Возвращаемые данные:**
| Поле | Тип |
|------|-----|
| id | int |
| teacher_id | int |
| discipline_id | int |
| group_id | int |
| semester | int |
| load_hours | decimal |

## Получить список LoadAssignment по заданным параметрам
| Параметр | Обязательность | Тип | Ограничение |
|----------|----------------|-----|-------------|
| teacher_id | Нет | int | FK -> Teacher.id |
| discipline_id | Нет | int | FK -> Discipline.id |
| group_id | Нет | int | FK -> Group.id |
| semester | Нет | int | 1-8 |
| load_hours_min | Нет | decimal | >0 |
| load_hours_max | Нет | decimal | >0 |
| limit | Нет | int | >0 |
| offset | Нет | int | >=0 |

**Возвращаемые данные:** массив LoadAssignment

### ER-диаграмма
![ER-диаграмма](erd.png)
```
