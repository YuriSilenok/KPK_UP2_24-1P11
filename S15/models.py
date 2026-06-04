import datetime
from peewee import (
    Model,
    SqliteDatabase,
    PrimaryKeyField,
    IntegerField,
    CharField,
    DateField,
    ForeignKeyField
)

# Инициализация базы данных SQLite
db = SqliteDatabase('load_assignment.db')


class BaseModel(Model):
    class Meta:
        database = db


class AcademicTerm(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=100)  # Например, "2025-2026, Осенний семестр"
    start_date = DateField()
    end_date = DateField()

    class Meta:
        table_name = 'academic_terms'


class LoadAssignment(BaseModel):
    id = PrimaryKeyField()
    # Храним только ID внешних сущностей, так как их данные лежат в других сервисах
    teacher_id = IntegerField()
    subject_id = IntegerField()
    group_id = IntegerField()
    
    # Связь с периодом обучения внутри этого сервиса
    term = ForeignKeyField(AcademicTerm, backref='assignments', on_delete='RESTRICT')
    
    hours = IntegerField(default=0)  # Количество часов на дисциплину
    assignment_type = CharField(max_length=50)  # Лекции, Практика, Лабораторные

    class Meta:
        table_name = 'load_assignments'


def init_db():
    """Функция для создания таблиц в базе данных."""
    db.connect()
    db.create_tables([AcademicTerm, LoadAssignment], safe=True)
    db.close()
    print("База данных Load Assignment Service успешно инициализирована.")


if __name__ == "__main__":
    init_db()
