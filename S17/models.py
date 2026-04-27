from peewee import *

db = SqliteDatabase('room_service_s7.db')

class BaseModel(Model):
    class Meta:
        database = db

class RoomType(BaseModel):
    """Тип помещения: Кабинет, Лаборатория, Мастерская"""
    title = CharField(unique=True, null=False)

class Room(BaseModel):
    """Сущность Аудитория"""
    number = CharField(null=False)  # Номер кабинета
    floor = IntegerField(null=False) # Этаж
    building = CharField(null=False) # Корпус
    capacity = IntegerField(null=False) # Вместимость
    # Связь с типом помещения (3НФ)
    room_type = ForeignKeyField(RoomType, backref='rooms', null=False)

def init_db():
    db.connect()
    db.create_tables([RoomType, Room], safe=True)
    
    # Наполнение справочников
    if RoomType.select().count() == 0:
        RoomType.create(title="Кабинет")
        RoomType.create(title="Лаборатория")
        RoomType.create(title="Мастерская")

if __name__ == "__main__":
    init_db()
    print("Сервис аудиторий (S7): БД успешно инициализирована.")
