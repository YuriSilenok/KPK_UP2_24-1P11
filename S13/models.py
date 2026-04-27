from peewee import *
import datetime

# Подключение к базе данных SQLite
db = SqliteDatabase('work_programs.db')

class BaseModel(Model):
    class Meta:
        database = db

class WorkProgram(BaseModel):
    """Сущность: Рабочая программа"""
    title = CharField(null=False)  # Название программы
    file_path = CharField(null=False)  # Путь к файлу программы
    version = CharField(null=False, default="1.0")
    created_at = DateTimeField(default=datetime.datetime.now, null=False)

class Specialty(BaseModel):
    """Сущность: Специальность (из смежного сервиса)"""
    code = CharField(unique=True, null=False) # Например, '09.02.07'
    name = CharField(null=False)

class ProgramAssignment(BaseModel):
    """Транзитивная таблица для связи Многие-ко-многим"""
    program = ForeignKeyField(WorkProgram, backref='assignments', null=False)
    specialty = ForeignKeyField(Specialty, backref='programs', null=False)
    discipline_id = IntegerField(null=False) # ID дисциплины

    class Meta:
        # Ограничение: нельзя привязать одну и ту же программу к одной специальности дважды
        indexes = (
            (('program', 'specialty', 'discipline_id'), True),
        )

def init_db():
    """Функция инициализации базы данных"""
    db.connect()
    db.create_tables([WorkProgram, Specialty, ProgramAssignment])
    print("Сервис рабочих программ: БД инициализирована.")

if __name__ == "__main__":
    init_db()




