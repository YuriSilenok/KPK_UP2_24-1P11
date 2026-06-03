from peewee import *
import datetime

db = SqliteDatabase('curriculum.db')


class BaseModel(Model):
    class Meta:
        database = db


class AssessmentForm:
    """Формы отчетности (Enum)"""
    EXAM = 'exam'
    CREDIT = 'credit'
    CHOICES = [EXAM, CREDIT]


# --- Справочники для других сервисов (оставлены для полноты) ---

class Group(BaseModel):
    """Группа студентов (хранится в Group Service)"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=100, unique=True, null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'groups'


class Discipline(BaseModel):
    """Дисциплина (хранится в Discipline Service)"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True, null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'disciplines'


class Semester(BaseModel):
    """Семестр (хранится в Academic Period Service)"""
    id = AutoField(primary_key=True)
    semester_number = IntegerField(null=False, constraints=[Check('semester_number BETWEEN 1 AND 8')])
    academic_year = CharField(max_length=9, null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'semesters'
        constraints = [SQL('UNIQUE(semester_number, academic_year)')]


# --- Модель для Curriculum Service ---

class Curriculum(BaseModel):
    id = AutoField(primary_key=True)

    # Внешние ключи заменены на IntegerField, так как сущности хранятся в других сервисах
    group_id = IntegerField(null=False) # Ссылка на Group Service
    discipline_id = IntegerField(null=False) # Ссылка на Discipline Service
    semester_id = IntegerField(null=False) # Ссылка на Academic Period Service

    theory_hours = IntegerField(null=False, constraints=[Check('theory_hours >= 0')])
    practice_hours = IntegerField(null=False, constraints=[Check('practice_hours >= 0')])
    assessment_form = CharField(max_length=10, null=False, constraints=[Check("assessment_form IN ('exam', 'credit')")])

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

    # ... [остальные методы без изменений] ...

    @classmethod
    def get_filtered_list(cls, filters=None, page=1, page_size=20):
        # ДОБАВЛЕНА ВАЛИДАЦИЯ page_size согласно описанию API
        if page_size < 1 or page_size > 100:
            raise ValueError("Параметр page_size должен быть в диапазоне от 1 до 100.")
            
        query = cls.select()
        # ... [остальной код метода] ...