from peewee import *
from datetime import datetime

db = SqliteDatabase('curriculum.db')


class BaseModel(Model):
    class Meta:
        database = db


class AssessmentForm:
    """Формы отчетности (Enum)"""
    EXAM = 'exam'
    CREDIT = 'credit'
    CHOICES = [EXAM, CREDIT]


class Group(BaseModel):
    """Группа студентов (ссылка на Group Service)"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=100, unique=True, null=False)

    class Meta:
        table_name = 'groups'


class Discipline(BaseModel):
    """Дисциплина (ссылка на Discipline Service)"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True, null=False)

    class Meta:
        table_name = 'disciplines'


class Semester(BaseModel):
    """Семестр (локальный справочник)"""
    id = AutoField(primary_key=True)
    semester_number = IntegerField(null=False, constraints=[Check('semester_number BETWEEN 1 AND 8')])
    academic_year = CharField(max_length=9, null=False)

    class Meta:
        table_name = 'semesters'
        constraints = [SQL('UNIQUE(semester_number, academic_year)')]


class Curriculum(BaseModel):
    """Учебный план (главный документ)"""
    id = AutoField(primary_key=True)

    # Внешние ключи (NOT NULL)
    group = ForeignKeyField(Group, backref='curriculums', on_delete='CASCADE', null=False)
    discipline = ForeignKeyField(Discipline, backref='curriculums', on_delete='CASCADE', null=False)
    semester = ForeignKeyField(Semester, backref='curriculums', on_delete='RESTRICT', null=False)

    # Поля с ограничениями
    theory_hours = IntegerField(
        null=False,
        constraints=[Check('theory_hours >= 0')]
    )
    practice_hours = IntegerField(
        null=False,
        constraints=[Check('practice_hours >= 0')]
    )
    assessment_form = CharField(
        max_length=10,
        null=False,
        constraints=[Check("assessment_form IN ('exam', 'credit')")]
    )

    # Мягкое удаление
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'curriculum'
        constraints = [
            SQL('UNIQUE(group_id, discipline_id, semester_id)')
        ]


def init_db():
    """Инициализация базы данных: создание всех таблиц"""
    db.connect()
    db.create_tables([Group, Discipline, Semester, Curriculum], safe=True)
    db.close()


def add_default_semesters():
    """Добавление тестовых данных для семестров (необязательно)"""
    db.connect()
    if Semester.select().count() == 0:
        for year in range(2024, 2026):
            for sem in range(1, 5):
                Semester.create(semester_number=sem, academic_year=f"{year}-{year+1}")
        print("✓ Добавлены тестовые семестры")
    db.close()


if __name__ == "__main__":
    init_db()
    add_default_semesters()
    print("База данных и таблицы созданы успешно!")