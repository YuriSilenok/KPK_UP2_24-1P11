"""База данных Group Service"""
from peewee import (
    Model,
    CharField,
    IntegerField,
    ForeignKeyField,
    AutoField,
    SqliteDatabase,
    Check
)

DB = SqliteDatabase('group_service_s7.db')

class BaseModel(Model):
    """Базовая модель"""
    class Meta:
        database = DB

class GroupStatus(BaseModel):
    """Класс статуса группы"""
    id = AutoField()
    title = CharField(unique=True, null=False)

    class Meta:
        table_name = 'statusgroup'

class Group(BaseModel):
    """Класс учебной группы"""
    id = AutoField()
    name = CharField(unique=True, null=False)
    formation_year = IntegerField(
        null=False, 
        constraints=[Check('formation_year >= 2000')]
    )
    education_base = IntegerField(
        null=False, 
        constraints=[Check('education_base IN (9, 11)')]
    )
    status = ForeignKeyField(
        GroupStatus, 
        backref='groups', 
        null=False, 
        default=1
    )
    curator_id = IntegerField(null=False)

    class Meta:
        table_name = 'groups'

def create_tables():
    """Создаёт таблицы и заполняет справочник"""
    with DB:
        DB.create_tables([GroupStatus, Group])
        if GroupStatus.select().count() == 0:
            GroupStatus.create(title="Активна")
            GroupStatus.create(title="Выпустилась")

if __name__ == "__main__":
    create_tables()
    print("S7 Group Service: БД успешно инициализирована.")