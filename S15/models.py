from peewee import *
from decimal import Decimal
from playhouse.shortcuts import model_to_dict

# Предполагается, что база данных уже инициализирована где-то в другом месте (например, в main.py)
# from main import database

# Если database не передается, можно создать временное подключение для демонстрации, но в реальном проекте импортируйте из main
# database = SqliteDatabase('schedule.db') 

class BaseModel(Model):
    class Meta:
        # database = database  # Раскомментируйте при интеграции с main.py
        pass

class Teacher(BaseModel):
    id = AutoField()
    full_name = CharField(max_length=255, constraints=[SQL('NOT NULL')])
    
    class Meta:
        table_name = 'teachers'  # Множественное число для соответствия стандарту (опционально, но общепринято)

class Discipline(BaseModel):
    id = AutoField()
    name = CharField(max_length=255, constraints=[SQL('NOT NULL')], unique=True)
    
    class Meta:
        table_name = 'disciplines'

class Group(BaseModel):
    id = AutoField()
    name = CharField(max_length=100, constraints=[SQL('NOT NULL')], unique=True)
    
    class Meta:
        table_name = 'groups'

class Student(BaseModel):
    id = AutoField()
    full_name = CharField(max_length=255, constraints=[SQL('NOT NULL')])
    student_number = CharField(max_length=50, constraints=[SQL('NOT NULL')], unique=True)  # Убран null=True
    current_group_id = ForeignKeyField(Group, backref='students', field='id', constraints=[SQL('NOT NULL')])  # Убран null=True
    
    class Meta:
        table_name = 'students'

class TeachingAssignment(BaseModel):
    id = AutoField()
    teacher_id = ForeignKeyField(Teacher, backref='assignments', field='id', constraints=[SQL('NOT NULL')])
    discipline_id = ForeignKeyField(Discipline, backref='assignments', field='id', constraints=[SQL('NOT NULL')])
    group_id = ForeignKeyField(Group, backref='assignments', field='id', constraints=[SQL('NOT NULL')])
    semester = IntegerField(constraints=[SQL('CHECK (semester BETWEEN 1 AND 8)'), SQL('NOT NULL')])
    load_hours = DecimalField(max_digits=10, decimal_places=2, constraints=[SQL('CHECK (load_hours > 0)'), SQL('NOT NULL')])
    
    class Meta:
        table_name = 'teaching_assignments'
        indexes = (
            (('teacher_id', 'discipline_id', 'group_id', 'semester'), True),  # Уникальный составной индекс
        )

# Функции API с улучшенной валидацией и кодами ошибок

# --- Функции для Teacher ---
def create_teacher(full_name: str):
    if not full_name:
        return {"code": 400, "message": "full_name is required"}
    try:
        teacher = Teacher.create(full_name=full_name)
        return {"code": 201, "data": model_to_dict(teacher)}
    except IntegrityError:
        return {"code": 409, "message": "duplicate entry"}  # 409 Conflict

def get_teacher(teacher_id: int):
    try:
        teacher_id = int(teacher_id)  # Явное приведение типа
    except (ValueError, TypeError):
        return {"code": 400, "message": "teacher_id must be an integer"}
    try:
        teacher = Teacher.get_by_id(teacher_id)
        return {"code": 200, "data": model_to_dict(teacher)}
    except Teacher.DoesNotExist:
        return {"code": 404, "message": "not found"}

# --- Функции для Discipline ---
def create_discipline(name: str):
    if not name:
        return {"code": 400, "message": "name is required"}
    try:
        discipline = Discipline.create(name=name)
        return {"code": 201, "data": model_to_dict(discipline)}
    except IntegrityError:
        return {"code": 409, "message": "duplicate entry"}

def get_discipline(discipline_id: int):
    try:
        discipline_id = int(discipline_id)
    except (ValueError, TypeError):
        return {"code": 400, "message": "discipline_id must be an integer"}
    try:
        discipline = Discipline.get_by_id(discipline_id)
        return {"code": 200, "data": model_to_dict(discipline)}
    except Discipline.DoesNotExist:
        return {"code": 404, "message": "not found"}

# --- Функции для Group ---
def create_group(name: str):
    if not name:
        return {"code": 400, "message": "name is required"}
    try:
        group = Group.create(name=name)
        return {"code": 201, "data": model_to_dict(group)}
    except IntegrityError:
        return {"code": 409, "message": "duplicate entry"}

