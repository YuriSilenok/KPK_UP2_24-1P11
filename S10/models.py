from peewee import *

db = SqliteDatabase("employee_status.db")

class BaseModel(Model):
    class Meta:
        database = db

class Position(BaseModel):
    name = CharField(unique=True)

class EmployeeStatus(BaseModel):
    employee_id = IntegerField()
    position = ForeignKeyField(Position, backref="employee_statuses")
    rate = FloatField()
    is_part_time = BooleanField(default=False)
    start_date = DateField()
    end_date = DateField(null=True)
    is_active = BooleanField(default=True)

class Vacation(BaseModel):
    employee_id = IntegerField()
    start_date = DateField()
    end_date = DateField()
    vacation_type = CharField()

class SickLeave(BaseModel):
    employee_id = IntegerField()
    start_date = DateField()
    end_date = DateField()
    document_number = CharField()

def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([
        Position,
        EmployeeStatus,
        Vacation,
        SickLeave
    ])



