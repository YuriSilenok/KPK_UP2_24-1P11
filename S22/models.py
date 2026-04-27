"""Timeslot Service"""

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
    """Справочник дней недели (внутренний)"""

    id = AutoField()
    day_number = IntegerField(unique=True, null=False)  # 1=Пн .. 7=Вс

    class Meta:
        db_table = "day_of_week"


class Schedule(BaseModel):
    """
    Расписание звонков для корпуса и дня недели.
    Без флага сокращённого дня.
    """

    id = AutoField()
    external_building_id = IntegerField(null=False)  # заглушка Campus Service
    day_of_week = ForeignKeyField(DayOfWeek, backref="schedules", null=False)

    class Meta:
        indexes = ((("external_building_id", "day_of_week"), True),)


class Timeslot(BaseModel):
    """
    Временной слот – может быть парой или переменой.
    Порядок задаётся order_number.
    """

    id = AutoField()
    schedule = ForeignKeyField(
        Schedule, backref="timeslots", on_delete="CASCADE", null=False
    )
    order_number = IntegerField(null=False)  # порядковый номер события (1,2,3,...)
    is_lesson = BooleanField(null=False)  # True = пара, False = перемена
    start_time = TimeField(null=False)
    end_time = TimeField(null=False)

    class Meta:
        indexes = ((("schedule", "order_number"), True),)


def verify_building_exists(building_id: int) -> bool:
    """Заглушка для Campus Service"""
    return 1 <= building_id <= 10


def create_tables():
    """Создаёт таблицы и заполняет дни недели"""
    with DB:
        DB.create_tables([DayOfWeek, Schedule, Timeslot])
        if not DayOfWeek.select().exists():
            for i in range(1, 8):
                DayOfWeek.create(day_number=i)


if __name__ == "__main__":
    create_tables()
