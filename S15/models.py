from peewee import Model, SqliteDatabase, IntegerField, CharField, DecimalField, ForeignKeyField, IntegrityError, SQL
from peewee import DoesNotExist

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
    current_group_id = ForeignKeyField(Group, backref="students", on_delete='CASCADE', null=True)
    status = CharField(max_length=50, constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'Student'

class LoadAssignment(BaseModel):
    id = IntegerField(primary_key=True)
    teacher_id = ForeignKeyField(Teacher, backref='assignments', on_delete='CASCADE', null=False)
    discipline_id = ForeignKeyField(Discipline, backref='assignments', on_delete='CASCADE', null=False)
    group_id = ForeignKeyField(Group, backref='assignments', on_delete='CASCADE', null=False)
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

def validate_semester(semester):
    return 1 <= semester <= 8

def validate_load_hours(hours):
    return hours > 0

def add_load_assignment(teacher_id, discipline_id, group_id, semester, load_hours):
    """Добавить новую нагрузку."""
    if not validate_semester(semester):
        return {"error": "invalid semester", "message": "semester должен быть от 1 до 8"}
    if not validate_load_hours(load_hours):
        return {"error": "invalid load_hours", "message": "load_hours должно быть > 0"}
    try:
        assignment = LoadAssignment.create(
            teacher_id=teacher_id,
            discipline_id=discipline_id,
            group_id=group_id,
            semester=semester,
            load_hours=load_hours
        )
        return {
            "id": assignment.id,
            "teacher_id": assignment.teacher_id.id,
            "discipline_id": assignment.discipline_id.id,
            "group_id": assignment.group_id.id,
            "semester": assignment.semester,
            "load_hours": assignment.load_hours
        }
    except IntegrityError as e:
        if "UNIQUE" in str(e):
            return {"error": "duplicate entry", "message": "Такая нагрузка уже существует"}
        else:
            return {"error": "foreign key", "message": "Неверный teacher_id, discipline_id или group_id"}
    except ValueError as e:
        return {"error": "invalid parameter", "message": f"Ошибка типа параметра: {e}"}

def update_load_assignment(id, teacher_id=None, discipline_id=None, group_id=None, semester=None, load_hours=None):
    """Обновить нагрузку по ID."""
    try:
        assignment = LoadAssignment.get_by_id(id)
        if semester is not None and not validate_semester(semester):
            return {"error": "invalid semester", "message": "semester должен быть от 1 до 8"}
        if load_hours is not None and not validate_load_hours(load_hours):
            return {"error": "invalid load_hours", "message": "load_hours должно быть > 0"}

        # Проверка уникальности комбинации перед сохранением
        new_teacher = teacher_id if teacher_id is not None else assignment.teacher_id.id
        new_discipline = discipline_id if discipline_id is not None else assignment.discipline_id.id
        new_group = group_id if group_id is not None else assignment.group_id.id
        new_semester = semester if semester is not None else assignment.semester

        # Исключаем текущую запись из проверки
        duplicate = LoadAssignment.select().where(
            (LoadAssignment.teacher_id == new_teacher) &
            (LoadAssignment.discipline_id == new_discipline) &
            (LoadAssignment.group_id == new_group) &
            (LoadAssignment.semester == new_semester) &
            (LoadAssignment.id != id)
        ).exists()
        if duplicate:
            return {"error": "duplicate entry", "message": "Такая нагрузка уже существует"}

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
        return {
            "id": assignment.id,
            "teacher_id": assignment.teacher_id.id,
            "discipline_id": assignment.discipline_id.id,
            "group_id": assignment.group_id.id,
            "semester": assignment.semester,
            "load_hours": assignment.load_hours
        }
    except DoesNotExist:
        return {"error": "not found", "message": "Запись не найдена"}
    except IntegrityError as e:
        if "UNIQUE" in str(e):
            return {"error": "duplicate entry", "message": "Такая нагрузка уже существует"}
        else:
            return {"error": "foreign key", "message": "Неверный teacher_id, discipline_id или group_id"}
    except ValueError as e:
        return {"error": "invalid parameter", "message": f"Ошибка типа параметра: {e}"}

def delete_load_assignment(id):
    """Удалить нагрузку по ID."""
    try:
        assignment = LoadAssignment.get_by_id(id)
        assignment.delete_instance()
        return True
    except DoesNotExist:
        return False

def get_load_assignment(id):
    """Получить нагрузку по ID."""
    try:
        assignment = LoadAssignment.get_by_id(id)
        return {
            "id": assignment.id,
            "teacher_id": assignment.teacher_id.id,
            "discipline_id": assignment.discipline_id.id,
            "group_id": assignment.group_id.id,
            "semester": assignment.semester,
            "load_hours": assignment.load_hours
        }
    except DoesNotExist:
        return {"error": "not found", "message": "Запись не найдена"}

def get_load_assignments(teacher_id=None, discipline_id=None, group_id=None, semester=None, limit=100, offset=0):
    """Получить список нагрузок с фильтрацией."""
    try:
        query = LoadAssignment.select()
        if teacher_id is not None:
            query = query.where(LoadAssignment.teacher_id == teacher_id)
        if discipline_id is not None:
            query = query.where(LoadAssignment.discipline_id == discipline_id)
        if group_id is not None:
            query = query.where(LoadAssignment.group_id == group_id)
        if semester is not None:
            query = query.where(LoadAssignment.semester == semester)
        if offset < 0:
            return {"error": "invalid offset", "message": "offset не может быть отрицательным"}
        if limit <= 0:
            return {"error": "invalid limit", "message": "limit должен быть больше 0"}
        query = query.offset(offset).limit(limit)
        return [
            {
                "id": a.id,
                "teacher_id": a.teacher_id.id,
                "discipline_id": a.discipline_id.id,
                "group_id": a.group_id.id,
                "semester": a.semester,
                "load_hours": a.load_hours
            }
            for a in query
        ]
    except ValueError as e:
        return {"error": "invalid parameter", "message": f"Ошибка параметров: {e}"}

if __name__ == '__main__':
    create_tables()
