from peewee import *

db = SqliteDatabase('holiday.db')

class BaseModel(Model):
    class Meta:
        database = db

class HolidayType(BaseModel):
    """Справочник типов: holiday (праздник) или vacation (каникулы)"""
    id = PrimaryKeyField()
    name = CharField(max_length=50, unique=True, null=False)
    code = CharField(max_length=20, unique=True, null=False)

    class Meta:
        table_name = 'holiday_type'

class Holiday(BaseModel):
    """Праздники и каникулы"""
    id = PrimaryKeyField()
    name = CharField(max_length=100, unique=True, null=False)
    date = DateField(null=True)
    start_date = DateField(null=True)
    end_date = DateField(null=True)
    type = ForeignKeyField(HolidayType, backref='holidays', null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'holiday'

class Faculty(BaseModel):
    """Отделения/факультеты"""
    id = PrimaryKeyField()
    name = CharField(max_length=100, unique=True, null=False)
    short_name = CharField(max_length=50, null=True)

    class Meta:
        table_name = 'faculty'

class HolidayFaculty(BaseModel):
    """Связь праздников с отделениями"""
    holiday = ForeignKeyField(Holiday, backref='faculties', on_delete='CASCADE', null=False)
    faculty = ForeignKeyField(Faculty, backref='holidays', on_delete='CASCADE', null=False)

    class Meta:
        table_name = 'holiday_faculty'
        primary_key = CompositeKey('holiday', 'faculty')

def init_db():
    db.connect()
    db.create_tables([HolidayType, Holiday, Faculty, HolidayFaculty], safe=True)
    
    # Добавляем типы по умолчанию
    if HolidayType.select().count() == 0:
        HolidayType.create(name='Праздник', code='holiday')
        HolidayType.create(name='Каникулы', code='vacation')
    
    db.close()

if __name__ == '__main__':
    init_db()
    print("База данных создана.")