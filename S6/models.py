import os
from peewee import *

# Путь к файлу базы данных в текущей папке
db_path = os.path.join(os.path.dirname(__file__), 'specialties.db')
db = SqliteDatabase(db_path)

class BaseModel(Model):
    class Meta:
        database = db

class Specialty(BaseModel):
    """Сущность: SPECIALTY (Специальности)"""
    code = CharField(unique=True, null=False)
    name = CharField(null=False)
    is_active = BooleanField(default=True, null=False)  # Флаг для мягкого удаления

    class Meta:
        table_name = 'specialty'

class FGOS(BaseModel):
    """Сущность: FGOS (ФГОС)"""
    code = CharField(unique=True, null=False)

    class Meta:
        table_name = 'fgos'

class SpecialtyFGOS(BaseModel):
    """Сущность: SPECIALTY_FGOS (Транзитивная таблица связи многие-ко-многим)"""
    # Поля внешних ключей не могут быть NULL согласно требованиям методички
    specialty = ForeignKeyField(Specialty, column_name='specialty_id', backref='fgos_links', on_delete='CASCADE')
    fgos = ForeignKeyField(FGOS, column_name='fgos_id', backref='specialty_links', on_delete='CASCADE')

    class Meta:
        table_name = 'specialty_fgos'
        # Уникальный индекс, чтобы исключить дублирование одинаковых связей
        indexes = (
            (('specialty', 'fgos'), True),
        )

def init_db():
    """Функция инициализации и создания таблиц в БД"""
    db.connect()
    db.create_tables([Specialty, FGOS, SpecialtyFGOS], safe=True)
    db.close()

# Точка входа, которая автоматически вызывает функцию инициализации базы данных
if __name__ == "__main__":
    # Если старая база существовала, удаляем её для применения чистой структуры
    if os.path.exists(db_path):
        os.remove(db_path)
        
    init_db()
    print("УСПЕХ: База данных specialties.db успешно инициализирована!")
