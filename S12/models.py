from peewee import (
    Model,
    CharField,
    IntegerField,
    BooleanField,
    AutoField,
    ForeignKeyField,
    SqliteDatabase,
    Check
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


class Curriculum(BaseModel):
    """Запись учебного плана (Класс унифицирован по названию в API)"""
    id = AutoField(primary_key=True)

    # Чистые внешние ключи без избыточных проверок >0 уровня БД
    group_id = ForeignKeyField(Group, backref='curriculums', on_delete='CASCADE', column_name='group_id', null=False)
    discipline_id = ForeignKeyField(Discipline, backref='curriculums', on_delete='CASCADE', column_name='discipline_id', null=False)
    semester_id = ForeignKeyField(Semester, backref='curriculums', on_delete='CASCADE', column_name='semester_id', null=False)

    theory_hours = IntegerField(null=False, constraints=[Check('theory_hours >= 0')])
    practice_hours = IntegerField(null=False, constraints=[Check('practice_hours >= 0')])
    
    # max_length удален, так как он отсутствовал в спецификации doc.md
    assessment_form = CharField(null=False, constraints=[Check("assessment_form IN ('exam', 'credit')")])

    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'curriculums'
        # Оставлен только строго документированный индекс составной уникальности
        indexes = [
            (('group_id', 'discipline_id', 'semester_id'), True)
        ]


def init_db():
    """Обязательная функция инициализации БД. Исключительно создает таблицы."""
    with db:
        db.create_tables([Group, Discipline, Semester, Curriculum], safe=True)


if __name__ == "__main__":
    init_db()
    print("S12 Curriculum Service: БД успешно инициализирована.")
