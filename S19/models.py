from datetime import datetime
from peewee import *

db = SqliteDatabase('resource_pool.db')

class BaseModel(Model):
    class Meta:
        database = db

class ResourceCategory(BaseModel):
    id = AutoField(primary_key=True)
    title = CharField(max_length=100, unique=True, constraints=[Check("length(title) >= 1")])
    details = CharField(max_length=500, null=False)

    class Meta:
        table_name = 'resource_categories'

class Resource(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField(max_length=100, constraints=[Check("length(name) >= 1")])
    description = CharField(max_length=500, null=False)
    category_id = ForeignKeyField(ResourceCategory, backref='resources', on_delete='RESTRICT')
    total_quantity = IntegerField(constraints=[Check('total_quantity >= 1')])
    available_quantity = IntegerField(constraints=[Check('available_quantity >= 0')])
    unit = CharField(max_length=10, choices=['шт', 'компл', 'экз'], default='шт')
    status = CharField(max_length=20, choices=['available', 'maintenance', 'retired'], default='available')
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'resources'
        indexes = (
            (('name', 'category_id'), True),
        )

    def save(self, *args, **kwargs):
        if self.available_quantity is None and self.total_quantity is not None:
            self.available_quantity = self.total_quantity
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def disable(cls, resource_id):
        affected = cls.update(is_active=False).where(
            (cls.id == resource_id) & (cls.is_active == True)
        ).execute()
        return affected > 0

def init_db():
    db.connect()
    db.create_tables([ResourceCategory, Resource], safe=True)

    if not ResourceCategory.select().exists():
        ResourceCategory.create(title='Спортивный инвентарь', details='Мячи, маты и т.д.')
        ResourceCategory.create(title='Библиотечный фонд', details='Книги, учебники')
        ResourceCategory.create(title='Лабораторное оборудование', details='Приборы и инструменты')

    if not Resource.select().exists():
        sport_category = ResourceCategory.get(title='Спортивный инвентарь')
        Resource.create(
            name='мяч',
            description='Wilson Evolution',
            category_id=sport_category,
            total_quantity=100,
            unit='шт'
        )
        Resource.create(
            name='мат',
            category_id=sport_category,
            total_quantity=50,
            unit='шт',
            status='maintenance'
        )

if __name__ == '__main__':
    init_db()
    print("База данных инициализирована.")