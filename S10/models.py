import datetime
from peewee import *

db = SqliteDatabase('employee_status.db')

# ---------- Валидаторы ----------
def validate_positive(value):
    if value <= 0:
        raise ValueError("user_id должен быть положительным целым числом")

def validate_hire_date(value):
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
    # Замечание 4: Добавлено значение по умолчанию 'active', как указано в doc.md
    status = CharField(max_length=20, default='active') 
    # Замечание 1, 3: Поле называется строго is_active (синхронизировано с doc.md)
    is_active = BooleanField(default=True)
    updated_at = DateTimeField(default=datetime.datetime.now) 

    def save(self, *args, **kwargs):
        """Валидация полей перед сохранением"""
        validate_positive(self.user_id)
        validate_hire_date(self.hire_date)
        
        # Замечание 2: Реализовано ограничение допустимых значений статуса
        allowed_statuses = ['active', 'on_vacation', 'sick_leave', 'fired']
        if self.status not in allowed_statuses:
            raise ValueError(f"Статус должен быть одним из: {', '.join(allowed_statuses)}")
            
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    # Замечание 5: Метод для автоматического формирования структуры positions для get_employee
    def get_positions_list(self):
        result = []
        query = (EmployeePosition
                 .select(EmployeePosition, Position)
                 .join(Position)
                 .where(EmployeePosition.employee == self))
        for ep in query:
            result.append({
                "position_title": ep.position.title,
                "start_date": ep.start_date.isoformat(),
                "end_date": ep.end_date.isoformat() if ep.end_date else None,
                "load_factor": round(ep.load_factor, 2)  # Округление до 2 знаков
            })
        return result

    # Замечание 6: Метод фильтрации сотрудников по position_id через соединение таблиц для list_employees
    @classmethod
    def get_by_position(cls, position_id):
        return (cls
                .select()
                .join(EmployeePosition)
                .where(EmployeePosition.position == position_id))

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
    # Замечание 8: Настройки on_delete='CASCADE' явно прописаны и соответствуют ERD
    employee = ForeignKeyField(Employee, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    position = ForeignKeyField(Position, backref='employee_positions_rel', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=True)
    # Замечание 7: Поле load_factor. В doc.md добавлено уточнение про формат (float, 2 знака после запятой)
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

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValueError("Дата окончания отпуска не может быть раньше даты начала")
        return super().save(*args, **kwargs)

class SickLeave(BaseModel):
    class Meta:
        db_table = "sick_leaves"

    id = AutoField()
    employee = ForeignKeyField(Employee, backref='sick_leaves', on_delete='CASCADE', null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    diagnosis = TextField(null=True)

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValueError("Дата окончания больничного не может быть раньше даты начала")
        return super().save(*args, **kwargs)

def init_db():
    db.connect()
    db.create_tables([Employee, Position, EmployeePosition, Vacation, SickLeave], safe=True)
    db.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized. Tables created successfully.")
