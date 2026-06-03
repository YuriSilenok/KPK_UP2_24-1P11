import datetime
from peewee import *

db = SqliteDatabase('employee_status.db')

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
    status = CharField(max_length=20, default='active', null=False) 
    is_active = BooleanField(default=True)
    # Описано в спецификации doc.md (Проверка models.py, пункт 4)
    updated_at = DateTimeField(default=datetime.datetime.now) 

    def save(self, *args, **kwargs):
        if self.user_id <= 0:
            raise ValueError("user_id должен быть положительным целым числом")
        if self.hire_date < datetime.date(1900, 1, 1):
            raise ValueError("Дата найма не может быть раньше 1900-01-01")
        
        allowed_statuses = ['active', 'on_vacation', 'sick_leave', 'fired']
        if self.status not in allowed_statuses:
            raise ValueError(f"Статус должен быть одним из: {', '.join(allowed_statuses)}")
            
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def filter_employees(cls, user_id=None, status=None, position_id=None, hire_date_from=None, hire_date_to=None):
        """Обеспечивает комплексную фильтрацию по ТЗ (Проверка models.py, пункт 3)"""
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
    name = CharField(max_length=100, unique=True, null=False)
    description = TextField(null=True)
    is_active = BooleanField(default=True)

class EmployeePosition(BaseModel):
    class Meta:
        db_table = "employee_positions"

    id = AutoField()
    employee = ForeignKeyField(Employee, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    position = ForeignKeyField(Position, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=True)
    load_factor = FloatField(null=False)
    is_active = BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("Дата окончания должности не может быть раньше даты начала")
        return super().save(*args, **kwargs)

class Vacation(BaseModel):
    class Meta:
        db_table = "vacations"

    id = AutoField()
    # Переведено в ForeignKeyField согласно логике ТЗ (Пункт 1)
    employee = ForeignKeyField(Employee, backref='vacations', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    vacation_type = CharField(max_length=255, null=False)
    is_active = BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValueError("Дата окончания отпуска не может быть раньше даты начала")
        if len(str(self.vacation_type)) > 255:
            raise ValueError("Длина типа отпуска не должна превышать 255 символов")
        return super().save(*args, **kwargs)

class SickLeave(BaseModel):
    class Meta:
        db_table = "sick_leaves"

    id = AutoField()
    # Переведено в ForeignKeyField согласно логике ТЗ (Пункт 2)
    employee = ForeignKeyField(Employee, backref='sick_leaves', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    # Описано в спецификации doc.md (Пункт 5)
    document_number = CharField(max_length=255, null=False)
    is_active = BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValueError("Дата окончания больничного не может быть раньше даты начала")
        if len(str(self.document_number)) > 255:
            raise ValueError("Длина номера документа не должна превышать 255 символов")
        return super().save(*args, **kwargs)

def init_db():
    db.connect()
    db.create_tables([Employee, Position, EmployeePosition, Vacation, SickLeave], safe=True)
    db.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
