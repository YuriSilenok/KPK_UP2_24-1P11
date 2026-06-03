import datetime
from peewee import *

db = SqliteDatabase('employee_status.db')

class BaseModel(Model):
    class Meta:
        database = db

class Employee(BaseModel):
    class Meta:
        db_table = "employees"

    id = AutoField()
    # Замечание 6 (doc.md): Ограничение уникальности (unique=True) отражено явно
    user_id = IntegerField(unique=True, null=False) 
    # Замечание 10: Убрано null=False для совместимости с опциональным обновлением в API
    hire_date = DateField()
    status = CharField(max_length=20) 
    # Замечание 6, 7 (doc.md): Поле переименовано в is_active согласно стандартам
    is_active = BooleanField(default=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

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
    # Замечание 5: Каскадное удаление (on_delete='CASCADE') оставлено для соответствия документации
    employee = ForeignKeyField(Employee, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    position = ForeignKeyField(Position, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
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
    db.create_tables([Employee, Position, EmployeePosition, Vacation, SickLeave], safe=True)
    db.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized. Tables created successfully.")
