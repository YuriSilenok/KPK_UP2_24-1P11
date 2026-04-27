from peewee import *

db = SqliteDatabase('student_movement.db')

class BaseModel(Model):
    class Meta:
        database = db

class Group(BaseModel):
    group_name = CharField()
    speciality = CharField()
    course_year = IntegerField()

class Student(BaseModel):
    full_name = CharField()
    student_number = CharField(unique=True)
    status = CharField()
    group = ForeignKeyField(Group, backref='students')

class MovementType(BaseModel):
    name = CharField(unique=True)

class StudentMovement(BaseModel):
    student = ForeignKeyField(Student, backref='movements')
    movement_type = ForeignKeyField(MovementType)
    
    group_from = ForeignKeyField(Group, null=True, backref='movements_from')
    group_to = ForeignKeyField(Group, null=True, backref='movements_to')
    
    movement_date = DateField()
    reason = TextField()
    order_number = CharField(unique=True)

def init_db():
    db.connect()
    db.create_tables([
        Group,
        Student,
        MovementType,
        StudentMovement
    ])

if __name__ == "__main__":
    init_db()