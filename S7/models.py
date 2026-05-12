"""База данных Group Service (Вариант №7)"""
from peewee import (
    Model,
    CharField,
    IntegerField,
    BooleanField,
    AutoField,
    SqliteDatabase,
    Check
)

# Подключение к базе данных твоего сервиса
DB = SqliteDatabase('group_service_s7.db')


class BaseModel(Model):
    """Базовая модель"""
    class Meta:
        database = DB


class Group(BaseModel):
    """Класс учебной группы колледжа"""
    id = AutoField()
    name = CharField(unique=True, null=False)
    
    # Ограничение по году (>= 2000) 
    formation_year = IntegerField(
        null=False, 
        constraints=[Check('formation_year >= 2000')]
    )
    
    # Ограничение по базе (9 или 11 класс)
    education_base = IntegerField(
        null=False, 
        constraints=[Check('education_base IN (9, 11)')]
    )
    
    # True — группа активна, False — выпустилась.
    is_active = BooleanField(default=True, null=False)
    
    # Внешний ID куратора
    curator_id = IntegerField(null=False)

    class Meta:
        table_name = 'groups'


def create_tables():
    """Создаёт таблицы базы данных"""
    with DB:
        DB.create_tables([Group])


if __name__ == "__main__":
    create_tables()
    print("S7 Group Service: БД успешно инициализирована.")