from peewee import Model, SqliteDatabase, IntegerField, CharField, DecimalField, ForeignKeyField, SQL, BooleanField, AutoField

db = SqliteDatabase('load_assignment.db')

class BaseModel(Model):
    class Meta:
        database = db

class Teacher(BaseModel):
    id = AutoField()
    full_name = CharField(max_length=200, unique=True, constraints=[SQL('NOT NULL')])
    position = CharField(max_length=100, constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'Teacher'

class Discipline(BaseModel):
    id = AutoField()
    name = CharField(max_length=200, unique=True, constraints=[SQL('NOT NULL')])
    hours_total = IntegerField(constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'Discipline'

class Group(BaseModel):
    id = AutoField()
    group_number = CharField(max_length=20, unique=True, constraints=[SQL('NOT NULL')])
    specialty_id = IntegerField(constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'Group'

class Student(BaseModel):
    id = AutoField()
    student_number = CharField(max_length=50, unique=True, constraints=[SQL('NOT NULL')])
    current_group_id = ForeignKeyField(Group, backref="students", on_delete='CASCADE')
    status = CharField(max_length=50, constraints=[SQL('NOT NULL')])

    class Meta:
        table_name = 'Student'

class LoadAssignment(BaseModel):
    id = AutoField()
    teacher_id = ForeignKeyField(Teacher, backref='assignments', on_delete='CASCADE')
    discipline_id = ForeignKeyField(Discipline, backref='assignments', on_delete='CASCADE')
    group_id = ForeignKeyField(Group, backref='assignments', on_delete='CASCADE')
    semester = IntegerField(constraints=[SQL('CHECK (semester BETWEEN 1 AND 8)'), SQL('NOT NULL')])
    load_hours = DecimalField(max_digits=5, decimal_places=2, constraints=[SQL('CHECK (load_hours > 0)'), SQL('NOT NULL')])
    is_active = BooleanField(default=True)

    class Meta:
        table_name = 'LoadAssignment'
        indexes = (
            (('teacher_id', 'discipline_id', 'group_id', 'semester'), True),
        )

def init_db():
    db.connect()
    db.create_tables([Teacher, Discipline, Group, Student, LoadAssignment], safe=True)
    db.close()

if __name__ == '__main__':
    init_db()
