from peewee import *

db = SqliteDatabase('holiday.db')

class BaseModel(Model):
    class Meta:
        database = db

class Holiday(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=100, unique=True, null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    type = CharField(default='holiday', null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'holiday'

class Faculty(BaseModel):
    id = PrimaryKeyField()
    name = CharField(unique=True, null=False)

    class Meta:
        table_name = 'faculty'

class HolidayFaculty(BaseModel):
    holiday = ForeignKeyField(Holiday, backref='faculties', on_delete='CASCADE', null=False)
    faculty = ForeignKeyField(Faculty, backref='holidays', on_delete='CASCADE', null=False)

    class Meta:
        table_name = 'holiday_faculty'
        primary_key = CompositeKey('holiday', 'faculty')

def init_db():
    db.connect()
    db.create_tables([Holiday, Faculty, HolidayFaculty], safe=True)
    db.close()

if __name__ == '__main__':
    init_db()
    print("База данных создана.")