"""Timeslot Service without fake dependencies"""

from datetime import time

from peewee import (
    AutoField,
    BooleanField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TimeField,
)

DB = SqliteDatabase("timeslot.db")


class BaseModel(Model):
    class Meta:
        database = DB


class DayOfWeek(BaseModel):
    """Справочник дней недели."""

    id = AutoField()
    name = IntegerField(unique=True, null=False)  # 1=Monday .. 7=Sunday
    # можно добавить order_index, но name уже порядок

    class Meta:
        db_table = "day_of_week"


class Schedule(BaseModel):
    """
    Расписание звонков для конкретной комбинации:
    - внешний id корпуса (из Campus Service)
    - внутренний day_of_week_id
    - тип дня (обычный/сокращённый)
    """

    id = AutoField()
    external_building_id = IntegerField(null=False)  # заглушка Campus Service
    day_of_week = ForeignKeyField(DayOfWeek, backref="schedules", null=False)
    is_shortened = BooleanField(default=False, null=False)

    class Meta:
        indexes = ((("external_building_id", "day_of_week", "is_shortened"), True),)


class Timeslot(BaseModel):
    """Временной слот (пара)"""

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
    """Заглушка для Campus Service (реальный сервис существует)"""
    return 1 <= building_id <= 10


def create_tables():
    """Создаёт таблицы в БД и заполняет дни недели"""
    with DB:
        DB.create_tables([DayOfWeek, Schedule, Timeslot])
        if not DayOfWeek.select().exists():
            for i in range(1, 8):
                DayOfWeek.create(name=i)


if __name__ == "__main__":
    create_tables()
