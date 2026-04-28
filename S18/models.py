from peewee import *
import sqlite3

db = SqliteDatabase('room_equipment.db')

class BaseModel(Model):
    class Meta:
        database = db

class EquipmentType(BaseModel):
    name = CharField(max_length=100, unique=True)  # projector, computers, machines, boards, other

class EquipmentStatus(BaseModel):
    name = CharField(max_length=50, unique=True)  # active, broken, maintenance
    description = TextField(default='')

class Equipment(BaseModel):
    name = CharField(max_length=100, constraints=[Check('length(name) >= 1 AND length(name) <= 100')])
    type_id = ForeignKeyField(EquipmentType, backref='equipment', field='id', on_delete='RESTRICT')
    room_id = IntegerField()  # внешний ключ к Room Service, но здесь без FK
    status_id = ForeignKeyField(EquipmentStatus, backref='equipment', field='id', on_delete='RESTRICT', default=1)
    inventory_number = CharField(max_length=50, unique=True, null=True)  # может быть NULL
    description = TextField(default='')

    class Meta:
        indexes = (
            (('room_id', 'name'), True),  # уникальная комбинация
        )

def init_db():
    db.connect()
    # Создаём таблицы в правильном порядке
    db.create_tables([EquipmentType, EquipmentStatus, Equipment], safe=True)
    
    # Заполняем таблицу типов начальными данными, если она пуста
    if EquipmentType.select().count() == 0:
        default_types = ['projector', 'computers', 'machines', 'boards', 'other']
        for type_name in default_types:
            EquipmentType.create(name=type_name)
    
    # Заполняем таблицу статусов начальными данными, если она пуста
    if EquipmentStatus.select().count() == 0:
        default_statuses = [
            ('active', 'Оборудование работает исправно'),
            ('broken', 'Оборудование сломано, требует ремонта'),
            ('maintenance', 'Оборудование на обслуживании/ремонте')
        ]
        for status_name, status_desc in default_statuses:
            EquipmentStatus.create(name=status_name, description=status_desc)
    
    db.close()

# точка входа для инициализации
if __name__ == '__main__':
    init_db()
    print("Database initialized for Room Equipment Service")