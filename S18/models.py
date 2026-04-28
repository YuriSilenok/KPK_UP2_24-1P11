from peewee import *
import sqlite3

db = SqliteDatabase('room_equipment.db')

class BaseModel(Model):
    class Meta:
        database = db

class EquipmentType(BaseModel):
    name = CharField(max_length=100, unique=True)  # projector, computers, machines, boards, other

class Equipment(BaseModel):
    name = CharField(max_length=100, constraints=[Check('length(name) >= 1 AND length(name) <= 100')])
    type_id = ForeignKeyField(EquipmentType, backref='equipment', field='id', on_delete='RESTRICT')
    room_id = IntegerField()  # внешний ключ к Room Service, но здесь без FK
    status = CharField(max_length=20, default='active', constraints=[Check("status IN ('active', 'broken', 'maintenance')")])
    inventory_number = CharField(max_length=50, unique=True, null=True)  # может быть NULL
    description = TextField(default='')

    class Meta:
        indexes = (
            (('room_id', 'name'), True),  # уникальная комбинация
        )

def init_db():
    db.connect()
    # Создаём таблицы в правильном порядке (сначала EquipmentType, затем Equipment)
    db.create_tables([EquipmentType, Equipment], safe=True)
    
    # Заполняем таблицу типов начальными данными, если она пуста
    if EquipmentType.select().count() == 0:
        default_types = ['projector', 'computers', 'machines', 'boards', 'other']
        for type_name in default_types:
            EquipmentType.create(name=type_name)
    
    db.close()

# точка входа для инициализации
if __name__ == '__main__':
    init_db()
    print("Database initialized for Room Equipment Service")