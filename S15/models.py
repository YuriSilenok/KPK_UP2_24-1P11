from peewee import *
from decimal import Decimal
from playhouse.shortcuts import model_to_dict

class Teacher(Model):
    id = AutoField()
    full_name = CharField(max_length=200, null=False)      # Varchar(200)
    position = CharField(max_length=100, null=False)       # добавлено обязательное поле

    class Meta:
        table_name = 'teachers'

class Discipline(Model):
    id = AutoField()
    name = CharField(max_length=200, null=False, unique=True)  # Varchar(200)
    hours_total = IntegerField(null=False)                     # добавлено обязательное поле

    class Meta:
        table_name = 'disciplines'

class Group(Model):
    id = AutoField()
    group_number = CharField(max_length=20, null=False, unique=True)  # Varchar(20), уникальное
    specialty_id = IntegerField(null=False)                           # обязательное поле

    class Meta:
        table_name = 'groups'

class Student(Model):
    id = AutoField()
    student_number = CharField(max_length=50, null=True, unique=True)  # необязательное
    current_group_id = ForeignKeyField(Group, null=True, backref='students')
    status = CharField(max_length=50, null=False)                      # обязательное поле

    class Meta:
        table_name = 'students'

class LoadAssignment(Model):
    id = AutoField()
    teacher_id = ForeignKeyField(Teacher, null=False, backref='assignments')
    discipline_id = ForeignKeyField(Discipline, null=False, backref='assignments')
    group_id = ForeignKeyField(Group, null=False, backref='assignments')
    semester = IntegerField(null=False, constraints=[SQL('CHECK (semester BETWEEN 1 AND 8)')])
    load_hours = DecimalField(max_digits=5, decimal_places=2, null=False,   # Decimal(5,2)
                              constraints=[SQL('CHECK (load_hours > 0)')])

    class Meta:
        table_name = 'load_assignments'
        indexes = (
            (('teacher_id', 'discipline_id', 'group_id', 'semester'), True),  # уникальный составной ключ
        )

# ==================== API-ФУНКЦИИ ====================

# ----- Teacher -----
def create_teacher(full_name, position):
    if not full_name or not position:
        return {"code": 400, "message": "full_name and position are required"}
    try:
        t = Teacher.create(full_name=full_name, position=position)
        return {"code": 201, "data": model_to_dict(t)}
    except IntegrityError:
        return {"code": 409, "message": "duplicate entry"}

def get_teacher(teacher_id):
    try:
        teacher_id = int(teacher_id)
    except:
        return {"code": 400, "message": "teacher_id must be integer"}
    try:
        t = Teacher.get_by_id(teacher_id)
        return {"code": 200, "data": model_to_dict(t)}
    except Teacher.DoesNotExist:
        return {"code": 404, "message": "not found"}

# ----- Discipline -----
def create_discipline(name, hours_total):
    if not name or hours_total is None:
        return {"code": 400, "message": "name and hours_total are required"}
    try:
        hours_total = int(hours_total)
    except:
        return {"code": 400, "message": "hours_total must be integer"}
    try:
        d = Discipline.create(name=name, hours_total=hours_total)
        return {"code": 201, "data": model_to_dict(d)}
    except IntegrityError:
        return {"code": 409, "message": "duplicate entry"}

def get_discipline(discipline_id):
    try:
        discipline_id = int(discipline_id)
    except:
        return {"code": 400, "message": "discipline_id must be integer"}
    try:
        d = Discipline.get_by_id(discipline_id)
        return {"code": 200, "data": model_to_dict(d)}
    except Discipline.DoesNotExist:
        return {"code": 404, "message": "not found"}

# ----- Group -----
def create_group(group_number, specialty_id):
    if not group_number or specialty_id is None:
        return {"code": 400, "message": "group_number and specialty_id are required"}
    try:
        specialty_id = int(specialty_id)
    except:
        return {"code": 400, "message": "specialty_id must be integer"}
    try:
        g = Group.create(group_number=group_number, specialty_id=specialty_id)
        return {"code": 201, "data": model_to_dict(g)}
    except IntegrityError:
        return {"code": 409, "message": "duplicate entry"}

def get_group(group_id):
    try:
        group_id = int(group_id)
    except:
        return {"code": 400, "message": "group_id must be integer"}
    try:
        g = Group.get_by_id(group_id)
        return {"code": 200, "data": model_to_dict(g)}
    except Group.DoesNotExist:
        return {"code": 404, "message": "not found"}

# ----- Student -----
def create_student(student_number, status, current_group_id=None):
    if not status:
        return {"code": 400, "message": "status is required"}
    if current_group_id is not None:
        try:
            current_group_id = int(current_group_id)
            Group.get_by_id(current_group_id)
        except (ValueError, Group.DoesNotExist):
            return {"code": 404, "message": "group not found"}
    try:
        s = Student.create(
            student_number=student_number if student_number else None,
            status=status,
            current_group_id=current_group_id
        )
        return {"code": 201, "data": model_to_dict(s)}
    except IntegrityError:
        return {"code": 409, "message": "duplicate student_number"}

def get_student(student_id):
    try:
        student_id = int(student_id)
    except:
        return {"code": 400, "message": "student_id must be integer"}
    try:
        s = Student.get_by_id(student_id)
        return {"code": 200, "data": model_to_dict(s)}
    except Student.DoesNotExist:
        return {"code": 404, "message": "not found"}

