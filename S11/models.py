import os
from peewee import (
    SqliteDatabase,
    Model,
    IntegerField,
    CharField,
    TextField,
)

# Путь к файлу БД
DB_PATH = os.path.join(os.path.dirname(__file__), "discipline.db")

# Инициализация подключения к БД
db = SqliteDatabase(DB_PATH, pragmas={
    "foreign_keys": 1,   # Включаем поддержку внешних ключей
    "journal_mode": "wal",  # Улучшаем производительность
})


class BaseModel(Model):
    """Базовая модель с привязкой к БД."""
    class Meta:
        database = db


class Discipline(BaseModel):
 
   # Модель дисциплины.

    id = IntegerField(primary_key=True)
    name = CharField(max_length=255, null=False)
    code = CharField(max_length=50, unique=True, null=False)
    specialty_id = IntegerField(null=False)

    class Meta:
        table_name = "discipline"
        indexes = (
            (('name', 'code', 'specialty_id'), True),
        )

def initialize_database():
    """
    Инициализация базы данных.
    Создает таблицы, если они не существуют.
    Безопасна для многократного вызова.
    """
    db.connect()
    db.create_tables([Discipline])
    print(f"База данных инициализирована: {DB_PATH}")
    print(f"Таблицы созданы: Discipline")
    db.close()


if __name__ == "__main__":
    """
    Точка входа для инициализации БД.
    Запуск: python models.py
    """
    initialize_database()
    print("DA")