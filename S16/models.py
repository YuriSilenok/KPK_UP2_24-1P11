from peewee import *
from peewee import Check

db = SqliteDatabase('campus.db')

class BaseModel(Model):
    class Meta:
        database = db

class Campus(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50, unique=True, null=False)
    address = CharField(max_length=200, null=False)
    floors = IntegerField(null=False, constraints=[Check('floors > 0')])
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'campus'

    @staticmethod
    def create_campus(name, address, floors):
        """
        Создание нового корпуса
        """
        if not name or len(name.strip()) == 0:
            raise ValueError("Поле name не может быть пустым")
        
        if not address or len(address.strip()) == 0:
            raise ValueError("Поле address не может быть пустым")
        
        if floors <= 0:
            raise ValueError("Поле floors должно быть больше 0")
        
        try:
            campus = Campus.create(
                name=name,
                address=address,
                floors=floors
            )
            return campus
        except IntegrityError:
            raise ValueError("Campus с таким именем уже существует")

    @staticmethod
    def update_campus(campus_id, name=None, address=None, floors=None):
        """
        Изменение корпуса по ID
        """
        try:
            campus = Campus.get_by_id(campus_id)
        except Campus.DoesNotExist:
            return None
        
        if name is not None:
            if len(name.strip()) == 0:
                raise ValueError("Поле name не может быть пустым")
            campus.name = name
        
        if address is not None:
            if len(address.strip()) == 0:
                raise ValueError("Поле address не может быть пустым")
            campus.address = address
        
        if floors is not None:
            if floors <= 0:
                raise ValueError("Поле floors должно быть больше 0")
            campus.floors = floors
        
        try:
            campus.save()
            return campus
        except IntegrityError:
            raise ValueError("Campus с таким именем уже существует")

    @staticmethod
    def delete_campus(campus_id):
        """
        Мягкое удаление корпуса по ID (установка is_active = False)
        Возвращает True, если корпус был успешно деактивирован, иначе False
        """
        try:
            campus = Campus.get_by_id(campus_id)
            campus.is_active = False
            campus.save()
            return True
        except Campus.DoesNotExist:
            return False

    @staticmethod
    def get_campus_by_id(campus_id):
        """
        Получение корпуса по ID
        """
        try:
            return Campus.get_by_id(campus_id)
        except Campus.DoesNotExist:
            return None

    @staticmethod
    def get_campuses_list(min_floors=None, max_floors=None, exact_floors=None, address_contains=None, is_active=True):
        """
        Получить список корпусов по заданным параметрам
        """
        query = Campus.select()
        
        if is_active is not None:
            query = query.where(Campus.is_active == is_active)
        
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
