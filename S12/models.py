"""База данных сервиса учебного плана"""

from peewee import (
    Model,
    CharField,
    IntegerField,
    ForeignKeyField,
    AutoField,
    SqliteDatabase,
    Check,
    BooleanField
)

DB = SqliteDatabase('curriculum_plan.db')


class BaseModel(Model):
    """Базовая модель"""

    class Meta:
        database = DB


class CurriculumPlan(BaseModel):
    """Учебный план"""

    id = AutoField()
    name = CharField(
        null=False,
        constraints=[Check("name != ''")]
    )
    speciality_id = IntegerField(
        null=False,
        constraints=[Check("speciality_id > 0")]
    )
    year = IntegerField(
        null=False,
        constraints=[Check("year > 2000")]
    )
    is_active = BooleanField(default=True)


class Subject(BaseModel):
    """Дисциплина"""

    id = AutoField()
    curriculum_plan = ForeignKeyField(
        CurriculumPlan,
        backref='subjects',
        on_delete='CASCADE',
        null=False
    )
    name = CharField(
        null=False,
        constraints=[Check("name != ''")]
    )
    semester = IntegerField(
        null=False,
        constraints=[Check("semester >= 1 AND semester <= 12")]
    )
    is_active = BooleanField(default=True)


class Hours(BaseModel):
    """Часы дисциплины"""

    id = AutoField()
    subject = ForeignKeyField(
        Subject,
        backref='hours',
        on_delete='CASCADE',
        null=False,
        unique=True
    )
    lecture_hours = IntegerField(
        default=0,
        null=False,
        constraints=[Check("lecture_hours >= 0")]
    )
    practice_hours = IntegerField(
        default=0,
        null=False,
        constraints=[Check("practice_hours >= 0")]
    )
    is_active = BooleanField(default=True)


class Assessment(BaseModel):
    """Форма контроля"""

    id = AutoField()
    subject = ForeignKeyField(
        Subject,
        backref='assessments',
        on_delete='CASCADE',
        null=False
    )
    type = CharField(
        null=False,
        constraints=[Check("type IN ('exam', 'zachet')")]
    )
    is_active = BooleanField(default=True)

    class Meta:
        constraints = [SQL('UNIQUE(subject_id, type)')]


def init_db():
    """Инициализация базы данных"""
    with DB:
        DB.create_tables([CurriculumPlan, Subject, Hours, Assessment])


if __name__ == "__main__":
    init_db()
    print("База данных и таблицы созданы успешно!")