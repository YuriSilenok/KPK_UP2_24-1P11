```python
from peewee import *

db = SqliteDatabase("employee_status.db")

class BaseModel(Model):
    class Meta:
        database = db

class Position(BaseModel):
    name = CharField(unique=True)

class EmployeeStatus(BaseModel):
    employee_id = IntegerField()
    position = ForeignKeyField(
        Position,
        backref="statuses",
        on_delete="RESTRICT"
    )

    rate = FloatField(default=1.0)
    is_part_time = BooleanField(default=False)

    start_date = DateField()
    end_date = DateField(null=True)

class Vacation(BaseModel):
    employee_status = ForeignKeyField(
        EmployeeStatus,
        backref="vacations",
        on_delete="CASCADE"
    )

    start_date = DateField()
    end_date = DateField()

    vacation_type = CharField()

class SickLeave(BaseModel):
    employee_status = ForeignKeyField(
        EmployeeStatus,
        backref="sick_leaves",
        on_delete="CASCADE"
    )

    start_date = DateField()
    end_date = DateField()

    document_number = CharField()

def initialize_database():
    db.connect()
    db.create_tables([
        Position,
        EmployeeStatus,
        Vacation,
        SickLeave
    ])
    db.close()

if __name__ == "__main__":
    initialize_database()
