"""Модуль моделей базы данных."""
import datetime
from peewee import SqliteDatabase, Model, CharField, DateTimeField, \
    ForeignKeyField, IntegerField

db = SqliteDatabase('work_programs.db')


class BaseModel(Model):
    """Базовая модель."""

    class Meta:
        database = db


class WorkProgram(BaseModel):
    """Модель рабочих программ."""

    title = CharField(null=False)
    file_path = CharField(null=False)
    version = CharField(null=False, default="1.0")
    created_at = DateTimeField(default=datetime.datetime.now, null=False)

    class Meta:
        indexes = (
            (('title', 'version'), True),
        )


class ProgramAssignment(BaseModel):
    """Модель назначений."""

    program = ForeignKeyField(
        WorkProgram,
        backref='assignments',
        on_delete='CASCADE'
    )
    specialty_id = IntegerField(null=False)
    discipline_id = IntegerField(null=False)

    class Meta:
        indexes = (
            (('program', 'specialty_id', 'discipline_id'), True),
        )


def init_db():
    """Инициализация БД."""
    db.connect()
    db.create_tables([WorkProgram, ProgramAssignment])
    print("БД Work Program Service инициализирована.")


if __name__ == "__main__":
    init_db()