# ----- LoadAssignment -----
def create_load_assignment(teacher_id, discipline_id, group_id, semester, load_hours):
    # приведение типов и валидация
    try:
        teacher_id = int(teacher_id)
        discipline_id = int(discipline_id)
        group_id = int(group_id)
        semester = int(semester)
        load_hours = Decimal(str(load_hours))
    except:
        return {"code": 400, "message": "invalid parameter type"}
    if not (1 <= semester <= 8):
        return {"code": 400, "message": "semester must be 1..8"}
    if load_hours <= 0:
        return {"code": 400, "message": "load_hours must be > 0"}
    # проверка существования родительских объектов
    try:
        Teacher.get_by_id(teacher_id)
        Discipline.get_by_id(discipline_id)
        Group.get_by_id(group_id)
    except Teacher.DoesNotExist:
        return {"code": 404, "message": "teacher not found"}
    except Discipline.DoesNotExist:
        return {"code": 404, "message": "discipline not found"}
    except Group.DoesNotExist:
        return {"code": 404, "message": "group not found"}
    # создание
    try:
        la = LoadAssignment.create(
            teacher_id=teacher_id,
            discipline_id=discipline_id,
            group_id=group_id,
            semester=semester,
            load_hours=load_hours
        )
        return {"code": 201, "data": model_to_dict(la)}
    except IntegrityError:
        return {"code": 409, "message": "duplicate assignment"}

def get_load_assignment(assignment_id):
    try:
        assignment_id = int(assignment_id)
    except:
        return {"code": 400, "message": "assignment_id must be integer"}
    try:
        la = LoadAssignment.get_by_id(assignment_id)
        return {"code": 200, "data": model_to_dict(la)}
    except LoadAssignment.DoesNotExist:
        return {"code": 404, "message": "not found"}

def update_load_assignment(assignment_id, teacher_id=None, discipline_id=None, group_id=None, semester=None, load_hours=None):
    try:
        assignment_id = int(assignment_id)
        la = LoadAssignment.get_by_id(assignment_id)
    except (ValueError, LoadAssignment.DoesNotExist):
        return {"code": 404, "message": "assignment not found"}

    # обновляем только переданные поля с валидацией
    if teacher_id is not None:
        try:
            teacher_id = int(teacher_id)
            Teacher.get_by_id(teacher_id)
            la.teacher_id = teacher_id
        except (ValueError, Teacher.DoesNotExist):
            return {"code": 404, "message": "teacher not found"}
    if discipline_id is not None:
        try:
            discipline_id = int(discipline_id)
            Discipline.get_by_id(discipline_id)
            la.discipline_id = discipline_id
        except (ValueError, Discipline.DoesNotExist):
            return {"code": 404, "message": "discipline not found"}
    if group_id is not None:
        try:
            group_id = int(group_id)
            Group.get_by_id(group_id)
            la.group_id = group_id
        except (ValueError, Group.DoesNotExist):
            return {"code": 404, "message": "group not found"}
    if semester is not None:
        try:
            semester = int(semester)
            if not (1 <= semester <= 8):
                return {"code": 400, "message": "semester must be 1..8"}
            la.semester = semester
        except ValueError:
            return {"code": 400, "message": "semester must be integer"}
    if load_hours is not None:
        try:
            load_hours = Decimal(str(load_hours))
            if load_hours <= 0:
                return {"code": 400, "message": "load_hours must be > 0"}
            la.load_hours = load_hours
        except:
            return {"code": 400, "message": "invalid load_hours"}

    la.save()
    return {"code": 200, "data": model_to_dict(la)}

def delete_load_assignment(assignment_id):
    try:
        assignment_id = int(assignment_id)
        la = LoadAssignment.get_by_id(assignment_id)
        la.delete_instance()
        return {"code": 200, "message": "deleted"}   # или просто True по требованию
    except (ValueError, LoadAssignment.DoesNotExist):
        return {"code": 404, "message": "not found"}

def list_load_assignments(teacher_id=None, discipline_id=None, group_id=None, semester=None, limit=100, offset=0):
    # фильтры
    query = LoadAssignment.select()
    if teacher_id is not None:
        try:
            query = query.where(LoadAssignment.teacher_id == int(teacher_id))
        except ValueError:
            return {"code": 400, "message": "teacher_id must be integer"}
    if discipline_id is not None:
        try:
            query = query.where(LoadAssignment.discipline_id == int(discipline_id))
        except ValueError:
            return {"code": 400, "message": "discipline_id must be integer"}
    if group_id is not None:
        try:
            query = query.where(LoadAssignment.group_id == int(group_id))
        except ValueError:
            return {"code": 400, "message": "group_id must be integer"}
    if semester is not None:
        try:
            sem = int(semester)
            if not (1 <= sem <= 8):
                return {"code": 400, "message": "semester must be 1..8"}
            query = query.where(LoadAssignment.semester == sem)
        except ValueError:
            return {"code": 400, "message": "semester must be integer"}
    # пагинация
    try:
        limit = int(limit)
        offset = int(offset)
    except ValueError:
        return {"code": 400, "message": "limit and offset must be integers"}
    assignments = list(query.limit(limit).offset(offset))
    return {"code": 200, "data": [model_to_dict(a) for a in assignments]}
