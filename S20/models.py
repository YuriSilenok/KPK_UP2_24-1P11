import datetime
from peewee import (
    SqliteDatabase, Model, AutoField, CharField, 
    IntegerField, DateField, DateTimeField, Check, IntegrityError
)

# ============================================================
# Подключение к базе данных
# ============================================================
db = SqliteDatabase('periods.db')

# ============================================================
# Базовая модель
# ============================================================
class BaseModel(Model):
    class Meta:
        database = db

# ============================================================
# Модель учебного периода
# ============================================================
class AcademicPeriod(BaseModel):
    id = AutoField()                          # ID периода
    name = CharField(max_length=100)          # Название
    period_type = CharField(max_length=20)    # Тип: Semester или Module
    year = IntegerField()                     # Год
    start_date = DateField()                  # Дата начала
    end_date = DateField()                    # Дата окончания
    parent_period_id = IntegerField(default=0) # ID родителя (0 - корневой)
    description = CharField(max_length=500, default='')  # Описание
    created_at = DateTimeField(default=datetime.datetime.now)  # Дата создания
    updated_at = DateTimeField(default=datetime.datetime.now)  # Дата обновления
    
    class Meta:
        table_name = 'academic_periods'
        # Уникальность: год + тип + название
        indexes = (
            (('year', 'period_type', 'name'), True),
        )
    
    def save(self, *args, **kwargs):
        # Обновляем дату изменения
        self.updated_at = datetime.datetime.now()
        
        # Проверка дат
        if self.start_date > self.end_date:
            raise ValueError('Дата начала не может быть позже даты окончания')
        
        # Проверка для семестра
        if self.period_type == 'Semester' and self.parent_period_id != 0:
            raise ValueError('У семестра parent_period_id должен быть 0')
        
        # Проверка для модуля
        if self.period_type == 'Module':
            if self.parent_period_id <= 0:
                raise ValueError('У модуля parent_period_id должен быть больше 0')
            
            # Проверяем, что родитель существует
            parent = AcademicPeriod.get_or_none(id=self.parent_period_id)
            if not parent:
                raise ValueError(f'Родитель с ID {self.parent_period_id} не найден')
            if parent.period_type != 'Semester':
                raise ValueError('Родитель модуля должен быть семестром')
        
        super().save(*args, **kwargs)
    
    def delete_instance(self, *args, **kwargs):
        # Проверяем, есть ли дочерние периоды
        children = AcademicPeriod.select().where(
            AcademicPeriod.parent_period_id == self.id
        ).count()
        
        if children > 0:
            raise ValueError(f'Нельзя удалить: есть {children} дочерних периодов')
        
        super().delete_instance(*args, **kwargs)

# ============================================================
# Вспомогательные функции
# ============================================================

def create_semester(name, year, start_date, end_date, description=''):
    """Создать семестр"""
    return AcademicPeriod.create(
        name=name,
        period_type='Semester',
        year=year,
        start_date=start_date,
        end_date=end_date,
        parent_period_id=0,
        description=description
    )

def create_module(name, year, start_date, end_date, semester_id, description=''):
    """Создать модуль внутри семестра"""
    return AcademicPeriod.create(
        name=name,
        period_type='Module',
        year=year,
        start_date=start_date,
        end_date=end_date,
        parent_period_id=semester_id,
        description=description
    )

def get_semesters():
    """Получить все семестры"""
    return AcademicPeriod.select().where(AcademicPeriod.period_type == 'Semester')

def get_modules(semester_id):
    """Получить все модули семестра"""
    return AcademicPeriod.select().where(
        (AcademicPeriod.period_type == 'Module') & 
        (AcademicPeriod.parent_period_id == semester_id)
    )

def get_periods_by_year(year):
    """Получить все периоды за год"""
    return AcademicPeriod.select().where(AcademicPeriod.year == year)

def update_period(period_id, **kwargs):
    """Обновить период"""
    period = AcademicPeriod.get_by_id(period_id)
    for key, value in kwargs.items():
        if hasattr(period, key):
            setattr(period, key, value)
    period.save()
    return period

def delete_period(period_id):
    """Удалить период"""
    period = AcademicPeriod.get_by_id(period_id)
    period.delete_instance()
    return True

# ============================================================
# Инициализация и тестовые данные
# ============================================================

def init_db():
    """Создать таблицы и добавить тестовые данные"""
    db.connect()
    db.create_tables([AcademicPeriod])
    
    # Если данные уже есть - выходим
    if AcademicPeriod.select().count() > 0:
        return
    
    print('Добавление тестовых данных...')
    
    # Создаём семестры
    sem1 = create_semester(
        name='Осенний семестр 2025',
        year=2025,
        start_date=datetime.date(2025, 9, 1),
        end_date=datetime.date(2025, 12, 31),
        description='Первый семестр'
    )
    
    sem2 = create_semester(
        name='Весенний семестр 2026',
        year=2026,
        start_date=datetime.date(2026, 2, 7),
        end_date=datetime.date(2026, 5, 30),
        description='Второй семестр'
    )
    
    # Создаём модули
    create_module(
        name='Модуль 1',
        year=2025,
        start_date=datetime.date(2025, 9, 1),
        end_date=datetime.date(2025, 10, 15),
        semester_id=sem1.id
    )
    
    create_module(
        name='Модуль 2',
        year=2025,
        start_date=datetime.date(2025, 10, 16),
        end_date=datetime.date(2025, 12, 15),
        semester_id=sem1.id
    )
    
    create_module(
        name='Модуль 3',
        year=2026,
        start_date=datetime.date(2026, 2, 7),
        end_date=datetime.date(2026, 3, 25),
        semester_id=sem2.id
    )
    
    print(f'Создано {AcademicPeriod.select().count()} периодов')

# ============================================================
# Пример использования
# ============================================================

def main():
    # Инициализация
    init_db()
    
    print('\n=== Все семестры ===')
    for s in get_semesters():
        print(f'{s.id}: {s.name} ({s.year})')
    
    print('\n=== Модули осеннего семестра ===')
    sem = AcademicPeriod.get(name='Осенний семестр 2025')
    for m in get_modules(sem.id):
        print(f'{m.name}: {m.start_date} - {m.end_date}')
    
    print('\n=== Все периоды 2025 года ===')
    for p in get_periods_by_year(2025):
        print(f'{p.name} ({p.period_type})')
    
    print('\n=== Обновление периода ===')
    period = AcademicPeriod.get(name='Модуль 1')
    print(f'Было: {period.description}')
    update_period(period.id, description='Обновлённое описание')
    print(f'Стало: {period.description}')
    
    # Закрываем соединение
    db.close()

if __name__ == '__main__':
    main()