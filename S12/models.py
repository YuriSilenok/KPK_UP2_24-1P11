from peewee import (
    Model,
    CharField,
    IntegerField,
    BooleanField,
    AutoField,
    ForeignKeyField,
    SqliteDatabase,
    Check,
    SQL
)

# Подключение к локальной базе данных SQLite для Варианта 12
db = SqliteDatabase('curriculum_service_s12.db')


class BaseModel(Model):
    """Базовая модель для настройки подключения"""
    class Meta:
        database = db


class Group(BaseModel):
    """Группа студентов"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=100, unique=True, null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'groups'


class Discipline(BaseModel):
    """Дисциплина"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True, null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'disciplines'


class Semester(BaseModel):
    """Семестр"""
    id = AutoField(primary_key=True)
    semester = IntegerField(null=False, constraints=[Check('semester BETWEEN 1 AND 8')])
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'semesters'
        constraints = [SQL('UNIQUE(semester)')]
class Curriculums(BaseModel):
    """Запись учебного плана"""
    id = AutoField(primary_key=True)

    # Внешние ключи с исправленным синтаксисом backref и проверкой на положительность ID (> 0)
    group = ForeignKeyField(Group, backref='curriculums', on_delete='CASCADE', column_name='group_id', null=False, constraints=[Check('group_id > 0')])
    discipline = ForeignKeyField(Discipline, backref='curriculums', on_delete='CASCADE', column_name='discipline_id', null=False, constraints=[Check('discipline_id > 0')])
    semester = ForeignKeyField(Semester, backref='curriculums', on_delete='CASCADE', column_name='semester_id', null=False, constraints=[Check('semester_id > 0')])

    theory_hours = IntegerField(null=False, constraints=[Check('theory_hours >= 0')])
    practice_hours = IntegerField(null=False, constraints=[Check('practice_hours >= 0')])
    assessment_form = CharField(max_length=10, null=False, constraints=[Check("assessment_form IN ('exam', 'credit')")])

    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'curriculums'
        constraints = [
            SQL('UNIQUE(group_id, discipline_id, semester_id)')
        ]
        # Добавлены индексы для оптимизации фильтрации по часам теории, практики и статусу активности
        indexes = (
            (('theory_hours',), False),
            (('practice_hours',), False),
            (('is_active',), False),
        )


def init_db():
    """Обязательная функция инициализации БД. Исключительно создает таблицы."""
    with db:
        db.create_tables([Group, Discipline, Semester, Curriculums], safe=True)


if __name__ == "__main__":
    init_db()
    print("S12 Curriculum Service: БД успешно инициализирована.")
