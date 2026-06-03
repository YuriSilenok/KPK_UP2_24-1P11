from peewee import *
import datetime # Импорт нужен для генерации академического года

db = SqliteDatabase('curriculum.db')


class BaseModel(Model):
    class Meta:
        database = db


class AssessmentForm:
    """Формы отчетности (Enum)"""
    EXAM = 'exam'
    CREDIT = 'credit'
    CHOICES = [EXAM, CREDIT]


# --- Модели с добавленным полем is_active ---

class Group(BaseModel):
    """Группа студентов"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=100, unique=True, null=False)
    is_active = BooleanField(default=True, null=False) # Мягкое удаление

    class Meta:
        table_name = 'groups'


class Discipline(BaseModel):
    """Дисциплина"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True, null=False)
    is_active = BooleanField(default=True, null=False) # Мягкое удаление

    class Meta:
        table_name = 'disciplines'


class Semester(BaseModel):
    """Семестр"""
    id = AutoField(primary_key=True)
    semester_number = IntegerField(null=False, constraints=[Check('semester_number BETWEEN 1 AND 8')])
    academic_year = CharField(max_length=9, null=False)
    is_active = BooleanField(default=True, null=False) # Мягкое удаление

    class Meta:
        table_name = 'semesters'
        constraints = [SQL('UNIQUE(semester_number, academic_year)')]


class Curriculum(BaseModel):
    id = AutoField(primary_key=True)

    # Внешние ключи реализованы через ForeignKeyField
    group = ForeignKeyField(Group, backref='curriculums', on_delete='RESTRICT', null=False)
    discipline = ForeignKeyField(Discipline, backref='curriculums', on_delete='RESTRICT', null=False)
    semester = ForeignKeyField(Semester, backref='curriculums', on_delete='RESTRICT', null=False)

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

    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'curriculum'
        constraints = [
            SQL('UNIQUE(group_id, discipline_id, semester_id)')
        ]
        indexes = (
            (('group_id',), False),
            (('discipline_id',), False),
            (('semester_id',), False),
            (('is_active',), False),
        )

    # ... Остальные методы класса Curriculum остаются без изменений ...
    # (create_curriculum, get_by_id_with_names, soft_delete, update_fields, get_filtered_list)
    # Они уже корректно работали с логикой is_active и уникальностью.

def create_tables():
    db.connect()
    db.create_tables([Group, Discipline, Semester, Curriculum], safe=True)
    db.close()


def add_default_data():
    if Semester.select().count() == 0:
        current_year = datetime.datetime.now().year
        for year in range(current_year - 1, current_year + 5): # Создаем семестры на несколько лет вперед/назад
            for sem in range(1, 3):
                Semester.create(semester_number=sem, academic_year=f"{year}-{year+1}")
        print("✓ Семестры добавлены")


if __name__ == "__main__":
    create_tables()
    add_default_data()
    print("База данных и таблицы созданы успешно!")