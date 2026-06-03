import datetime
from peewee import *

db = SqliteDatabase('employee_status.db')

# ---------- Валидаторы ----------
def validate_positive(value):
    """Проверка, что значение — положительное целое"""
    if value <= 0:
        raise ValueError("user_id должен быть положительным целым числом")

def validate_hire_date(value):
    """Проверка, что дата найма не раньше 1900-01-01"""
    if value < datetime.date(1900, 1, 1):
        raise ValueError("Дата найма не может быть раньше 1900-01-01")

# ---------- Модели ----------
class BaseModel(Model):
    class Meta:
        database = db

class Employee(BaseModel):
    class Meta:
        db_table = "employees"

    id = AutoField()
    user_id = IntegerField(unique=True, null=False) 
    hire_date = DateField(null=False)
    status = CharField(max_length=20, default='active')
    is_deleted = BooleanField(default=False)
    updated_at = DateTimeField(default=datetime.datetime.now) 

    def save(self, *args, **kwargs):
        """Валидация полей и автоматическое обновление updated_at перед сохранением"""
        validate_positive(self.user_id)
        validate_hire_date(self.hire_date)
        
        allowed_statuses = ['active', 'on_vacation', 'sick_leave', 'fired']
        if self.status not in allowed_statuses:
            raise ValueError(f"Статус должен быть одним из: {', '.join(allowed_statuses)}")
            
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    def soft_delete(self):
        """Мягкое удаление сотрудника"""
        if not self.is_deleted:
            self.is_deleted = True
            self.save()
            return True
        return False

    @property
    def positions(self):
        """Возвращает список должностей в требуемом формате"""
        result = []
        for ep in EmployeePosition.select().where(EmployeePosition.employee == self):
            result.append({
                "position_title": ep.position.title,
                "start_date": ep.start_date.isoformat(),
                "end_date": ep.end_date.isoformat() if ep.end_date else None,
                "load_factor": ep.load_factor
            })
        return result

class Position(BaseModel):
    class Meta:
        db_table = "positions"

    id = AutoField()
    title = CharField(max_length=100, null=False)
    description = TextField(null=True)

    def save(self, *args, **kwargs):
        if not self.title or not (1 <= len(str(self.title)) <= 100):
            raise ValueError("Длина названия должности должна быть от 1 до 100 символов")
        return super().save(*args, **kwargs)

class EmployeePosition(BaseModel):
    class Meta:
        db_table = "employee_positions"

    id = AutoField()
    employee = ForeignKeyField(Employee, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    position = ForeignKeyField(Position, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=True)
    load_factor = FloatField(null=False)

    def save(self, *args, **kwargs):
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("Дата окончания должности не может быть раньше даты начала")
        return super().save(*args, **kwargs)

class Vacation(BaseModel):
    class Meta:
        db_table = "vacations"

    id = AutoField()
    employee = ForeignKeyField(Employee, backref='vacations', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    type = CharField(max_length=50, null=False)
    is_deleted = BooleanField(default=False) 

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValueError("Дата окончания отпуска не может быть раньше даты начала")
        if not self.type or not (1 <= len(str(self.type)) <= 50):
            raise ValueError("Длина типа отпуска должна быть от 1 до 50 символов")
        return super().save(*args, **kwargs)
    
    def soft_delete(self):
        """Мягкое удаление записи об отпуске"""
        if not self.is_deleted:
            self.is_deleted = True
            self.save()
            return True
        return False

class SickLeave(BaseModel):
    class Meta:
        db_table = "sick_leaves"

    id = AutoField()
    employee = ForeignKeyField(Employee, backref='sick_leaves', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    diagnosis = TextField(null=True)
    is_deleted = BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValueError("Дата окончания больничного не может быть раньше даты начала")
        if self.diagnosis and len(str(self.diagnosis)) > 500:
            raise ValueError("Длина диагноза не должна превышать 500 символов")
        return super().save(*args, **kwargs)
    
    def soft_delete(self):
        """Мягкое удаление записи о больничном"""
        if not self.is_deleted:
            self.is_deleted = True
            self.save()
            return True
        return False

def initialize_db():
    db.connect()
    db.create_tables([Employee, Position, EmployeePosition, Vacation, SickLeave], safe=True)
    db.close()

if __name__ == '__main__':
    initialize_db()
    # Заменено на английский язык, чтобы текст отображался корректно в любой консоли
    print("Database initialized. Tables created successfully.")
