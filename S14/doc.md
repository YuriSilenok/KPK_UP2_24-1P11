# Load Calculation Service (Сервис расчета нагрузки)

**Вариант 14**

## Сущность: CalculatedLoad

| Поле | Тип | Ограничение |
|------|-----|-------------|
| id | int | PRIMARY KEY |
| teacher_id | int | NOT NULL, >0 |
| period_id | int | NOT NULL, >0 |
| total_hours | float | NOT NULL, ≥0 |
| is_active | bool | DEFAULT true |

**Уникальная комбинация:** teacher_id + period_id

## ER-диаграмма

![ER-диаграмма](erd.png)