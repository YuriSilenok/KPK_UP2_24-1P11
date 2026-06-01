from peewee import *
import sqlite3

db = SqliteDatabase('load_assignment.db')

class BaseModel(Model):
    class Meta:
        database = db

class Teacher(BaseModel):
    id = IntegerField(primary_key=True)
    full_name = CharField(max_length=200, unique=True, constraints=[SQL('NOT NULL')])
    position = CharField(max_length=100, constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'Teacher'

class Discipline(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=200, unique=True, constraints=[SQL('NOT NULL')])
    hours_total = IntegerField(constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'Discipline'

class Group(BaseModel):
    id = IntegerField(primary_key=True)
    group_number = CharField(max_length=20, unique=True, constraints=[SQL('NOT NULL')])
    specialty_id = IntegerField(constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'Group'

class Student(BaseModel):
    id = IntegerField(primary_key=True)
    student_number = CharField(unique=True, null=True)
    current_group_id = ForeignKeyField(Group, backref='students', on_delete='CASCADE', null=True)
    status = CharField(constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'Student'

class LoadAssignment(BaseModel):
    id = IntegerField(primary_key=True)
    teacher_id = ForeignKeyField(Teacher, backref='assignments', on_delete='CASCADE')
    discipline_id = ForeignKeyField(Discipline, backref='assignments', on_delete='CASCADE')
    group_id = ForeignKeyField(Group, backref='assignments', on_delete='CASCADE')
    semester = IntegerField(constraints=[SQL('CHECK (semester BETWEEN 1 AND 8)')])
    load_hours = DecimalField(max_digits=5, decimal_places=2, constraints=[SQL('CHECK (load_hours > 0)')])

    class Meta:
        table_name = 'LoadAssignment'
        indexes = (
            (('teacher_id', 'discipline_id', 'group_id', 'semester'), True),
        )


def create_tables():
    db.connect()
    db.create_tables([Teacher, Discipline, Group, Student, LoadAssignment], safe=True)
    db.close()


if __name__ == '__main__':
    create_tables()

