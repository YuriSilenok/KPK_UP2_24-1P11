from peewee import *


db = SqliteDatabase('room_service_s17.db')


class BaseModel(Model):
    """
    Базовая модель для всех таблиц.
    """

    class Meta:
        database = db


class RoomType(BaseModel):
    """
    Тип аудитории.

    Примеры:
    - Кабинет
    - Лаборатория
    - Мастерская
    """

    title = CharField(
        unique=True,
        null=False
    )


class Room(BaseModel):
    """
    Аудитория.
    """

    number = CharField(
        null=False
    )

    floor = IntegerField(
        null=False,
        constraints=[Check('floor >= 0')]
    )

    building = CharField(
        null=False
    )

    capacity = IntegerField(
        null=False,
        constraints=[Check('capacity > 0')]
    )

    room_type = ForeignKeyField(
        RoomType,
        backref='rooms',
        null=False,
        on_delete='RESTRICT'
    )

    # Логическое удаление
    is_deleted = BooleanField(
        default=False
    )

    class Meta:
        indexes = (
            # Уникальный номер аудитории внутри корпуса
            (("number", "building"), True),
        )


# Инициализация базы данных

def init_db():
    db.connect(reuse_if_open=True)

    db.create_tables([
        RoomType,
        Room
    ], safe=True)

    # Заполнение справочника типов аудиторий
    if RoomType.select().count() == 0:
        RoomType.create(title='Кабинет')
        RoomType.create(title='Лаборатория')
        RoomType.create(title='Мастерская')

    db.close()


# Точка входа
if __name__ == '__main__':
    init_db()
    print('Room Service (S17): база данных успешно создана.')