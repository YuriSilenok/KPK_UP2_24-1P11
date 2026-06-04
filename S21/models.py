from peewee import *

db = SqliteDatabase('holiday.db')

class BaseModel(Model):
    class Meta:
        database = db

class HolidayType(BaseModel):
    """Справочник типов: holiday (праздник) или vacation (каникулы)"""
    id = AutoField()
    name = CharField(max_length=50, null=False)
    code = CharField(max_length=8, unique=True, null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'holiday_type'

class Holiday(BaseModel):
    """Праздники"""
    id = AutoField()
    name = CharField(max_length=100, null=False)
    date = DateField(null=False)
    type = ForeignKeyField(HolidayType, backref='holidays', null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'holiday'
        indexes = (
            (('date',), False),
            (('type',), False),
        )

class VacationPeriod(BaseModel):
    """Каникулы (период)"""
    id = AutoField()
    name = CharField(max_length=100, null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    type = ForeignKeyField(HolidayType, backref='vacations', null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'vacation_period'
        indexes = (
            (('start_date',), False),
            (('end_date',), False),
            (('type',), False),
        )

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValueError("end_date должен быть >= start_date")
        return super().save(*args, **kwargs)

def init_db():
    db.connect()
    db.create_tables([HolidayType, Holiday, VacationPeriod], safe=True)
    
    if HolidayType.select().count() == 0:
        HolidayType.create(name='Праздник', code='holiday')
        HolidayType.create(name='Каникулы', code='vacation')
    
    db.close()

if __name__ == '__main__':
    init_db()
    print("База данных создана.")
