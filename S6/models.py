from peewee import *

db = SqliteDatabase('specialties.db')

class Specialty(Model):
    code = CharField(unique=True)
    name = CharField()
    class Meta:
        database = db

class FGOS(Model):
    code = CharField(unique=True)
    class Meta:
        database = db

class SpecialtyFGOS(Model):
    specialty = ForeignKeyField(Specialty)
    fgos = ForeignKeyField(FGOS)
    class Meta:
        database = db

def init_db():
    db.connect()
    db.create_tables([Specialty, FGOS, SpecialtyFGOS], safe=True)
    db.close()

if __name__ == "__main__":
    init_db()
    print("База данных готова!")
