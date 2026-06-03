import datetime
from peewee import *

db = SqliteDatabase('employee_status.db')

# ---------- Валидаторы ----------
def validate_positive(value):
    if value <= 0:
        raise ValueError("user_id должен быть положительным целым числом")

def validate_hire_date(value):
    if value < datetime.date(1900, 1, 1):
        raise ValueError("Дата найма не может быть раньше 1900-01-01")

# ---------- Модели ----------
class BaseModel(Model):
    class Meta:
        database = db

class Employee(BaseModel):
    class Meta:
        db_table = "employees"

    id = AutoField()
    user_id = IntegerField(unique=True, null=False) 
    hire_date = DateField(null=False)
    # Замечание 5: Поле status объявлено как NOT NULL в БД (null=False)
    # Опциональность при частичном обновлении (update_employee) будет контролироваться на уровне API
    status = CharField(max_length=20, default='active', null=False) 
    is_active = BooleanField(default=True)
    updated_at = DateTimeField(default=datetime.datetime.now) 

    def save(self, *args, **kwargs):
        """Валидация полей перед сохранением"""
        validate_positive(self.user_id)
        validate_hire_date(self.hire_date)
        
        allowed_statuses = ['active', 'on_vacation', 'sick_leave', 'fired']
        # Замечание 1: Исправлена синтаксическая ошибка во f-строке (добавлен апостроф после f)
        if self.status not in allowed_statuses:
            raise ValueError(f"Статус должен быть одним из: {', '.join(allowed_statuses)}")
            
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    # Замечание 8: Добавлен метод мягкого удаления, возвращающий булево значение (True/False)
    def soft_delete(self):
        """Мягкое удаление сотрудника"""
        if self.is_active:
            self.is_active = False
            self.save()
            return True
        return False

    # Замечание 7: Метод комплексной фильтрации сотрудников по всем параметрам спецификации list_employees
    @classmethod
    def filter_employees(cls, user_id=None, status=None, position_id=None, hire_date_from=None, hire_date_to=None):
        query = cls.select()
        
        if position_id is not None:
            query = query.join(EmployeePosition).where(EmployeePosition.position == position_id)
            
        if user_id is not None:
            query = query.where(cls.user_id == user_id)
        if status is not None:
            query = query.where(cls.status == status)
        if hire_date_from is not None:
            query = query.where(cls.hire_date >= hire_date_from)
        if hire_date_to is not None:
            query = query.where(cls.hire_date <= hire_date_to)
            
        return query

class Position(BaseModel):
    class Meta:
        db_table = "positions"

    id = AutoField()
    title = CharField(max_length=100, null=False)
    # Замечание 2: Изменено на null=False для строгого соответствия ER-диаграмме (NOT NULL)
    description = TextField(null=False)

    def save(self, *args, **kwargs):
        if not self.title or not (1 <= len(str(self.title)) <= 100):
            raise ValueError("Длина названия должности должна быть от 1 до 100 символов")
        return super().save(*args, **kwargs)

class EmployeePosition(BaseModel):
    class Meta:
        db_table = "employee_positions"

    id = AutoField()
    employee = ForeignKeyField(Employee, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    position = ForeignKeyField(Position, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    # Замечание 3, 4: Изменено на null=False для соответствия ER-диаграмме (NOT NULL). 
    # Это гарантирует, что у каждой связи всегда заполнены даты и структура вернётся без пропусков (None).
    end_date = DateField(null=False)
    load_factor = FloatField(null=False)

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValueError("Дата окончания должности не может быть раньше даты начала")
        return super().save(*args, **kwargs)

class Vacation(BaseModel):
    class Meta:
        db_table = "vacations"

    id = AutoField()
    employee = ForeignKeyField(Employee, backref='vacations', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    type = CharField(max_length=50, null=False)

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValueError("Дата окончания отпуска не может быть раньше даты начала")
        return super().save(*args, **kwargs)

class SickLeave(BaseModel):
    class Meta:
        db_table = "sick_leaves"

    id = AutoField()
    employee = ForeignKeyField(Employee, backref='sick_leaves', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    # Замечание 6: Изменено на null=False для устранения противоречий с doc.md (NOT NULL)
    diagnosis = TextField(null=False)

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValueError("Дата окончания больничного не может быть раньше даты начала")
        return super().save(*args, **kwargs)

def init_db():
    db.connect()
    db.create_tables([Employee, Position, EmployeePosition, Vacation, SickLeave], safe=True)
    db.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized. Tables created successfully.")
