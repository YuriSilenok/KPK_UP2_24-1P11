from peewee import *

db = SqliteDatabase('curriculum.db')


class BaseModel(Model):
    class Meta:
        database = db


class Group(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField(max_length=100, unique=True, null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'group'


class Discipline(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True, null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'discipline'


class Semester(BaseModel):
    id = AutoField(primary_key=True)
    semester_number = IntegerField(null=False, constraints=[Check('semester_number BETWEEN 1 AND 8')])
    academic_year = CharField(max_length=9, null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'semester'
        constraints = [SQL('UNIQUE(semester_number, academic_year)')]


class Curriculum(BaseModel):
    id = AutoField(primary_key=True)
    group = ForeignKeyField(Group, backref='curriculums', on_delete='CASCADE', null=False)
    discipline = ForeignKeyField(Discipline, backref='curriculums', on_delete='CASCADE', null=False)
    semester = ForeignKeyField(Semester, backref='curriculums', on_delete='RESTRICT', null=False)
    theory_hours = IntegerField(null=False, constraints=[Check('theory_hours >= 0')])
    practice_hours = IntegerField(null=False, constraints=[Check('practice_hours >= 0')])
    assessment_form = CharField(max_length=10, null=False, constraints=[Check("assessment_form IN ('exam', 'credit')")])
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'curriculum'
        constraints = [SQL('UNIQUE(group_id, discipline_id, semester_id)')]


def init_db():
    db.connect()
    db.create_tables([Group, Discipline, Semester, Curriculum], safe=True)
    db.close()


if __name__ == "__main__":
    init_db()