"""База данных Curriculum Plan"""

from peewee import (
    Model,
    CharField,
    IntegerField,
    ForeignKeyField,
    AutoField,
    SqliteDatabase
)

DB = SqliteDatabase('curriculum_plan.db')

class BaseModel(Model):
    """Базовая модель"""

    class Meta:
        database = DB

class CurriculumPlan(BaseModel):
    """Класс учебного плана"""

    id = AutoField()
    name = CharField(null=False)
    speciality = CharField(null=False)
    year = IntegerField(null=False)

class Subject(BaseModel):
    """Класс дисциплины"""

    id = AutoField()
    curriculum_plan = ForeignKeyField(
        CurriculumPlan,
        backref='subjects',
        on_delete='CASCADE',
        null=False
    )
    name = CharField(null=False)
    semester = IntegerField(null=False)

class Hours(BaseModel):
    """Класс часов по дисциплине"""

    id = AutoField()
    subject = ForeignKeyField(
        Subject,
        backref='hours',
        on_delete='CASCADE',
        null=False
    )
    lecture_hours = IntegerField(default=0, null=False)
    practice_hours = IntegerField(default=0, null=False)

class Assessment(BaseModel):
    """Класс формы контроля"""

    id = AutoField()
    subject = ForeignKeyField(
        Subject,
        backref='assessments',
        on_delete='CASCADE',
        null=False
    )
    type = CharField(null=False)

def create_tables():
    """Создаёт таблицы"""
    with DB:
        DB.create_tables([CurriculumPlan, Subject, Hours, Assessment])

if __name__ == "__main__":
    create_tables()