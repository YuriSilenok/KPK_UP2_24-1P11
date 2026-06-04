from peewee import *

db = SqliteDatabase('holiday.db')

class BaseModel(Model):
    class Meta:
        database = db

class HolidayType(BaseModel):
    id = AutoField()
    name = CharField(max_length=50, null=False)
    code = CharField(max_length=8, unique=True, null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'holiday_type'

class Holiday(BaseModel):
    id = AutoField()
    name = CharField(max_length=100, null=False)
    date = DateField(null=False)
    # Исправлено: имя атрибута type_id соответствует doc.md и схеме БД
    type_id = ForeignKeyField(HolidayType, backref='holidays', null=False, column_name='type_id')
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'holiday'
        indexes = (
            (('date',), False),
            (('type_id',), False),  # Исправлено имя поля в индексе
        )

class VacationPeriod(BaseModel):
    id = AutoField()
    name = CharField(max_length=100, null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    # Исправлено: имя атрибута type_id соответствует doc.md и схеме БД
    type_id = ForeignKeyField(HolidayType, backref='vacations', null=False, column_name='type_id')
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'vacation_period'
        indexes = (
            (('start_date',), False),
            (('end_date',), False),
            (('type_id',), False),  # Исправлено имя поля в индексе
        )

    def save(self, *args, **kwargs):
        # Data integrity constraint (ограничение целостности данных)
        if self.end_date < self.start_date:
            raise ValueError("end_date must be >= start_date")
        return super().save(*args, **kwargs)

def init_db():
    db.connect()
    db.create_tables([HolidayType, Holiday, VacationPeriod], safe=True)
    
    # Начальные данные строго по требованиям
    if HolidayType.select().count() == 0:
        HolidayType.create(name='Праздник', code='holiday')
        HolidayType.create(name='Каникулы', code='vacation')
    
    db.close()

if __name__ == '__main__':
    init_db()
    print("Database created.")
