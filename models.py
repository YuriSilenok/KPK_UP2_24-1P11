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
    - name: название подгруппы
    - type: тип подгруппы (language/sport/other)
    - group_id: внешний ключ к группе (из сервиса групп)
    """
    id = AutoField()
    name = CharField(max_length=100, verbose_name='Название подгруппы')
    type = CharField(
        max_length=20,
        choices=['language', 'sport', 'other'],
        verbose_name='Тип подгруппы'
    )
    group_id = IntegerField(verbose_name='ID группы')
    
    class Meta:
        table_name = 'subgroups'
        # Уникальная комбинация: в одной группе не может быть двух подгрупп с одинаковым названием
        indexes = (
            (('group_id', 'name'), True),
        )
    
    def __str__(self):
        return f"{self.name} (группа {self.group_id})"


class StudentInSubgroup(BaseModel):
    """
    Транзитивная модель для связи многие-ко-многим между подгруппой и студентом
    
    Поля:
    - id: первичный ключ
    - subgroup: внешний ключ к подгруппе
    - student_id: внешний ключ к студенту (из сервиса студентов)
    """
    id = AutoField()
    subgroup = ForeignKeyField(Subgroup, backref='students', verbose_name='Подгруппа')
    student_id = IntegerField(verbose_name='ID студента')
    
    class Meta:
        table_name = 'student_in_subgroups'
        # Уникальная комбинация: один студент не может быть дважды в одной подгруппе
        indexes = (
            (('subgroup', 'student_id'), True),
        )
    
    def __str__(self):
        return f"Студент {self.student_id} в подгруппе {self.subgroup.name}"


def init_db():
    """
    Функция инициализации базы данных
    Создаёт таблицы, если они не существуют
    """
    try:
        # Подключаемся к БД
        db.connect()
        
        # Создаём таблицы
        db.create_tables([Subgroup, StudentInSubgroup], safe=True)
        
        print(f"✅ База данных '{DB_PATH}' успешно инициализирована")
        print(f"   - Создана таблица: {Subgroup._meta.table_name}")
        print(f"   - Создана таблица: {StudentInSubgroup._meta.table_name}")
        
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