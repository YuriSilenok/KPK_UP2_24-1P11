from peewee import *
from datetime import datetime

db = SqliteDatabase('student_movement.db')


class BaseModel(Model):
    class Meta:
        database = db


class MovementType(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50, unique=True)

    class Meta:
        table_name = 'movement_types'


class StudentMovement(BaseModel):
    id = PrimaryKeyField()
    student_id = IntegerField()
    movement_type_id = ForeignKeyField(MovementType, backref='movements')
    from_group_id = IntegerField(null=True)
    to_group_id = IntegerField(null=True)
    movement_date = DateField()
    reason = CharField(max_length=500)
    order_number = CharField(max_length=50, unique=True)
    created_by = CharField(max_length=100)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(null=True)
    is_active = BooleanField(default=True)

    class Meta:
        table_name = 'student_movements'


def check_time_overlap(student_id, movement_date, exclude_id=None):
    """
    Проверка пересечения интервалов движения для одного студента.
    Записи со статусом is_active = false (cancelled) исключаются из проверки.
    """
    query = StudentMovement.select().where(
        (StudentMovement.student_id == student_id) &
        (StudentMovement.movement_date == movement_date) &
        (StudentMovement.is_active == True)
    )
    if exclude_id:
        query = query.where(StudentMovement.id != exclude_id)
    return query.count() == 0


def init_db():
    db.connect()
    db.create_tables([MovementType, StudentMovement], safe=True)
    db.close()
    print("✅ База данных создана!")


if __name__ == '__main__':
    init_db()