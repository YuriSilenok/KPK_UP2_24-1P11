"""
Модели для сервиса подгрупп (Subgroup Service) — Политехнический колледж Кострома
Связь с предметом (subject_id) для определения совместимости подгрупп в расписании
"""

from peewee import *
import os

DB_PATH = 'subgroup_service.db'
db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class Subgroup(BaseModel):
    """
    Модель подгруппы
    subject_id — внешний ключ к предмету (дисциплине)
    """
    group_id = IntegerField(verbose_name='ID группы')
    name = CharField(verbose_name='Название подгруппы')
    discipline_id = IntegerField(verbose_name='ID предмета')
    is_active = BooleanField(verbose_name='Активна', default=True)  # ← ДОБАВЛЕНО
    
    class Meta:
        table_name = 'subgroups'
        indexes = (
            (('group_id', 'name'), True),
        )
    
    def __str__(self):
        return f"Подгруппа {self.name} (предмет {self.discipline_id}) - группа {self.group_id}"


class SubgroupStudent(BaseModel):
    """
    Модель связи подгруппы и студента
    """
    subgroup_id = ForeignKeyField(Subgroup, verbose_name='ID подгруппы', backref='students')
    student_id = IntegerField(verbose_name='ID студента')  # ← ОСТАЛОСЬ IntegerField (ID из другого сервиса)
    
    class Meta:
        table_name = 'subgroup_students'
        indexes = (
            (('subgroup_id', 'student_id'), True),
        )
    
    def __str__(self):
        return f"Студент {self.student_id} в подгруппе {self.subgroup_id}"


def init_db():
    try:
        db.connect()
        db.create_tables([Subgroup, SubgroupStudent], safe=True)
        print(f"✅ База данных '{DB_PATH}' успешно инициализирована")
        print(f"   - Создана таблица: {Subgroup._meta.table_name}")
        print(f"   - Создана таблица: {SubgroupStudent._meta.table_name}")
    except Exception as e:
        print(f"❌ Ошибка при инициализации БД: {e}")
    finally:
        if not db.is_closed():
            db.close()


if __name__ == '__main__':
    print("=" * 50)
    print("Инициализация БД для сервиса подгрупп (Политехнический колледж Кострома)")
    print("=" * 50)
    init_db()
    print("=" * 50)
    print("✅ Готово!")
    print("=" * 50)