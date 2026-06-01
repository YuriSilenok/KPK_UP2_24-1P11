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
    student_number = CharField(max_length=50, unique=True, null=True)
    current_group_id = ForeignKeyField(Group, backref='students', on_delete='CASCADE', null=True)
    status = CharField(max_length=50, constraints=[SQL('NOT NULL')])

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

# API методы для LoadAssignment

def add_load_assignment(teacher_id, discipline_id, group_id, semester, load_hours):
    try:
        assignment = LoadAssignment.create(
            teacher_id=teacher_id,
            discipline_id=discipline_id,
            group_id=group_id,
            semester=semester,
            load_hours=load_hours
        )
        return {"id": assignment.id, "teacher_id": assignment.teacher_id.id, "discipline_id": assignment.discipline_id.id, "group_id": assignment.group_id.id, "semester": assignment.semester, "load_hours": assignment.load_hours}
    except IntegrityError:
        return {"error": "duplicate entry", "message": "Такая нагрузка уже существует"}

def update_load_assignment(id, teacher_id=None, discipline_id=None, group_id=None, semester=None, load_hours=None):
    try:
        assignment = LoadAssignment.get_by_id(id)
        if teacher_id is not None:
            assignment.teacher_id = teacher_id
        if discipline_id is not None:
            assignment.discipline_id = discipline_id
        if group_id is not None:
            assignment.group_id = group_id
        if semester is not None:
            assignment.semester = semester
        if load_hours is not None:
            assignment.load_hours = load_hours
        assignment.save()
        return {"id": assignment.id, "teacher_id": assignment.teacher_id.id, "discipline_id": assignment.discipline_id.id, "group_id": assignment.group_id.id, "semester": assignment.semester, "load_hours": assignment.load_hours}
    except DoesNotExist:
        return {"error": "not found", "message": "Запись не найдена"}

def delete_load_assignment(id):
    try:
        assignment = LoadAssignment.get_by_id(id)
        assignment.delete_instance()
        return {"success": True}
    except DoesNotExist:
        return {"error": "not found", "message": "Запись не найдена"}

def get_load_assignment(id):
    try:
        assignment = LoadAssignment.get_by_id(id)
        return {"id": assignment.id, "teacher_id": assignment.teacher_id.id, "discipline_id": assignment.discipline_id.id, "group_id": assignment.group_id.id, "semester": assignment.semester, "load_hours": assignment.load_hours}
    except DoesNotExist:
        return {"error": "not found", "message": "Запись не найдена"}

def get_load_assignments(teacher_id=None, discipline_id=None, group_id=None, semester=None, limit=None, offset=None):
    query = LoadAssignment.select()
    if teacher_id is not None:
        query = query.where(LoadAssignment.teacher_id == teacher_id)
    if discipline_id is not None:
        query = query.where(LoadAssignment.discipline_id == discipline_id)
    if group_id is not None:
        query = query.where(LoadAssignment.group_id == group_id)
    if semester is not None:
        query = query.where(LoadAssignment.semester == semester)
    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)
    return [{"id": a.id, "teacher_id": a.teacher_id.id, "discipline_id": a.discipline_id.id, "group_id": a.group_id.id, "semester": a.semester, "load_hours": a.load_hours} for a in query]

if __name__ == '__main__':
    create_tables()
