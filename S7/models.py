from peewee import *

# Подключение к локальной БД
db = SqliteDatabase('group_service_s7.db')

class BaseModel(Model):
    class Meta:
        database = db

class GroupStatus(BaseModel):
    """Справочник: Активна / Выпустилась"""
    title = CharField(unique=True, null=False)

    class Meta:
        table_name = 'statusgroup'

class Group(BaseModel):
    """Сущность Учебная группа"""
    name = CharField(unique=True, null=False)
    formation_year = IntegerField(null=False)
    education_base = IntegerField(null=False)  # 9 или 11 класс
    status = ForeignKeyField(GroupStatus, backref='groups', null=False)
    curator_id = IntegerField(null=False)      # Внешний ID

    class Meta:
        table_name = 'groups'

def init_db():
    """Функция инициализации базы данных"""
    db.connect()
    # safe=True не выдаст ошибку, если таблицы уже есть
    db.create_tables([GroupStatus, Group], safe=True)
    
    # Заполнение справочника статусов, если он пуст
    if GroupStatus.select().count() == 0:
        GroupStatus.create(title="Активна")
        GroupStatus.create(title="Выпустилась")

if __name__ == "__main__":
    init_db()
    print("S7 Group Service: БД успешно инициализирована.")
