from peewee import *

# Подключение к БД
db = SqliteDatabase('group_service_s7.db')

class BaseModel(Model):
    class Meta:
        database = db

class GroupStatus(BaseModel):
    """Справочник: Активна / Выпустилась"""
    title = CharField(unique=True, null=False)

class Group(BaseModel):
    """Сущность Учебная группа"""
    name = CharField(unique=True, null=False)           # Номер группы
    formation_year = IntegerField(null=False)          # Год поступления
    education_base = IntegerField(null=False)          # 9 или 11 класс
    status = ForeignKeyField(GroupStatus, backref='groups', null=False)
    curator_id = IntegerField(null=False)              # ID из сервиса профилей

def init_db():
    """Инициализация таблиц"""
    db.connect()
    db.create_tables([GroupStatus, Group], safe=True)
    
    # Заполнение справочника статусов
    if GroupStatus.select().count() == 0:
        GroupStatus.create(title="Активна")
        GroupStatus.create(title="Выпустилась")

if __name__ == "__main__":
    init_db()
    print("S7 Group Service: БД успешно инициализирована.")