def get_group(group_id: int):
    try:
        group_id = int(group_id)
    except (ValueError, TypeError):
        return {"code": 400, "message": "group_id must be an integer"}
    try:
        group = Group.get_by_id(group_id)
        return {"code": 200, "data": model_to_dict(group)}
    except Group.DoesNotExist:
        return {"code": 404, "message": "not found"}

# --- Функции для Student ---
def create_student(full_name: str, student_number: str, current_group_id: int):
    if not full_name:
        return {"code": 400, "message": "full_name is required"}
    if not student_number:
        return {"code": 400, "message": "student_number is required"}
    try:
        current_group_id = int(current_group_id)
    except (ValueError, TypeError):
        return {"code": 400, "message": "current_group_id must be an integer"}
    
    # Проверяем, существует ли группа
    try:
        Group.get_by_id(current_group_id)
    except Group.DoesNotExist:
        return {"code": 404, "message": "group not found"}
    
    try:
        student = Student.create(
            full_name=full_name,
            student_number=student_number,
            current_group_id=current_group_id
        )
        return {"code": 201, "data": model_to_dict(student)}
    except IntegrityError:
        return {"code": 409, "message": "duplicate entry (student_number must be unique)"}

def get_student(student_id: int):
    try:
        student_id = int(student_id)
    except (ValueError, TypeError):
        return {"code": 400, "message": "student_id must be an integer"}
    try:
        student = Student.get_by_id(student_id)
        return {"code": 200, "data": model_to_dict(student)}
    except Student.DoesNotExist:
        return {"code": 404, "message": "not found"}

# --- Функции для TeachingAssignment ---
def create_teaching_assignment(teacher_id: int, discipline_id: int, group_id: int, semester: int, load_hours: Decimal):
    # Приведение типов и валидация
    try:
        teacher_id = int(teacher_id)
    except (ValueError, TypeError):
        return {"code": 400, "message": "teacher_id must be an integer"}
    try:
        discipline_id = int(discipline_id)
    except (ValueError, TypeError):
        return {"code": 400, "message": "discipline_id must be an integer"}
    try:
        group_id = int(group_id)
    except (ValueError, TypeError):
        return {"code": 400, "message": "group_id must be an integer"}
    try:
        semester = int(semester)
    except (ValueError, TypeError):
        return {"code": 400, "message": "semester must be an integer"}
    
    # Проверка диапазона семестра (1-8)
    if semester < 1 or semester > 8:
        return {"code": 400, "message": "semester must be between 1 and 8"}
    
    # Проверка load_hours > 0
    try:
        load_hours = Decimal(str(load_hours))
        if load_hours <= 0:
            return {"code": 400, "message": "load_hours must be greater than 0"}
    except (ValueError, TypeError, InvalidOperation):
        return {"code": 400, "message": "load_hours must be a valid decimal number"}
    
    # Проверка существования связанных записей
    try:
        Teacher.get_by_id(teacher_id)
    except Teacher.DoesNotExist:
        return {"code": 404, "message": "teacher not found"}
    
    try:
        Discipline.get_by_id(discipline_id)
    except Discipline.DoesNotExist:
        return {"code": 404, "message": "discipline not found"}
    
    try:
        Group.get_by_id(group_id)
    except Group.DoesNotExist:
        return {"code": 404, "message": "group not found"}
    
    # Создание записи
    try:
        assignment = TeachingAssignment.create(
            teacher_id=teacher_id,
            discipline_id=discipline_id,
            group_id=group_id,
            semester=semester,
            load_hours=load_hours
        )
        return {"code": 201, "data": model_to_dict(assignment)}
    except IntegrityError:
        return {"code": 409, "message": "duplicate entry: such teaching assignment already exists"}

def get_teaching_assignment(assignment_id: int):
    try:
        assignment_id = int(assignment_id)
    except (ValueError, TypeError):
        return {"code": 400, "message": "assignment_id must be an integer"}
    try:
        assignment = TeachingAssignment.get_by_id(assignment_id)
        return {"code": 200, "data": model_to_dict(assignment)}
    except TeachingAssignment.DoesNotExist:
        return {"code": 404, "message": "not found"}
