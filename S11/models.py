import os
from peewee import (
    SqliteDatabase,
    Model,
    IntegerField,
    CharField,
    ForeignKeyField,
)

# Путь к файлу БД
DB_PATH = os.path.join(os.path.dirname(__file__), "discipline.db")

# Инициализация подключения к БД
db = SqliteDatabase(DB_PATH, pragmas={
    "foreign_keys": 1,
    "journal_mode": "wal",  
})


class BaseModel(Model):
    """Базовая модель с привязкой к БД."""
    class Meta:
        database = db


class Discipline(BaseModel):
    """Модель дисциплины."""
    id = IntegerField(primary_key=True)
    name = CharField(max_length=255, unique=True, null=False)
    code = CharField(max_length=50, unique=True, null=False)

    class Meta:
        table_name = "discipline"

class Specialty(BaseModel):
    """Модель специальности."""
    id = IntegerField(primary_key=True)
    name = CharField(max_length=255, unique=True, null=False)
    code = CharField(max_length=50, unique=True, null=False)

    class Meta:
        table_name = "specialty"


class DisciplinesSpecialty(BaseModel):
    """Связующая таблица для связи дисциплин и специальностей (many-to-many)."""
    discipline = ForeignKeyField(Discipline, backref='specialties', on_delete='CASCADE', null=False)
    specialty = ForeignKeyField(Specialty, backref='disciplines', on_delete='CASCADE', null=False)

    class Meta:
        table_name = "disciplinesspecialty"
        primary_key = False  # Составной ключ из двух полей
        indexes = (
            (('discipline', 'specialty'), True),  # Уникальная пара (discipline_id, specialty_id)
        )


def initialize_database():
    """
    Инициализация базы данных.
    Создает таблицы, если они не существуют.
    Безопасна для многократного вызова.
    """
    db.connect()
    db.create_tables([Discipline, Specialty, DisciplinesSpecialty])
    print(f"База данных инициализирована: {DB_PATH}")
    print(f"Таблицы созданы: Discipline, Specialty, DisciplinesSpecialty")
    db.close()


if __name__ == "__main__":
    initialize_database()
    print("Инициализация завершена")