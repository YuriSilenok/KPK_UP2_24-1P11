from peewee import (
    Model, CharField, IntegerField, ForeignKeyField,
    AutoField, SqliteDatabase, Check, BooleanField
)

db = SqliteDatabase('curriculum_plan.db')


class BaseModel(Model):
    class Meta:
        database = db


class CurriculumPlan(BaseModel):
    id = AutoField()
    name = CharField(null=False, constraints=[Check("name != ''")])
    speciality_id = IntegerField(null=False, constraints=[Check("speciality_id > 0")])
    year = IntegerField(null=False, constraints=[Check("year > 2000")])
    is_active = BooleanField(default=True)


class Subject(BaseModel):
    id = AutoField()
    curriculum_plan = ForeignKeyField(CurriculumPlan, backref='subjects', on_delete='CASCADE', null=False)
    name = CharField(null=False, constraints=[Check("name != ''")])
    semester = IntegerField(null=False, constraints=[Check("semester BETWEEN 1 AND 12")])
    is_active = BooleanField(default=True)


class Hours(BaseModel):
    id = AutoField()
    subject = ForeignKeyField(Subject, backref='hours', on_delete='CASCADE', null=False, unique=True)
    lecture_hours = IntegerField(default=0, null=False, constraints=[Check("lecture_hours >= 0")])
    practice_hours = IntegerField(default=0, null=False, constraints=[Check("practice_hours >= 0")])
    is_active = BooleanField(default=True)


class Assessment(BaseModel):
    id = AutoField()
    subject = ForeignKeyField(Subject, backref='assessments', on_delete='CASCADE', null=False)
    type = CharField(null=False, constraints=[Check("type IN ('exam', 'zachet')")])
    is_active = BooleanField(default=True)


def init_db():
    with db:
        db.create_tables([CurriculumPlan, Subject, Hours, Assessment])


if __name__ == "__main__":
    init_db()