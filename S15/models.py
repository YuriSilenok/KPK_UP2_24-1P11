from peewee import Model, IntegerField, BooleanField
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase('load_assignment.db')


class BaseModel(Model):
    class Meta:
        database = db


class LoadAssignment(BaseModel):
    id = IntegerField(primary_key=True)
    teacher_id = IntegerField()  # ссылка на внешний сервис (Teacher)
    discipline_id = IntegerField()  # ссылка на внешний сервис (Discipline)
    group_id = IntegerField()  # ссылка на внешний сервис (Group)
    is_active = BooleanField(default=True)


def init_db():
    db.create_tables([LoadAssignment])


if __name__ == "__main__":
    init_db()
