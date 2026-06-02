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
    # ИСПРАВЛЕНО ПО РЕКОМЕНДАЦИИ БОТА: Убраны избыточные column_name.
    # Переменные названы specialty и fgos. Peewee автоматически создаст 
    # в самой БД колонки с суффиксами '_id': 'specialty_id' и 'fgos_id' строго по ТЗ.
    specialty = ForeignKeyField(Specialty, backref='fgos_links', on_delete='CASCADE', null=False)
    fgos = ForeignKeyField(FGOS, backref='specialty_links', on_delete='CASCADE', null=False)

    class Meta:
        table_name = 'specialty_fgos'
        # Задан составной первичный ключ
        primary_key = CompositeKey('specialty', 'fgos')

def init_db():
    db.connect()
    db.create_tables([Specialty, FGOS, SpecialtyFGOS], safe=True)
    db.close()

if __name__ == "__main__":
    if os.path.exists(db_path):
        os.remove(db_path)
    init_db()
    print("УСПЕХ: База данных specialties.db успешно создана без синтаксических избыточностей!")
