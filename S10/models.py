import datetime
from peewee import *

db = SqliteDatabase('employee_status.db')

# ---------- Валидаторы (Оставлены только базовые ограничения типов) ----------
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
    # Замечание 5: unique=True оставлен, так как один user_id имеет строго одну статусную запись
    user_id = IntegerField(unique=True, null=False) 
    hire_date = DateField(null=False)
    status = CharField(max_length=20, default='active', null=False) 
    is_active = BooleanField(default=True)
    updated_at = DateTimeField(default=datetime.datetime.now) 

    def save(self, *args, **kwargs):
        """Валидация данных перед записью в БД"""
        validate_positive(self.user_id)
        validate_hire_date(self.hire_date)
        
        allowed_statuses = ['active', 'on_vacation', 'sick_leave', 'fired']
        if self.status not in allowed_statuses:
            raise ValueError(f"Статус должен быть одним из: {', '.join(allowed_statuses)}")
            
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    # Замечание 4: Добавлено явное свойство для гарантированного формирования структуры positions
    @property
    def positions(self):
        """Формирует сложную структуру должностей для get_employee API"""
        result = []
        # Замечание 3: Логика соединения таблиц через ForeignKeyField
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
    description = TextField(null=False)

class EmployeePosition(BaseModel):
    class Meta:
        db_table = "employee_positions"

    id = AutoField()
    employee = ForeignKeyField(Employee, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    position = ForeignKeyField(Position, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=True)
    load_factor = FloatField(null=False)

class Vacation(BaseModel):
    class Meta:
        db_table = "vacations"

    id = AutoField()
    employee = ForeignKeyField(Employee, backref='vacations', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    type = CharField(max_length=50, null=False)

class SickLeave(BaseModel):
    class Meta:
        db_table = "sick_leaves"

    id = AutoField()
    employee = ForeignKeyField(Employee, backref='sick_leaves', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    diagnosis = TextField(null=False)

def init_db():
    db.connect()
    # Восстановлены все таблицы согласно ERD и замечанию 7
    db.create_tables([Employee, Position, EmployeePosition, Vacation, SickLeave], safe=True)
    db.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized. All tables created successfully.")
