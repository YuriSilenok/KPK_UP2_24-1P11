import os
from peewee import *
from datetime import date

db = SqliteDatabase('academic_periods.db')

class BaseModel(Model):
    class Meta:
        database = db

class AcademicPeriod(BaseModel):
    name = CharField(max_length=100)
    academic_year = CharField(max_length=9, null=False)  # Формат 2025-2026, необязательный
    type = CharField(max_length=20)  # semester, module
    start_date = DateField()
    end_date = DateField()
    parent_period_id = IntegerField(default=0)  # 0 — корневой период, иначе ID родителя (семестра для модуля)

    class Meta:
        indexes = (
            (('name', 'academic_year'), True),  # уникальная комбинация
        )

def init_db():
    db.connect()
    db.create_tables([AcademicPeriod], safe=True)
    db.close()

def get_db_init_handler():
    def handler():
        init_db()
        return {"message": "Database initialized"}
    return handler