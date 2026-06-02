from peewee import *

db = SqliteDatabase('room_service.db')


class BaseModel(Model):
    class Meta:
        database = db


class RoomType(BaseModel):
    title = CharField(
        max_length=100,
        unique=True,
        null=False
    )


class Room(BaseModel):
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
        on_delete='CASCADE',
        null=False
    )

    is_active = BooleanField(
        default=True,
        null=False
    )

    class Meta:
        indexes = (
            (
                ('number', 'campus_id'),
                True
            ),
        )


def initialize_database():
    db.connect()
    db.create_tables([RoomType, Room])

    default_room_types = [
        'Classroom',
        'Laboratory',
        'Workshop'
    ]

    for title in default_room_types:
        RoomType.get_or_create(title=title)

    db.close()


if __name__ == '__main__':
    initialize_database()