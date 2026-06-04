"""Модуль моделей базы данных для Work Program Service (Вариант №13)"""
import datetime
from peewee import (
    Model,
    CharField,
    IntegerField,
    BooleanField,
    AutoField,
    DateTimeField,
    SqliteDatabase,
    ForeignKeyField,
    Check
)

# Подключение к локальной базе данных SQLite с поддержкой внешних ключей
DB = SqliteDatabase('work_programs_s13.db', pragmas={'foreign_keys': 1})


class BaseModel(Model):
    """Базовая модель для настройки подключения"""
    class Meta:
        database = DB


class WorkProgram(BaseModel):
    """Класс рабочей программы дисциплин колледжа"""
    id = AutoField()
    title = CharField(null=False)
    file_path = CharField(null=False, unique=True)
    
    # Задан явный индекс для оптимизации запросов фильтрации и ограничение формата
    version = CharField(
        null=False, 
        default="1.0",
        index=True,
        constraints=[Check("length(version) >= 3 AND version LIKE '%.%'")]
    )
    
    is_deleted = BooleanField(default=False, null=False)
    created_at = DateTimeField(default=datetime.datetime.now, null=False)

    class Meta:
        table_name = 'work_programs'
        # Составная уникальность: название + версия
        indexes = (
            (('title', 'version'), True),
        )


class ProgramAssignment(BaseModel):
    """Связь программ с внешними ID специальностей и дисциплин (3НФ)"""
    assignment_id = AutoField()
    
    work_program = ForeignKeyField(
        WorkProgram,
        backref='assignments',
        column_name='work_program_id'
    )
    specialty_id = IntegerField(null=False)
    discipline_id = IntegerField(null=False)
    is_deleted = BooleanField(default=False, null=False)

    class Meta:
        table_name = 'program_assignments'
        # Исправлено: в индексе используется точное имя колонки 'work_program_id'
        indexes = (
            (('work_program_id', 'specialty_id', 'discipline_id'), True),
        )


def create_tables():
    """Создаёт таблицы базы данных"""
    with DB:
        DB.create_tables([WorkProgram, ProgramAssignment])


if __name__ == "__main__":
    create_tables()
    print("S13 Work Program Service: БД успешно инициализирована.")
