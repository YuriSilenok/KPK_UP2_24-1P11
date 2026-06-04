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
    # Разрешаем null=True для соответствия необязательному статусу параметров в PATCH
    title = CharField(null=True)
    file_path = CharField(null=True, unique=True)
    
    # Ограничение формата версии (длина строки от 3 символов, например "1.0")
    version = CharField(
        null=True, 
        default="1.0",
        constraints=[Check("length(version) >= 3 AND version LIKE '%.%'")]
    )
    
    # Автоматический статус при создании (по умолчанию False означает активна)
    is_deleted = BooleanField(default=False, null=False)
    created_at = DateTimeField(default=datetime.datetime.now, null=False)

    def delete_instance(self, *args, **kwargs):
        """Мягкое удаление программы и ее назначений"""
        with DB.atomic():
            self.is_deleted = True
            self.save()
            # Соответствие имени поля work_program
            ProgramAssignment.update(is_deleted=True).where(ProgramAssignment.work_program == self.id).execute()
        return True

    class Meta:
        table_name = 'work_programs'
        # Составная уникальность: название + версия
        indexes = (
            (('title', 'version'), True),
        )


class ProgramAssignment(BaseModel):
    """Связь программ с внешними ID специальностей и дисциплин (3НФ)"""
    assignment_id = AutoField()
    
    # Убран on_delete='CASCADE', имя поля строго согласуется с work_program_id
    work_program = ForeignKeyField(
        WorkProgram,
        backref='assignments',
        on_delete='RESTRICT',
        column_name='work_program_id'
    )
    specialty_id = IntegerField(null=False)
    discipline_id = IntegerField(null=False)
    is_deleted = BooleanField(default=False, null=False)

    class Meta:
        table_name = 'program_assignments'
        # Составная уникальность: программа + внешняя специальность + внешняя дисциплина
        indexes = (
            (('work_program', 'specialty_id', 'discipline_id'), True),
        )


def create_tables():
    """Создаёт таблицы базы данных"""
    with DB:
        DB.create_tables([WorkProgram, ProgramAssignment])


if __name__ == "__main__":
    create_tables()
    print("S13 Work Program Service: БД успешно инициализирована.")
