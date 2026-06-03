from peewee import *

db = SqliteDatabase("employee_status.db")

class BaseModel(Model):
    class Meta:
        database = db

class Position(BaseModel):
    id = AutoField()
    name = CharField(unique=True)
    is_active = BooleanField(default=True)

class EmployeeStatus(BaseModel):
    id = AutoField()
    employee_id = IntegerField()
    position = ForeignKeyField(Position, backref="employee_statuses")
    rate = FloatField()
    is_part_time = BooleanField(default=False)
    start_date = DateField()
    end_date = DateField(null=True)
    is_active = BooleanField(default=True)

class Vacation(BaseModel):
    id = AutoField()
    employee_id = IntegerField()
    start_date = DateField()
    end_date = DateField()
    vacation_type = CharField()
    is_active = BooleanField(default=True)

class SickLeave(BaseModel):
    id = AutoField()
    employee_id = IntegerField()
    start_date = DateField()
    end_date = DateField()
    document_number = CharField()
    is_active = BooleanField(default=True)

def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([
        Position,
        EmployeeStatus,
        Vacation,
        SickLeave
    ])

if __name__ == "__main__":
    init_db()
