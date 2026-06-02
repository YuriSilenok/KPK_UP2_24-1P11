from peewee import Model, SqliteDatabase, IntegerField, CharField, DecimalField, ForeignKeyField, IntegrityError, SQL, BooleanField, AutoField
from peewee import DoesNotExist, OperationalError

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
    semester = IntegerField(constraints=[SQL('CHECK (semester BETWEEN 1 AND 8)')])
    load_hours = DecimalField(max_digits=5, decimal_places=2, constraints=[SQL('CHECK (load_hours > 0)')])
    is_active = BooleanField(default=True)

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

def validate_positive_id(value):
    return value is not None and value > 0

def add_load_assignment(teacher_id, discipline_id, group_id, semester, load_hours):
    if not validate_positive_id(teacher_id):
        return ({"error": "Неверный параметр", "message": "teacher_id должен быть положительным числом"}, 400)
    if not validate_positive_id(discipline_id):
        return ({"error": "Неверный параметр", "message": "discipline_id должен быть положительным числом"}, 400)
    if not validate_positive_id(group_id):
        return ({"error": "Неверный параметр", "message": "group_id должен быть положительным числом"}, 400)
    if not validate_semester(semester):
        return ({"error": "Ошибка валидации", "message": "semester должен быть от 1 до 8"}, 422)
    if not validate_load_hours(load_hours):
        return ({"error": "Ошибка валидации", "message": "load_hours должно быть > 0"}, 422)
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
            "teacher_id": assignment.teacher_id.id,
            "discipline_id": assignment.discipline_id.id,
            "group_id": assignment.group_id.id,
            "semester": assignment.semester,
            "load_hours": assignment.load_hours,
            "is_active": assignment.is_active
        }
        return (data, 201)
    except IntegrityError as e:
        error_msg = str(e)
        if "UNIQUE" in error_msg:
            return ({"error": "конфликт", "message": "нарушение уникальности"}, 409)
        else:
            # Определяем, какой внешний ключ не найден
            if "teacher_id" in error_msg:
                return ({"error": "Внешний ключ", "message": "teacher_id не найден"}, 500)
            elif "discipline_id" in error_msg:
                return ({"error": "Внешний ключ", "message": "discipline_id не найден"}, 500)
            elif "group_id" in error_msg:
                return ({"error": "Внешний ключ", "message": "group_id не найден"}, 500)
            return ({"error": "Ошибка базы данных", "message": "Произошла ошибка при создании записи"}, 500)
    except OperationalError as e:
        return ({"error": "Ошибка базы данных", "message": str(e)}, 500)
    except ValueError as e:
        return ({"error": "Неверный параметр", "message": f"Ошибка типа параметра: {e}"}, 400)

def update_load_assignment(id, teacher_id=None, discipline_id=None, group_id=None, semester=None, load_hours=None):
    if teacher_id is None and discipline_id is None and group_id is None and semester is None and load_hours is None:
        return ({"error": "Неверный параметр", "message": "Необходимо указать хотя бы одно поле для обновления"}, 400)
    try:
        assignment = LoadAssignment.get(LoadAssignment.id == id, LoadAssignment.is_active == True)
    except DoesNotExist:
        return ({"error": "Не найдено", "message": "Запись не найдена или неактивна"}, 404)

    if teacher_id is not None:
        if not validate_positive_id(teacher_id):
            return ({"error": "Неверный параметр", "message": "teacher_id должен быть положительным числом"}, 400)
    if discipline_id is not None:
        if not validate_positive_id(discipline_id):
            return ({"error": "Неверный параметр", "message": "discipline_id должен быть положительным числом"}, 400)
    if group_id is not None:
        if not validate_positive_id(group_id):
            return ({"error": "Неверный параметр", "message": "group_id должен быть положительным числом"}, 400)
    if semester is not None and not validate_semester(semester):
        return ({"error": "Ошибка валидации", "message": "semester должен быть от 1 до 8"}, 422)
    if load_hours is not None and not validate_load_hours(load_hours):
        return ({"error": "Ошибка валидации", "message": "load_hours должно быть > 0"}, 422)

    # Определяем новую комбинацию после изменений
    new_teacher = teacher_id if teacher_id is not None else assignment.teacher_id.id
    new_discipline = discipline_id if discipline_id is not None else assignment.discipline_id.id
    new_group = group_id if group_id is not None else assignment.group_id.id
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
        return ({"error": "конфликт", "message": "нарушение уникальности"}, 409)

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
        "teacher_id": assignment.teacher_id.id,
        "discipline_id": assignment.discipline_id.id,
        "group_id": assignment.group_id.id,
        "semester": assignment.semester,
        "load_hours": assignment.load_hours,
        "is_active": assignment.is_active
    }
    return (data, 200)

def delete_load_assignment(id):
    try:
        assignment = LoadAssignment.get(LoadAssignment.id == id, LoadAssignment.is_active == True)
        assignment.is_active = False
        assignment.save()
        return ({"result": True}, 200)
    except DoesNotExist:
        return ({"error": "Не найдено", "message": "Запись не найдена или уже неактивна"}, 404)

def get_load_assignment(id):
    try:
        assignment = LoadAssignment.get(LoadAssignment.id == id, LoadAssignment.is_active == True)
        data = {
            "id": assignment.id,
            "teacher_id": assignment.teacher_id.id,
            "discipline_id": assignment.discipline_id.id,
            "group_id": assignment.group_id.id,
            "semester": assignment.semester,
            "load_hours": assignment.load_hours,
            "is_active": assignment.is_active
        }
        return (data, 200)
    except DoesNotExist:
        return ({"error": "Не найдено", "message": "Запись не найдена"}, 404)

def get_load_assignments(teacher_id=None, discipline_id=None, group_id=None, semester=None, limit=100, offset=0):
    # Валидация фильтров
    if teacher_id is not None and not validate_positive_id(teacher_id):
        return ({"error": "Неверный параметр", "message": "teacher_id должен быть положительным числом"}, 400)
    if discipline_id is not None and not validate_positive_id(discipline_id):
        return ({"error": "Неверный параметр", "message": "discipline_id должен быть положительным числом"}, 400)
    if group_id is not None and not validate_positive_id(group_id):
        return ({"error": "Неверный параметр", "message": "group_id должен быть положительным числом"}, 400)
    if semester is not None and not validate_semester(semester):
        # Ошибка валидации - 422
        return ({"error": "Ошибка валидации", "message": "semester должен быть от 1 до 8"}, 422)
    if limit <= 0:
        return ({"error": "Неверный параметр", "message": "limit должен быть больше 0"}, 400)
    if offset < 0:
        return ({"error": "Неверный параметр", "message": "offset не может быть отрицательным"}, 400)

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
            "teacher_id": a.teacher_id.id,
            "discipline_id": a.discipline_id.id,
            "group_id": a.group_id.id,
            "semester": a.semester,
            "load_hours": a.load_hours,
            "is_active": a.is_active
        }
        for a in query
    ]
    return (data, 200)

if __name__ == '__main__':
    create_tables()
