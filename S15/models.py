from peewee import (
    Model,
    SqliteDatabase,
    PrimaryKeyField,
    IntegerField,
    BooleanField
)

db = SqliteDatabase('load_assignment.db')


class BaseModel(Model):
    class Meta:
        database = db


class LoadAssignment(BaseModel):
    id = PrimaryKeyField()
    teacher_id = IntegerField()
    discipline_id = IntegerField()
    group_id = IntegerField()
    is_active = BooleanField(default=True)

    class Meta:
        table_name = 'load_assignments'
        indexes = (
            (('teacher_id', 'discipline_id', 'group_id'), True),
        )


def init_db():
    db.connect()
    db.create_tables([LoadAssignment], safe=True)
    db.close()
    print("База данных Load Assignment Service успешно инициализирована.")


if __name__ == "__main__":
    init_db()
