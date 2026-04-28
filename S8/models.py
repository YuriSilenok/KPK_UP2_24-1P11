"""
Модели для сервиса подгрупп (Subgroup Service) - Вариант 8
"""

from peewee import *
import os

# Путь к файлу базы данных
DB_PATH = 'subgroup_service.db'

# Подключение к БД
db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    """Базовый класс модели с подключением к БД"""
    class Meta:
        database = db


class Subgroup(BaseModel):
    """
    Модель подгруппы
    
    Поля:
    - id: первичный ключ
    - type: тип подгруппы (1=language, 2=sport, 3=other)
    - group_id: внешний ключ к группе (из сервиса групп)
    """
    id = AutoField()
    type = IntegerField(verbose_name='Тип подгруппы')
    group_id = IntegerField(verbose_name='ID группы')
    
    class Meta:
        table_name = 'subgroups'
        indexes = (
            (('group_id', 'type'), True),
        )
    
    def __str__(self):
        return f"Подгруппа {self.type} (группа {self.group_id})"


def init_db():
    """
    Функция инициализации базы данных
    Создаёт таблицы, если они не существуют
    """
    try:
        # Подключаемся к БД
        db.connect()
        
        # Создаём таблицы (только Subgroup)
        db.create_tables([Subgroup], safe=True)
        
        print(f"✅ База данных '{DB_PATH}' успешно инициализирована")
        print(f"   - Создана таблица: {Subgroup._meta.table_name}")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации БД: {e}")
    finally:
        # Закрываем соединение
        if not db.is_closed():
            db.close()


def get_db_connection():
    """
    Возвращает подключение к БД для использования в API
    """
    if db.is_closed():
        db.connect()
    return db


def close_db_connection():
    """
    Закрывает подключение к БД
    """
    if not db.is_closed():
        db.close()


# Точка входа
if __name__ == '__main__':
    """
    Точка входа: вызывается при запуске файла напрямую
    """
    print("=" * 50)
    print("Инициализация базы данных для сервиса подгрупп (вариант 8)")
    print("=" * 50)
    init_db()
    print("=" * 50)
    print("✅ Готово! База данных инициализирована.")
    print("=" * 50)