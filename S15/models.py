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

    class Meta:
        table_name = 'teacher'

class Discipline(BaseModel):
    id = AutoField()
    name = CharField(max_length=200, unique=True, constraints=[SQL('NOT NULL')])
    hours_total = IntegerField(constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'discipline'

class Group(BaseModel):
    id = AutoField()
    group_number = CharField(max_length=20, unique=True, constraints=[SQL('NOT NULL')])
    specialty_id = IntegerField(constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'group'

class Student(BaseModel):
    id = AutoField()
    student_number = CharField(unique=True, null=True)
    current_group_id = ForeignKeyField(Group, backref='students', on_delete='CASCADE', null=True)
    status = CharField(constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'student'

class LoadAssignment(BaseModel):
    id = AutoField()
    teacher_id = ForeignKeyField(Teacher, backref='assignments', on_delete='CASCADE')
    discipline_id = ForeignKeyField(Discipline, backref='assignments', on_delete='CASCADE')
    group_id = ForeignKeyField(Group, backref='assignments', on_delete='CASCADE')
    semester = IntegerField(constraints=[SQL('CHECK (semester BETWEEN 1 AND 8)')])
    load_hours = DecimalField(max_digits=5, decimal_places=2, constraints=[SQL('CHECK (load_hours > 0)')])

    class Meta:
        table_name = 'loadassignment'
        indexes = (
            (('teacher_id', 'discipline_id', 'group_id', 'semester'), True),
        )


def create_tables():
    with db:
        db.create_tables([Teacher, Discipline, Group, Student, LoadAssignment], safe=True)

        if Teacher.select().count() == 0:
            t1 = Teacher.create(full_name='Иванов Иван Иванович', position='Профессор')
            t2 = Teacher.create(full_name='Петрова Мария Сергеевна', position='Доцент')
            t3 = Teacher.create(full_name='Сидоров Алексей Владимирович', position='Старший преподаватель')

        if Discipline.select().count() == 0:
            d1 = Discipline.create(name='Математика', hours_total=144)
            d2 = Discipline.create(name='Физика', hours_total=108)
            d3 = Discipline.create(name='Программирование', hours_total=180)

        if Group.select().count() == 0:
            g1 = Group.create(group_number='ИС-101', specialty_id=1)
            g2 = Group.create(group_number='ИС-102', specialty_id=1)
            g3 = Group.create(group_number='ПМ-201', specialty_id=2)

        if Student.select().count() == 0:
            Student.create(student_number='2024001', current_group_id=1, status='Обучается')
            Student.create(student_number='2024002', current_group_id=1, status='Обучается')
            Student.create(student_number='2024003', current_group_id=2, status='Академический отпуск')

        if LoadAssignment.select().count() == 0:
            LoadAssignment.create(teacher_id=1, discipline_id=1, group_id=1, semester=1, load_hours=36.5)
            LoadAssignment.create(teacher_id=2, discipline_id=2, group_id=1, semester=1, load_hours=32.0)
            LoadAssignment.create(teacher_id=1, discipline_id=1, group_id=2, semester=1, load_hours=36.5)
            LoadAssignment.create(teacher_id=3, discipline_id=3, group_id=1, semester=2, load_hours=45.0)


if __name__ == '__main__':
    create_tables()
