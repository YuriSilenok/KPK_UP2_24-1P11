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
    type_id = ForeignKeyField(HolidayType, backref='holidays', null=False, column_name='type_id')
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'holiday'
        indexes = (
            (('date',), False),
            (('type_id',), False),
        )

def init_db():
    db.connect()
    # Создаем только те таблицы, что есть в doc.md
    db.create_tables([HolidayType, Holiday], safe=True)
    db.close()

if __name__ == '__main__':
    init_db()
    print("Database created.")
