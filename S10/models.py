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
    # Логическая связь со сторонним микросервисом Profile Service.
    user_id = IntegerField(unique=True, null=False) 
    # Замечание 1 и 2: Ошибочное поле get_by_id полностью удалено.
    # Замечание 6: Убрано null=False для полноценной опциональности в методе update_employee.
    hire_date = DateField()
    status = CharField(max_length=20, default='active') 
    is_active = BooleanField(default=True)
    updated_at = DateTimeField(default=datetime.datetime.now) 

    def save(self, *args, **kwargs):
        """Валидация данных перед записью в БД"""
        if self.user_id <= 0:
            raise ValueError("user_id должен быть положительным целым числом")
        if self.hire_date and self.hire_date < datetime.date(1900, 1, 1):
            raise ValueError("Дата найма не может быть раньше 1900-01-01")
        
        allowed_statuses = ['active', 'on_vacation', 'sick_leave', 'fired']
        if self.status not in allowed_statuses:
            raise ValueError(f"Статус должен быть одним из: {', '.join(allowed_statuses)}")
            
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    @property
    def positions(self):
        """Свойство (property) уровня приложения для динамической агрегации должностей"""
        result = []
        query = (EmployeePosition
                 .select(EmployeePosition, Position)
                 .join(Position)
                 .where(EmployeePosition.employee == self))
        for ep in query:
            result.append({
                "position_title": ep.position.title,
                "start_date": ep.start_date.isoformat(),
                "end_date": ep.end_date.isoformat() if ep.end_date else None,
                "load_factor": ep.load_factor
            })
        return result

class Position(BaseModel):
    class Meta:
        db_table = "positions"

    id = AutoField()
    title = CharField(max_length=100, null=False)
    description = TextField(null=True)

class EmployeePosition(BaseModel):
    class Meta:
        db_table = "employee_positions"

    id = AutoField()
    employee = ForeignKeyField(Employee, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    position = ForeignKeyField(Position, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=True)
    load_factor = FloatField(null=False)

    def save(self, *args, **kwargs):
        if self.end_date is not None and self.end_date < self.start_date:
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
    diagnosis = TextField(null=True)

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
    print("Database initialized successfully.")
