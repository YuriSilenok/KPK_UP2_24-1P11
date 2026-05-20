from peewee import *


# Подключение SQLite базы данных
db = SqliteDatabase('room_service_s17.db')


class BaseModel(Model):
    """
    Базовая модель.
    """

    class Meta:
        database = db


class RoomType(BaseModel):
    """
    Тип аудитории.
    """

    title = CharField(
        max_length=100,
        unique=True,
        null=False
    )


class Room(BaseModel):
    """
    Аудитория.
    """

    number = CharField(
        max_length=20,
        null=False
    )

    floor = IntegerField(
        null=False,
        constraints=[Check('floor >= 0')]
    )

    campus_id = IntegerField(
    null=False
    )

    capacity = IntegerField(
        null=False,
        constraints=[Check('capacity > 0')]
    )

    room_type = ForeignKeyField(
        RoomType,
        backref='rooms',
        null=False
    )

    # Логическое удаление
    is_active = BooleanField(
        default=False
    )

    class Meta:
        indexes = (
            (('number', 'building'), True),
        )


def init_db():
    """
    Инициализация базы данных.
    """

    db.connect(reuse_if_open=True)

    db.create_tables([
        RoomType,
        Room
    ], safe=True)

    # Начальное заполнение справочника типов аудиторий
    # Используется для базовой инициализации сервиса
    if RoomType.select().count() == 0:
        RoomType.create(title='Classroom')
        RoomType.create(title='Laboratory')
        RoomType.create(title='Workshop')

    db.close()


if __name__ == '__main__':
    init_db()
    print('Room Service (S17): database initialized successfully.')