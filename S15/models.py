from peewee import Model, IntegerField, ForeignKeyField, BooleanField
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase('load_assignment.db')


class BaseModel(Model):
    class Meta:
        database = db


class Teacher(BaseModel):
    id = IntegerField(primary_key=True)


class Discipline(BaseModel):
    id = IntegerField(primary_key=True)


class Group(BaseModel):
    id = IntegerField(primary_key=True)


class LoadAssignment(BaseModel):
    id = IntegerField(primary_key=True)
    teacher_id = ForeignKeyField(Teacher, backref='assignments')
    discipline_id = ForeignKeyField(Discipline, backref='assignments')
    group_id = ForeignKeyField(Group, backref='assignments')
    is_active = BooleanField(default=True)


def init_db():
    db.create_tables([Teacher, Discipline, Group, LoadAssignment])


if __name__ == "__main__":
    init_db()
