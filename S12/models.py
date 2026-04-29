"""База данных Curriculum Plan"""

from peewee import (
    Model,
    CharField,
    IntegerField,
    ForeignKeyField,
    AutoField,
    SqliteDatabase,
    Check
)

DB = SqliteDatabase('curriculum_plan.db')

class BaseModel(Model):
    """Базовая модель"""

    class Meta:
        database = DB

class CurriculumPlan(BaseModel):
    """Класс учебного плана"""

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

class Subject(BaseModel):
    """Класс дисциплины"""

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

class Hours(BaseModel):
    """Класс часов дисциплины"""

    id = AutoField()

    subject = ForeignKeyField(
        Subject,
        backref='hours',
        on_delete='CASCADE',
        null=False
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

class Assessment(BaseModel):
    """Класс формы контроля"""

    id = AutoField()

    subject = ForeignKeyField(
        Subject,
        backref='assessments',
        on_delete='CASCADE',
        null=False
    )

    type = CharField(
        null=False,
        constraints=[Check("type IN ('экзамен', 'зачет')")]
    )

def create_tables():
    """Создаёт таблицы"""
    with DB:
        DB.create_tables([CurriculumPlan, Subject, Hours, Assessment])

if __name__ == "__main__":
    create_tables()