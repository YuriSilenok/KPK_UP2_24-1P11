from peewee import *

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
    movement_date = DateField(constraints=[Check("movement_date <= date('now')")])
    reason = CharField(max_length=500)
    order_number = CharField(max_length=50, unique=True)
    created_by = CharField(max_length=100)
    is_active = BooleanField(default=True)

    class Meta:
        table_name = 'student_movements'


def init_db():
    db.connect()
    db.create_tables([MovementType, StudentMovement], safe=True)
    db.close()
    print("✅ База данных создана!")


if __name__ == '__main__':
    init_db()