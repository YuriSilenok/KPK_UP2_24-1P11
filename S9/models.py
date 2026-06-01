from peewee import *

db = SqliteDatabase('student_movement.db')


class BaseModel(Model):
    class Meta:
        database = db


class Group(BaseModel):
    speciality = CharField(max_length=100)
    course_year = IntegerField()

    class Meta:
        table_name = 'groups'


class Student(BaseModel):
    student_number = CharField(max_length=20, unique=True)
    current_group = ForeignKeyField(Group, backref='students')
    status = CharField(max_length=50)

    class Meta:
        table_name = 'students'


class MovementType(BaseModel):
    name = CharField(max_length=50, unique=True)

    class Meta:
        table_name = 'movement_types'


class StudentMovement(BaseModel):
    student = ForeignKeyField(Student, backref='movements')
    movement_type = ForeignKeyField(MovementType, backref='movements')
    from_group = ForeignKeyField(Group, null=True, backref='from_movements')
    to_group = ForeignKeyField(Group, null=True, backref='to_movements')
    movement_date = DateField()
    reason = TextField()
    order_number = CharField(max_length=50, unique=True)
    created_by = CharField(max_length=100)
    is_active = BooleanField(default=True)

    class Meta:
        table_name = 'student_movements'


def init_db():
    db.connect()
    db.create_tables([Group, Student, MovementType, StudentMovement], safe=True)
    db.close()
    print("✅ База данных создана!")


if __name__ == '__main__':
    init_db()