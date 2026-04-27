from peewee import *
import sqlite3

db = SqliteDatabase('load_assignment.db')

class BaseModel(Model):
    class Meta:
        database = db

class Teacher(BaseModel):
    id = AutoField()
    full_name = CharField(max_length=200, unique=True, constraints=[SQL('NOT NULL')])
    position = CharField(max_length=100, constraints=[SQL('NOT NULL')])

class Discipline(BaseModel):
    id = AutoField()
    name = CharField(max_length=200, unique=True, constraints=[SQL('NOT NULL')])
    hours_total = IntegerField(constraints=[SQL('NOT NULL')])

class Group(BaseModel):
    id = AutoField()
    group_number = CharField(max_length=20, unique=True, constraints=[SQL('NOT NULL')])
    specialty_id = IntegerField(constraints=[SQL('NOT NULL')])  # внешний ключ справочника

class LoadAssignment(BaseModel):
    id = AutoField()
    teacher = ForeignKeyField(Teacher, backref='assignments', on_delete='CASCADE')
    discipline = ForeignKeyField(Discipline, backref='assignments', on_delete='CASCADE')
    group = ForeignKeyField(Group, backref='assignments', on_delete='CASCADE')
    semester = IntegerField(constraints=[SQL('NOT NULL')])
    load_hours = DecimalField(max_digits=5, decimal_places=2, constraints=[SQL('NOT NULL')])

    class Meta:
        indexes = (
            (('teacher', 'discipline', 'group', 'semester'), True),  # уникальная комбинация
        )