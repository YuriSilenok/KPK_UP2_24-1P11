from peewee import *

db = SqliteDatabase('holiday.db')

class BaseModel(Model):
    class Meta:
        database = db

class HolidayType(BaseModel):
    """Справочник типов: holiday (праздник) или vacation (каникулы)"""
    id = PrimaryKeyField()
    name = CharField(max_length=50, null=False)
    code = CharField(
        max_length=8,
        unique=True,
        null=False,
        constraints=[Check("code IN ('holiday', 'vacation')")]
    )
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'holiday_type'

class Holiday(BaseModel):
    """Праздники"""
    id = PrimaryKeyField()
    name = CharField(max_length=100, null=False)
    date = DateField(null=False, index=True)
    type = ForeignKeyField(HolidayType, backref='holidays', null=False, index=True)
    is_active = BooleanField(default=True, null=False, index=True)

    class Meta:
        table_name = 'holiday'

class VacationPeriod(BaseModel):
    """Каникулы (период)"""
    id = PrimaryKeyField()
    name = CharField(max_length=100, null=False)
    start_date = DateField(null=False, index=True)
    end_date = DateField(null=False, index=True)
    type = ForeignKeyField(HolidayType, backref='vacations', null=False, index=True)
    is_active = BooleanField(default=True, null=False, index=True)

    class Meta:
        table_name = 'vacation_period'

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValueError("end_date должен быть >= start_date")
        return super().save(*args, **kwargs)

def init_db():
    """
    Инициализация базы данных.
    Создаёт таблицы и добавляет типы праздников по умолчанию:
    - name='Праздник', code='holiday'
    - name='Каникулы', code='vacation'
    """
    db.connect()
    db.create_tables([HolidayType, Holiday, VacationPeriod], safe=True)
    
    # Добавляем типы по умолчанию
    if HolidayType.select().count() == 0:
        HolidayType.create(name='Праздник', code='holiday')
        HolidayType.create(name='Каникулы', code='vacation')
    
    db.close()

if __name__ == '__main__':
    init_db()
    print("База данных создана.")
