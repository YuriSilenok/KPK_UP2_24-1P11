"""""
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

class SubgroupType(BaseModel):
    class Meta:
        table_name = 'subgroup_types'

class Subgroup(BaseModel):
    id = AutoField()
    name = ForeignKeyField(SubgroupType, verbose_name='ID типа подгруппы')  # ← исправленная строка
    group_id = IntegerField(verbose_name='ID группы')
    
    class Meta:
        table_name = 'subgroups'
        indexes = (
            (('group_id', 'name'), True),
        )
    
    def __str__(self):
        return f"Подгруппа {self.name} (группа {self.group_id})"


class SubgroupStudent(BaseModel):
    """
    Модель связи подгруппы и студента
    (Подгруппа_Студент)
    """
    id = AutoField()
    subgroup_id = IntegerField(verbose_name='ID подгруппы')  # FK на Subgroup
    student_id = IntegerField(verbose_name='ID студента')   # FK на Student
    
    class Meta:
        table_name = 'subgroup_students'
        indexes = (
            (('subgroup_id', 'student_id'), True),  # Уникальная пара подгруппа-студент
        )
    
    def __str__(self):
        return f"Студент {self.student_id} в подгруппе {self.subgroup_id}"


def init_db():
    """
    Функция инициализации базы данных
    Создаёт таблицы, если они не существуют
    """
    try:
        # Подключаемся к БД
        db.connect()
        
        # Создаём таблицы (Subgroup и SubgroupStudent)
        db.create_tables([Subgroup, SubgroupStudent], safe=True)
        
        print(f"✅ База данных '{DB_PATH}' успешно инициализирована")
        print(f"   - Создана таблица: {Subgroup._meta.table_name}")
        print(f"   - Создана таблица: {SubgroupStudent._meta.table_name}")
        
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