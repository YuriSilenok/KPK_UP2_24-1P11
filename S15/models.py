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
    specialty_id = IntegerField(constraints=[SQL('NOT NULL')])

class Students(BaseModel):
    id = AutoField()
    student_number = CharField(max_length=50, unique=True)  # VARCHAR без NOT NULL
    current_group_id = ForeignKeyField(Group, backref='students', on_delete='CASCADE', null=True)  # может быть NULL
    status = CharField(max_length=50, constraints=[SQL('NOT NULL')])

class LoadAssignment(BaseModel):
    id = AutoField()
    teacher_id = ForeignKeyField(Teacher, backref='assignments', on_delete='CASCADE')
    discipline_id = ForeignKeyField(Discipline, backref='assignments', on_delete='CASCADE')
    group_id = ForeignKeyField(Group, backref='assignments', on_delete='CASCADE')
    semester = IntegerField(constraints=[SQL('CHECK (semester BETWEEN 1 AND 8)')])
    load_hours = DecimalField(max_digits=5, decimal_places=2, constraints=[SQL('CHECK (load_hours > 0)')])

    class Meta:
        indexes = (
            (('teacher_id', 'discipline_id', 'group_id', 'semester'), True),  # уникальный составной ключ
        )


# Функция для создания таблиц и заполнения начальными данными
def create_tables():
    db.connect()
    db.create_tables([Teacher, Discipline, Group, Students, LoadAssignment], safe=True)

    # Добавление начальных данных, если таблицы пустые
    if Teacher.select().count() == 0:
        Teacher.create(full_name='Иванов Иван Иванович', position='Профессор')
        Teacher.create(full_name='Петрова Мария Сергеевна', position='Доцент')
        Teacher.create(full_name='Сидоров Алексей Владимирович', position='Старший преподаватель')

    if Discipline.select().count() == 0:
        Discipline.create(name='Математика', hours_total=144)
        Discipline.create(name='Физика', hours_total=108)
        Discipline.create(name='Программирование', hours_total=180)

    if Group.select().count() == 0:
        Group.create(group_number='ИС-101', specialty_id=1)
        Group.create(group_number='ИС-102', specialty_id=1)
        Group.create(group_number='ПМ-201', specialty_id=2)

    if Students.select().count() == 0:
        Students.create(student_number='2024001', current_group_id=1, status='Обучается')
        Students.create(student_number='2024002', current_group_id=1, status='Обучается')
        Students.create(student_number='2024003', current_group_id=2, status='Академический отпуск')

    if LoadAssignment.select().count() == 0:
        LoadAssignment.create(teacher_id=1, discipline_id=1, group_id=1, semester=1, load_hours=36.5)
        LoadAssignment.create(teacher_id=2, discipline_id=2, group_id=1, semester=1, load_hours=32.0)
        LoadAssignment.create(teacher_id=1, discipline_id=1, group_id=2, semester=1, load_hours=36.5)
        LoadAssignment.create(teacher_id=3, discipline_id=3, group_id=1, semester=2, load_hours=45.0)

    print("Таблицы успешно созданы и заполнены начальными данными!")
    db.close()


if __name__ == '__main__':
    create_tables()
