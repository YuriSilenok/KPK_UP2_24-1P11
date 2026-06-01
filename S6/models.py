import os
from peewee import *

db_path = os.path.join(os.path.dirname(__file__), 'specialties.db')
db = SqliteDatabase(db_path)

class BaseModel(Model):
    class Meta:
        database = db

class Specialty(BaseModel):
    """Сущность: SPECIALTY (Специальности)"""
    id = AutoField(primary_key=True, verbose_name="Идентификатор")
    code = CharField(unique=True, null=False, verbose_name="Код")
    name = CharField(null=False, verbose_name="Название")
    is_active = BooleanField(default=True, null=False, verbose_name="Статус активности")

    class Meta:
        table_name = 'specialty'

class FGOS(BaseModel):
    """Сущность: FGOS (ФГОС)"""
    id = AutoField(primary_key=True, verbose_name="Идентификатор")
    code = CharField(unique=True, null=False, verbose_name="Код ФГОС")

    class Meta:
        table_name = 'fgos'

class SpecialtyFGOS(BaseModel):
    """Сущность: SPECIALTY_FGOS (Транзитивная таблица)"""
    # ИСПРАВЛЕНО: Явный null=False для запрета NULL по требованию препода
    specialty_id = ForeignKeyField(Specialty, column_name='specialty_id', backref='fgos_links', on_delete='CASCADE', null=False)
    fgos_id = ForeignKeyField(FGOS, column_name='fgos_id', backref='specialty_links', on_delete='CASCADE', null=False)

    class Meta:
        table_name = 'specialty_fgos'
        # ИСПРАВЛЕНО: Убран лишний id, задан составной первичный ключ из двух полей
        primary_key = CompositeKey('specialty_id', 'fgos_id')

def init_db():
    db.connect()
    db.create_tables([Specialty, FGOS, SpecialtyFGOS], safe=True)
    db.close()

if __name__ == "__main__":
    if os.path.exists(db_path):
        os.remove(db_path)
    init_db()
    print("УСПЕХ: База данных specialties.db успешно создана без ошибок!")
