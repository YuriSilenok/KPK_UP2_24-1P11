from datetime import datetime
from peewee import *

database = SqliteDatabase('resource_pool.db')

class BaseModel(Model):
    class Meta:
        database = database

class Category(BaseModel):
    id = AutoField(primary_key=True)
    title = CharField(max_length=100, unique=True, constraints=[Check("length(title) >= 1")])
    details = CharField(max_length=500, null=True)

    class Meta:
        table_name = 'categories'

class Person(BaseModel):
    id = AutoField(primary_key=True)
    login = CharField(max_length=50, unique=True)
    mail = CharField(max_length=100, unique=True)

    class Meta:
        table_name = 'persons'

class Asset(BaseModel):
    id = AutoField(primary_key=True)
    title = CharField(max_length=100, constraints=[Check("length(title) >= 1")])
    description = CharField(max_length=500, null=True)
    category = ForeignKeyField(Category, backref='assets', on_delete='RESTRICT')
    total_count = IntegerField(constraints=[Check('total_count >= 1')], default=1)
    available_count = IntegerField(constraints=[Check('available_count >= 0')], default=1)
    measure = CharField(max_length=10, choices=['шт', 'компл', 'экз'], default='шт')
    condition = CharField(max_length=20, choices=['available', 'maintenance', 'retired'], default='available')
    active = BooleanField(default=True)
    created_date = DateTimeField(default=datetime.now)
    modified_date = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'assets'
        indexes = (
            (('title', 'category'), True),
        )

    def save(self, *args, **kwargs):
        if not self.available_count:
            self.available_count = self.total_count
        self.modified_date = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def disable(cls, asset_id):
        affected = cls.update(active=False).where(
            (cls.id == asset_id) & (cls.active == True)
        ).execute()
        return affected > 0

class Booking(BaseModel):
    id = AutoField(primary_key=True)
    asset = ForeignKeyField(Asset, backref='bookings', on_delete='CASCADE')
    booked_by = ForeignKeyField(Person, backref='bookings', on_delete='CASCADE')
    amount = IntegerField(constraints=[Check('amount >= 1')], default=1)
    start_dt = DateTimeField()
    end_dt = DateTimeField()
    reason = TextField(null=True)
    booking_status = CharField(max_length=20, choices=['active', 'completed', 'cancelled'], default='active')
    created_dt = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'bookings'

def initialize_database():
    database.connect()
    database.create_tables([Category, Asset, Person, Booking], safe=True)

    if not Category.select().exists():
        Category.create(title='Спортивный инвентарь', details='Мячи, маты и т.д.')
        Category.create(title='Библиотечный фонд', details='Книги, учебники')
        Category.create(title='Лабораторное оборудование', details='Приборы и инструменты')

    if not Person.select().exists():
        Person.create(login='teacher1', mail='teacher1@gmail.com')
        Person.create(login='student1', mail='student1@gmail.com')

    if not Asset.select().exists():
        sport_category = Category.get(title='Спортивный инвентарь')
        Asset.create(
            title='мяч',
            description='Wilson Evolution',
            category=sport_category,
            total_count=100,
            measure='шт'
        )
        Asset.create(
            title='мат',
            category=sport_category,
            total_count=50,
            measure='шт',
            condition='maintenance'
        )

def pusk():
    initialize_database()
    print("База данных инициализирована.")

if __name__ == '__main__':
    pusk()