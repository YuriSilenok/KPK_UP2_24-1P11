from peewee import *

db = SqliteDatabase('campus.db')

class BaseModel(Model):
    class Meta:
        database = db

class Campus(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50, unique=True, null=False)
    address = CharField(null=False)
    floors = IntegerField(null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'campus'

class Amenity(BaseModel):
    id = PrimaryKeyField()
    title = CharField(unique=True, null=False)

    class Meta:
        table_name = 'amenity'

class CampusAmenity(BaseModel):
    campus = ForeignKeyField(Campus, backref='amenities', on_delete='CASCADE', null=False)
    amenity = ForeignKeyField(Amenity, backref='campuses', on_delete='CASCADE', null=False)

    class Meta:
        table_name = 'campus_amenity'
        primary_key = CompositeKey('campus', 'amenity')

def init_db():
    db.connect()
    db.create_tables([Campus, Amenity, CampusAmenity], safe=True)
    db.close()

if __name__ == '__main__':
    init_db()
    print("База данных создана.")