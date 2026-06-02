from peewee import Model, SqliteDatabase, IntegerField, CharField, DecimalField, ForeignKeyField, IntegrityError, SQL, BooleanField, AutoField
from peewee import DoesNotExist
from decimal import Decimal, InvalidOperation

# Инициализация базы данных SQLite
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
    # Связи через ForeignKeyField настроены строго без null=True
    teacher = ForeignKeyField(Teacher, backref='assignments', on_delete='CASCADE', null=False)
    discipline = ForeignKeyField(Discipline, backref='assignments', on_delete='CASCADE', null=False)
    group = ForeignKeyField(Group, backref='assignments', on_delete='CASCADE', null=False)
    semester = IntegerField(constraints=[SQL('CHECK (semester BETWEEN 1 AND 8)'), SQL('NOT NULL')])
    load_hours = DecimalField(max_digits=5, decimal_places=2, constraints=[SQL('CHECK (load_hours > 0)'), SQL('NOT NULL')])
    is_active = BooleanField(default=True)  # Логическое удаление строго через is_active

    class Meta:
        table_name = 'LoadAssignment'
        indexes = (
            # Уникальный индекс для предотвращения дубликатов в БД
            (('teacher', 'discipline', 'group', 'semester'), True),
        )

def create_tables():
    """Функция инициализации базы данных и создания таблиц"""
    db.connect()
    db.create_tables([Teacher, Discipline, Group, Student, LoadAssignment], safe=True)
    db.close()

def add_load_assignment(teacher_id, discipline_id, group_id, semester, load_hours):
    """Добавление сущности распределения нагрузки (POST)"""
    # Валидация наличия всех параметров
    if any(v is None for v in [teacher_id, discipline_id, group_id, semester, load_hours]):
        return ({"error": "invalid parameter", "message": "Все поля являются обязательными"}, 400)
    
    # Валидация типов данных
    try:
        teacher_id = int(teacher_id)
        discipline_id = int(discipline_id)
        group_id = int(group_id)
        semester = int(semester)
        load_hours = Decimal(str(load_hours))
    except (ValueError, TypeError, InvalidOperation):
        return ({"error": "invalid parameter", "message": "Неверный тип данных параметров"}, 400)

    # Валидация бизнес-ограничений строго по тексту ошибок из doc.md
    if not (1 <= semester <= 8):
        return ({"error": "validation error", "message": "semester не входит в диапазон 1-8"}, 422)
    if load_hours <= 0:
        return ({"error": "validation error", "message": "load_hours <= 0"}, 422)
    
    # Пре-проверка существования связанных внешних ключей (предотвращение 500 ошибки базы)
    if not Teacher.select().where(Teacher.id == teacher_id).exists():
        return ({"error": "not found", "message": f"Teacher с id {teacher_id} не найден"}, 404)
    if not Discipline.select().where(Discipline.id == discipline_id).exists():
        return ({"error": "not found", "message": f"Discipline с id {discipline_id} не найден"}, 404)
    if not Group.select().where(Group.id == group_id).exists():
        return ({"error": "not found", "message": f"Group с id {group_id} не найден"}, 404)

    try:
        assignment = LoadAssignment.create(
            teacher=teacher_id,
            discipline=discipline_id,
            group=group_id,
            semester=semester,
            load_hours=load_hours,
            is_active=True
        )
        
        # Выходные параметры JSON соответствуют doc.md (без суффиксов _id_id и без is_active)
        return ({
            "id": assignment.id,
            "teacher_id": teacher_id,
            "discipline_id": discipline_id,
            "group_id": group_id,
            "semester": assignment.semester,
            "load_hours": assignment.load_hours
        }, 201)
    except IntegrityError:
        return ({"error": "duplicate entry", "message": "Такая нагрузка уже существует"}, 409)

