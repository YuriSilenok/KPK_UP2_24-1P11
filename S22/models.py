"""Timeslot Service"""

from datetime import time
from peewee import (
    AutoField,
    BooleanField,
    IntegerField,
    Model,
    SqliteDatabase,
    TimeField,
)

DB = SqliteDatabase("timeslot.db")


class BaseModel(Model):
     """Базовая модель"""
    
    class Meta:
        database = DB


class Schedule(BaseModel):
    """
    Расписание звонков для конкретной комбинации:
    - внешний id корпуса (из Campus Service)
    - внешний id дня недели (из DayOfWeek Service)
    - тип дня (обычный/сокращённый)
    """

    id = AutoField()
    external_building_id = IntegerField(null=False)  # заглушка Campus Service
    external_day_of_week_id = IntegerField(null=False)  # заглушка DayOfWeek Service
    is_shortened = BooleanField(default=False, null=False)

    class Meta:
        indexes = (
            (("external_building_id", "external_day_of_week_id", "is_shortened"), True),
        )


class Timeslot(BaseModel):
    """Привязка к расписанию, номер пары, время"""

    id = AutoField()
    schedule = ForeignKeyField(
        Schedule, backref="timeslots", on_delete="CASCADE", null=False
    )
    pair_number = IntegerField(null=False)
    start_time = TimeField(null=False)
    end_time = TimeField(null=False)

    class Meta:
        indexes = ((("schedule", "pair_number"), True),)


def verify_building_exists(building_id: int) -> bool:
    """Campus Service"""
    # Имитация существования с id 1..10
    return 1 <= building_id <= 10


def verify_day_of_week_exists(day_of_week_id: int) -> bool:
    """DayOfWeek Service"""
    # id 1..7 соответствуют понедельник..воскресенье
    return 1 <= day_of_week_id <= 7


def create_tables():
    """Создаёт таблицы в БД"""
    with DB:
        DB.create_tables([Schedule, Timeslot])


if __name__ == "__main__":
    create_tables()
