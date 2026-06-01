import os
import sys
from peewee import *
from datetime import date, datetime

# Инициализация базы данных
db = SqliteDatabase('employee_status.db')

class BaseModel(Model):
    class Meta:
        database = db

class Position(BaseModel):
    id = AutoField(primary_key=True)
    title = CharField(max_length=100, unique=True, constraints=[Check('length(title) > 0')])
    description = TextField(null=True)
    base_rate = FloatField(constraints=[Check('base_rate > 0')])
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class EmployeePosition(BaseModel):
    id = AutoField(primary_key=True)
    profile_id = IntegerField()  # Внешний ключ к Profile Service
    position = ForeignKeyField(Position, backref='employees', on_delete='RESTRICT')
    rate = FloatField(constraints=[Check('rate BETWEEN 0.1 AND 2.0')], default=1.0)
    is_primary = BooleanField(default=False)
    start_date = DateField()
    end_date = DateField(null=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
    
    class Meta:
        indexes = (
            (('profile_id', 'is_primary'), True),
            (('profile_id', 'position', 'start_date'), True),
        )

class Leave(BaseModel):
    id = AutoField(primary_key=True)
    employee_position = ForeignKeyField(EmployeePosition, backref='leaves', on_delete='CASCADE')
    start_date = DateField()
    end_date = DateField(constraints=[Check('end_date > start_date')])
    leave_type = CharField(max_length=20, default='annual')  # annual, sick, unpaid
    status = CharField(max_length=20, default='pending')  # pending, approved, rejected
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class SickLeave(BaseModel):
    id = AutoField(primary_key=True)
    employee_position = ForeignKeyField(EmployeePosition, backref='sick_leaves', on_delete='CASCADE')
    start_date = DateField()
    end_date = DateField(constraints=[Check('end_date > start_date')])
    certificate_number = CharField(max_length=50, unique=True)
    status = CharField(max_length=20, default='active')  # active, closed
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

def init_db():
    """Функция инициализации базы данных"""
    db.connect()
    db.create_tables([Position, EmployeePosition, Leave, SickLeave], safe=True)
    print("База данных инициализирована успешно!")
    print("Созданы таблицы:")
    print("- Position (Должности)")
    print("- EmployeePosition (Ставки сотрудников)")
    print("- Leave (Отпуска)")
    print("- SickLeave (Больничные)")
    return db

def get_db():
    """Возвращает подключение к БД"""
    return db

if __name__ == "__main__":
    # Точка входа для инициализации БД
    init_db()