def update_load_assignment(id, teacher_id=None, discipline_id=None, group_id=None, semester=None, load_hours=None):
    """Изменение сущности распределения нагрузки по ID (PUT)"""
    if all(v is None for v in [teacher_id, discipline_id, group_id, semester, load_hours]):
        return ({"error": "invalid parameter", "message": "Необходимо указать хотя бы одно поле для обновления"}, 400)
        
    try:
        assignment = LoadAssignment.get(LoadAssignment.id == id, LoadAssignment.is_active == True)
    except DoesNotExist:
        return ({"error": "not found", "message": "Запись не найдена"}, 404)

    # Пошаговая валидация типов и существования внешних сущностей при обновлении поля
    if teacher_id is not None:
        try: teacher_id = int(teacher_id)
        except (ValueError, TypeError): return ({"error": "invalid parameter", "message": "Неверный тип для teacher_id"}, 400)
        if not Teacher.select().where(Teacher.id == teacher_id).exists():
            return ({"error": "not found", "message": "Указанный Teacher не существует"}, 404)
        assignment.teacher = teacher_id

    if discipline_id is not None:
        try: discipline_id = int(discipline_id)
        except (ValueError, TypeError): return ({"error": "invalid parameter", "message": "Неверный тип для discipline_id"}, 400)
        if not Discipline.select().where(Discipline.id == discipline_id).exists():
            return ({"error": "not found", "message": "Указанная Discipline не существует"}, 404)
        assignment.discipline = discipline_id

    if group_id is not None:
        try: group_id = int(group_id)
        except (ValueError, TypeError): return ({"error": "invalid parameter", "message": "Неверный тип для group_id"}, 400)
        if not Group.select().where(Group.id == group_id).exists():
            return ({"error": "not found", "message": "Указанная Group не существует"}, 404)
        assignment.group = group_id

    if semester is not None:
        try: semester = int(semester)
        except (ValueError, TypeError): return ({"error": "invalid parameter", "message": "Неверный тип для semester"}, 400)
        if not (1 <= semester <= 8):
            return ({"error": "validation error", "message": "semester не входит в диапазон 1-8"}, 422)
        assignment.semester = semester

    if load_hours is not None:
        try: load_hours = Decimal(str(load_hours))
        except (ValueError, TypeError, InvalidOperation): return ({"error": "invalid parameter", "message": "Неверный тип для load_hours"}, 400)
        if load_hours <= 0:
            return ({"error": "validation error", "message": "load_hours <= 0"}, 422)
        assignment.load_hours = load_hours

    # Проверка уникальности новой комбинации полей перед сохранением изменения
    duplicate = LoadAssignment.select().where(
        (LoadAssignment.teacher == (teacher_id if teacher_id is not None else assignment.teacher_id)),
        (LoadAssignment.discipline == (discipline_id if discipline_id is not None else assignment.discipline_id)),
        (LoadAssignment.group == (group_id if group_id is not None else assignment.group_id)),
        (LoadAssignment.semester == (semester if semester is not None else assignment.semester)),
        (LoadAssignment.id != id),
        (LoadAssignment.is_active == True)
    ).exists()
    
    if duplicate:
        return ({"error": "duplicate entry", "message": "Такая нагрузка уже существует"}, 409)

    assignment.save()
    
    return ({
        "id": assignment.id,
        "teacher_id": assignment.teacher_id,
        "discipline_id": assignment.discipline_id,
        "group_id": assignment.group_id,
        "semester": assignment.semester,
        "load_hours": assignment.load_hours
    }, 200)

def delete_load_assignment(id):
    """Логическое удаление сущности распределения нагрузки (DELETE)"""
    try:
        assignment = LoadAssignment.get(LoadAssignment.id == id, LoadAssignment.is_active == True)
        assignment.is_active = False
        assignment.save()
        return (True, 200)  # Успех: True и HTTP 200 строго по регламенту doc.md
    except DoesNotExist:
        return (False, 404)  # Ошибка: False и HTTP 404, если запись отсутствует

def get_load_assignment(id):
    """Получение одной сущности по ID (GET)"""
    try:
        assignment = LoadAssignment.get(LoadAssignment.id == id, LoadAssignment.is_active == True)
        return ({
            "id": assignment.id,
            "teacher_id": assignment.teacher_id,
            "discipline_id": assignment.discipline_id,
            "group_id": assignment.group_id,
            "semester": assignment.semester,
            "load_hours": assignment.load_hours
        }, 200)
    except DoesNotExist:
        return ({"error": "not found", "message": "Запись не найдена"}, 404)

def get_load_assignments(teacher_id=None, discipline_id=None, group_id=None, semester=None, limit=100, offset=0):
