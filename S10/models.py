from peewee import *
import datetime

db = SqliteDatabase('app.db')

class BaseModel(Model):
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    def deactivate(self):
        """Базовый метод мягкого удаления"""
        self.is_active = False
        self.save()
        return True

class Profile(BaseModel):
    full_name = CharField(max_length=255)
    
    class Meta:
        table_name = 'profiles'

class Position(BaseModel):
    # Убрано unique=True согласно требованиям
    title = CharField(max_length=255) 
    code = CharField(max_length=50, unique=True)
    department = CharField(max_length=100)

    class Meta:
        table_name = 'positions'

    def deactivate(self):
        """Проверка связей перед удалением. Возвращает True/False."""
        has_active_positions = EmployeePosition.select().where(
            (EmployeePosition.position == self) & 
            (EmployeePosition.is_active == True)
        ).exists()
        
        if has_active_positions:
            return False
            
        self.is_active = False
        self.save()
        return True

class EmployeePosition(BaseModel):
    profile = ForeignKeyField(Profile, backref='employee_positions')
    position = ForeignKeyField(Position, backref='employee_positions')
    start_date = DateField()
    end_date = DateField(null=True)
    rate = DecimalField(max_digits=3, decimal_places=2)
    is_primary = BooleanField(default=False)

    class Meta:
        table_name = 'employee_positions'

    def save(self, *args, **kwargs):
        # Валидация обязательности внешних ключей
        if not self.profile or not self.position:
            raise ValueError("Поля profile и position являются обязательными.")
            
        # Проверка корректности дат
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("Дата окончания не может быть раньше даты начала.")
            
        # Логика переключения основной ставки только при изменении флага на True
        if self.is_primary:
            existing_primary = EmployeePosition.get_or_none(
                (EmployeePosition.profile == self.profile) & 
                (EmployeePosition.is_primary == True) & 
                (EmployeePosition.id != self.id)
            )
            if existing_primary:
                EmployeePosition.update(is_primary=False).where(
                    (EmployeePosition.profile == self.profile) & 
                    (EmployeePosition.id != self.id) &
                    (EmployeePosition.is_primary == True)
                ).execute()
            
        super().save(*args, **kwargs)

    def update_position(self, new_position_id):
        """Смена должности с проверкой активных периодов"""
        active_leaves = Leave.select().where(
            (Leave.employee_position == self) & 
            (Leave.status == 'ACTIVE')
        ).exists()
        
        active_sick_leaves = SickLeave.select().where(
            (SickLeave.employee_position == self) & 
            (SickLeave.status == 'ACTIVE')
        ).exists()

        if active_leaves or active_sick_leaves:
            raise ValueError("Невозможно изменить должность: у сотрудника есть активные отпуска или больничные листы.")
        
        self.position_id = new_position_id
        self.save()

    def deactivate(self):
        """Мягкое удаление ставки"""
        self.is_active = False
        self.save()
        return True

class Leave(BaseModel):
    employee_position = ForeignKeyField(EmployeePosition, backref='leaves')
    start_date = DateField()
    end_date = DateField()
    leave_type = CharField(max_length=20)
    status = CharField(max_length=20)

    class Meta:
        table_name = 'leaves'

    def save(self, *args, **kwargs):
        if not self.employee_position:
            raise ValueError("Поле employee_position является обязательным.")
            
        if self.end_date < self.start_date:
            raise ValueError("Дата окончания не может быть раньше даты начала.")
            
        # Явная валидация перечислений
        valid_types = ['ANNUAL', 'UNPAID', 'STUDY']
        valid_statuses = ['PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELLED']
        
        if self.leave_type not in valid_types:
            raise ValueError(f"Недопустимый тип отпуска. Разрешены: {valid_types}")
        if self.status not in valid_statuses:
            raise ValueError(f"Недопустимый статус. Разрешены: {valid_statuses}")
            
        super().save(*args, **kwargs)

    def deactivate(self):
        """Мягкое удаление отпуска"""
        self.is_active = False
        self.save()
        return True

class SickLeave(BaseModel):
    employee_position = ForeignKeyField(EmployeePosition, backref='sick_leaves')
    start_date = DateField()
    end_date = DateField()
    certificate_number = CharField(max_length=50, unique=True)
    status = CharField(max_length=20)

    class Meta:
        table_name = 'sick_leaves'

    def save(self, *args, **kwargs):
        if not self.employee_position:
            raise ValueError("Поле employee_position является обязательным.")

        # Исправлено: разрешена ситуация end_date == start_date
        if self.end_date < self.start_date:
            raise ValueError("Дата окончания не может быть раньше даты начала.")
        
        # Явная валидация перечислений
        valid_statuses = ['OPEN', 'CLOSED', 'EXTENDED']
        if self.status not in valid_statuses:
            raise ValueError(f"Недопустимый статус. Разрешены: {valid_statuses}")
        
        super().save(*args, **kwargs)

    def deactivate(self):
        """Мягкое удаление больничного"""
        self.is_active = False
        self.save()
        return True