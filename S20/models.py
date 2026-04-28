import os
from peewee import *
from datetime import date

db = SqliteDatabase('academic_periods.db')

class BaseModel(Model):
    class Meta:
        database = db

class AcademicPeriod(BaseModel):
    name = CharField(max_length=100)  # исправлено: title -> name
    type = CharField(max_length=20)  # semester, module
    start_date = DateField()
    end_date = DateField()
    parent = IntegerField(default=0)  # 0 — корневой период, иначе ID родителя (семестра для модуля)

class Teacher(BaseModel):
    name = CharField(max_length=100)
    email = CharField(unique=True)

class PeriodTeacher(BaseModel):
    period = ForeignKeyField(AcademicPeriod, backref='teachers_link')
    teacher = ForeignKeyField(Teacher, backref='periods_link')

def init_db():
    db.connect()
    db.create_tables([AcademicPeriod, Teacher, PeriodTeacher], safe=True)
    db.close()

def get_db_init_handler():
    def handler():
        init_db()
        return {"message": "Database initialized"}
    return handler