from peewee import Model, SqliteDatabase, IntegerField, CharField, DecimalField, ForeignKeyField, IntegrityError, SQL, BooleanField, AutoField
from peewee import DoesNotExist

db = SqliteDatabase('load_assignment.db')

class BaseModel(Model):
    class Meta:
        database = db

class Teacher(BaseModel):
    id = AutoField()
    full_name = CharField(max_length=200, unique=True, constraints=[SQL('NOT NULL')])
    position = CharField(max_length=100, constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'Teacher'

class Discipline(BaseModel):
    id = AutoField()
    name = CharField(max_length=200, unique=True, constraints=[SQL('NOT NULL')])
    hours_total = IntegerField(constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'Discipline'

class Group(BaseModel):
    id = AutoField()
    group_number = CharField(max_length=20, unique=True, constraints=[SQL('NOT NULL')])
    specialty_id = IntegerField(constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'Group'

class Student(BaseModel):
    id = AutoField()
    student_number = CharField(max_length=50, unique=True, null=True)
    current_group_id = ForeignKeyField(Group, backref="students", on_delete='CASCADE', null=True)
    status = CharField(max_length=50, constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'Student'

class LoadAssignment(BaseModel):
    id = AutoField()
    teacher_id = ForeignKeyField(Teacher, backref='assignments', on_delete='CASCADE', null=False)
    discipline_id = ForeignKeyField(Discipline, backref='assignments', on_delete='CASCADE', null=False)
    group_id = ForeignKeyField(Group, backref='assignments', on_delete='CASCADE', null=False)
    semester = IntegerField(constraints=[SQL('CHECK (semester BETWEEN 1 AND 8)'), SQL('NOT NULL')])
    load_hours = DecimalField(max_digits=5, decimal_places=2, constraints=[SQL('CHECK (load_hours > 0)'), SQL('NOT NULL')])
    is_active = BooleanField(default=True)  # СИНХРОНИЗИРОВАНО: строго is_active по ТЗ

    class Meta:
        table_name = 'LoadAssignment'
        indexes = (
            (('teacher_id', 'discipline_id', 'group_id', 'semester'), True),
        )

def create_tables():
    db.connect()
    db.create_tables([Teacher, Discipline, Group, Student, LoadAssignment], safe=True)
    db.close()

def validate_semester(semester):
    return 1 <= semester <= 8

def validate_load_hours(hours):
    return hours > 0

def add_load_assignment(teacher_id, discipline_id, group_id, semester, load_hours):
    if not validate_semester(semester):
        return ({"error": "validation error", "message": "semester должен быть от 1 до 8"}, 422)
    if not validate_load_hours(load_hours):
        return ({"error": "validation error", "message": "load_hours должно быть > 0"}, 422)
    
    try:
        Teacher.get_by_id(teacher_id)
        Discipline.get_by_id(discipline_id)
        Group.get_by_id(group_id)
    except DoesNotExist:
        return ({"error": "not found", "message": "Неверный teacher_id, discipline_id или group_id"}, 404)

    try:
        assignment = LoadAssignment.create(
            teacher_id=teacher_id,
            discipline_id=discipline_id,
            group_id=group_id,
            semester=semester,
            load_hours=load_hours,
            is_active=True
        )
        data = {
            "id": assignment.id,
            "teacher_id": assignment.teacher_id_id,
            "discipline_id": assignment.discipline_id_id,
            "group_id": assignment.group_id_id,
            "semester": assignment.semester,
            "load_hours": float(assignment.load_hours),
            "is_active": assignment.is_active
        }
        return (data, 201)
    except IntegrityError as e:
        if e.args and 'unique' in str(e).lower():
            return ({"error": "duplicate entry", "message": "Такая нагрузка уже существует"}, 409)
        return ({"error": "database error", "message": "Ошибка нарушения целостности данных"}, 400)
    except ValueError as e:
        return ({"error": "invalid parameter", "message": f"Ошибка типа параметра: {e}"}, 400)

def update_load_assignment(id, teacher_id=None, discipline_id=None, group_id=None, semester=None, load_hours=None):
    if teacher_id is None and discipline_id is None and group_id is None and semester is None and load_hours is None:
        return ({"error": "invalid parameter", "message": "Необходимо указать хотя бы одно поле для обновления"}, 400)
    try:
        assignment = LoadAssignment.get(LoadAssignment.id == id, LoadAssignment.is_active == True)
    except DoesNotExist:
        return ({"error": "not found", "message": "Запись не найдена"}, 404)

    if semester is not None and not validate_semester(semester):
        return ({"error": "validation error", "message": "semester должен быть от 1 до 8"}, 422)
    if load_hours is not None and not validate_load_hours(load_hours):
        return ({"error": "validation error", "message": "load_hours должно быть > 0"}, 422)

    try:
        if teacher_id is not None: Teacher.get_by_id(teacher_id)
        if discipline_id is not None: Discipline.get_by_id(discipline_id)
        if group_id is not None: Group.get_by_id(group_id)
    except DoesNotExist:
        return ({"error": "not found", "message": "Указанный связанный объект не существует"}, 404)

    new_teacher = teacher_id if teacher_id is not None else assignment.teacher_id_id
    new_discipline = discipline_id if discipline_id is not None else assignment.discipline_id_id
    new_group = group_id if group_id is not None else assignment.group_id_id
    new_semester = semester if semester is not None else assignment.semester

    duplicate = LoadAssignment.select().where(
        (LoadAssignment.teacher_id == new_teacher) &
        (LoadAssignment.discipline_id == new_discipline) &
        (LoadAssignment.group_id == new_group) &
        (LoadAssignment.semester == new_semester) &
        (LoadAssignment.id != id) &
        (LoadAssignment.is_active == True)
    ).exists()
    if duplicate:
        return ({"error": "duplicate entry", "message": "Такая нагрузка уже существует"}, 409)

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
    
    data = {
        "id": assignment.id,
        "teacher_id": assignment.teacher_id_id,
        "discipline_id": assignment.discipline_id_id,
        "group_id": assignment.group_id_id,
        "semester": assignment.semester,
        "load_hours": float(assignment.load_hours),
        "is_active": assignment.is_active
    }
    return (data, 200)

def delete_load_assignment(id):
    try:
        assignment = LoadAssignment.get(LoadAssignment.id == id, LoadAssignment.is_active == True)
        assignment.is_active = False  # Мягкое удаление: переключаем в False
        assignment.save()
        return ({"result": True}, 200)
    except DoesNotExist:
        return ({"error": "not found", "message": "Запись не найдена"}, 404)

def get_load_assignment(id):
    try:
        assignment = LoadAssignment.get(LoadAssignment.id == id, LoadAssignment.is_active == True)
        data = {
            "id": assignment.id,
            "teacher_id": assignment.teacher_id_id,
            "discipline_id": assignment.discipline_id_id,
            "group_id": assignment.group_id_id,
            "semester": assignment.semester,
            "load_hours": float(assignment.load_hours),
            "is_active": assignment.is_active
        }
        return (data, 200)
    except DoesNotExist:
        return ({"error": "not found", "message": "Запись не найдена"}, 404)

def get_load_assignments(teacher_id=None, discipline_id=None, group_id=None, semester=None, limit=100, offset=0):
    if limit <= 0:
        return ({"error": "invalid parameter", "message": "limit должен быть больше 0"}, 400)
    if offset < 0:
        return ({"error": "invalid parameter", "message": "offset не может быть отрицательным"}, 400)
    
    query = LoadAssignment.select().where(LoadAssignment.is_active == True)
    if teacher_id is not None:
        query = query.where(LoadAssignment.teacher_id == teacher_id)
    if discipline_id is not None:
        query = query.where(LoadAssignment.discipline_id == discipline_id)
    if group_id is not None:
        query = query.where(LoadAssignment.group_id == group_id)
    if semester is not None:
        query = query.where(LoadAssignment.semester == semester)
        
    query = query.offset(offset).limit(limit)
    
    data = [
        {
            "id": a.id,
            "teacher_id": a.teacher_id_id,
            "discipline_id": a.discipline_id_id,
            "group_id": a.group_id_id,
            "semester": a.semester,
            "load_hours": float(a.load_hours),
            "is_active": a.is_active
        } for a in query
    ]
    return (data, 200)

if __name__ == '__main__':
    create_tables()
