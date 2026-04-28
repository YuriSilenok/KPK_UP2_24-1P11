"""Timeslot Service — без отдельной таблицы дней недели"""

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


class Schedule(BaseModel):
    """
    Расписание звонков для группы/подгруппы в конкретный день недели.
    """

    id = AutoField()
    group_id = IntegerField(null=False)  # заглушка Group Service
    subgroup_id = IntegerField(null=False)  # 0 = основная группа, >0 подгруппа
    day_of_week = IntegerField(null=False)

    class Meta:
        indexes = ((("group_id", "subgroup_id", "day_of_week"), True),)


class Timeslot(BaseModel):
    """
    Временной слот – занятие или перемена.
    """

    id = AutoField()
    schedule = ForeignKeyField(
        Schedule, backref="timeslots", on_delete="CASCADE", null=False
    )
    order_number = IntegerField(null=False)
    is_lesson = BooleanField(null=False)  # True = занятие, False = перемена
    start_time = TimeField(null=False)
    end_time = TimeField(null=False)

    class Meta:
        indexes = ((("schedule", "order_number"), True),)


def verify_group_exists(group_id: int) -> bool:
    """Заглушка для Group Service"""
    return 1 <= group_id <= 20


def verify_subgroup_exists(subgroup_id: int) -> bool:
    """Заглушка для Subgroup Service: 0 – группа, 1..50 – подгруппа"""
    return 0 <= subgroup_id <= 50


def create_tables():
    """Создаёт таблицы (без DayOfWeek)"""
    with DB:
        DB.create_tables([Schedule, Timeslot])


if __name__ == "__main__":
    create_tables()
