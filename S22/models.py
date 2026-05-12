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


class Schedule(BaseModel):
    """
    Расписание звонков для группы/подгруппы в конкретный день недели.
    """

    id = AutoField()
    group_id = IntegerField()  # заглушка Group Service
    subgroup_id = IntegerField()  # 0 = основная группа, >0 подгруппа
    day_of_week = IntegerField()

    class Meta:
        indexes = ((("group_id", "subgroup_id", "day_of_week"), True),)


class Timeslot(BaseModel):
    """
    Временной слот – занятие или перемена.
    """

    id = AutoField()
    schedule = ForeignKeyField(Schedule, backref="timeslots", on_delete="CASCADE")
    order_number = IntegerField()
    is_lesson = BooleanField()  # True = занятие, False = перемена
    start_time = TimeField()
    end_time = TimeField()

    class Meta:
        indexes = ((("schedule", "order_number"), True),)


def create_tables():
    """Создаёт таблицы (без DayOfWeek)"""
    with DB:
        DB.create_tables([Schedule, Timeslot])


if __name__ == "__main__":
    create_tables()
