# 15. Load Assignment Service (Сервис распределения нагрузки): 
Сервис предназначен для учета проживания студентов в общежитии:
- заселение
- выселение
- комнаты
- общежития
- заявки на поселение#
- # Students

| Поле | Тип | Ограничения |
|---|---|---|
| id | Integer | PK |
| full_name | Varchar | NOT NULL |
| student_number | Varchar | UNIQUE |
| current_group_id | Integer | FK |
| status | Varchar | NOT NULL |

## Dormitories

| Поле | Тип | Ограничения |
|---|---|---|
| id | Integer | PK |
| name | Varchar | UNIQUE |
| address | Varchar | NOT NULL |
| floors | Integer | NOT NULL |
## Rooms

| Поле | Тип | Ограничения |
|---|---|---|
| id | Integer | PK |
| room_number | Varchar | NOT NULL |
| capacity | Integer | NOT NULL |
| occupied_places | Integer | DEFAULT 0 |
| dormitory_id | Integer | FK |
## Settlements

| Поле | Тип | Ограничения |
|---|---|---|
| id | Integer | PK |
| student_id | Integer | FK |
| room_id | Integer | FK |
| check_in_date | Date | NOT NULL |
| check_out_date | Date | NULL |
| status | Varchar | NOT NULL |
## Связи

Один студент может иметь много заявок

Students -> Applications

Один студент может иметь историю заселений

Students -> Settlements

В одной комнате живут несколько студентов

Rooms -> Settlements

Один корпус имеет много комнат

Dormitories -> Rooms


### ER-диаграмма
![Диаграмма](erd.png)