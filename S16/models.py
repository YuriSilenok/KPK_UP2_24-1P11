from peewee import *
from peewee import Check

db = SqliteDatabase('campus.db')

class BaseModel(Model):
    class Meta:
        database = db

class Campus(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50, unique=True, null=False)
    floors = IntegerField(null=False, constraints=[Check('floors > 0')])
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'campus'

    @staticmethod
    def get_campuses_list(min_floors=None, max_floors=None, exact_floors=None, address_contains=None):
        """
        Получить список корпусов по заданным параметрам
        """
        query = Campus.select().where(Campus.is_active == True)
        
        if min_floors is not None:
            query = query.where(Campus.floors >= min_floors)
        
        if max_floors is not None:
            query = query.where(Campus.floors <= max_floors)
        
        if exact_floors is not None:
            query = query.where(Campus.floors == exact_floors)
        
        if address_contains is not None:
            query = query.where(Campus.address.contains(address_contains))
        
        return query

def init_db():
    db.connect()
    # Создаем только таблицу Campus
    db.create_tables([Campus], safe=True)
    db.close()

if __name__ == '__main__':
    init_db()
    print("База данных создана.")