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
    title = CharField(max_length=255) 
    # Убрано unique=True, проверка уникальности code с учетом is_active в save()
    code = CharField(max_length=50)
    department = CharField(max_length=100)

    class Meta:
        table_name = 'positions'

    def save(self, *args, **kwargs):
        # Проверка уникальности code только среди активных записей
        if self.code:
            existing = Position.select().where(
                (Position.code == self.code) & 
                (Position.is_active == True) & 
                (Position.id != self.id)
            ).exists()
            if existing:
                raise ValueError("Код должности уже существует среди активных записей.")
        super().save(*args, **kwargs)

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
            
        # Валидация даты начала (не в будущем)
        if self.start_date > datetime.date.today():
            raise ValueError("Дата начала ставки не может быть в будущем.")
            
        # Валидация диапазона rate
        if not (0.1 <= self.rate <= 2.0):
            raise ValueError("Коэффициент ставки должен быть в диапазоне [0.1; 2.0].")
            
        # Проверка корректности дат
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("Дата окончания не может быть раньше даты начала.")
            
        # Логика переключения основной ставки
        if self.is_primary:
            EmployeePosition.update(is_primary=False).where(
                (EmployeePosition.profile == self.profile) & 
                (EmployeePosition.id != self.id) &
                (EmployeePosition.is_active == True) &
                (EmployeePosition.is_primary == True)
            ).execute()
            
        super().save(*args, **kwargs)

    def update_position(self, new_position_id):
        """Смена должности с проверкой существования и активных периодов"""
        # Проверка существования новой должности
        if not Position.get_or_none((Position.id == new_position_id) & (Position.is_active == True)):
            raise ValueError("Указанная должность не существует или неактивна.")

        active_leaves = Leave.select().where(
            (Leave.employee_position == self) & 
            (Leave.status == 'ACTIVE') &
            (Leave.is_active == True)
        ).exists()
        
        active_sick_leaves = SickLeave.select().where(
            (SickLeave.employee_position == self) & 
            (SickLeave.status == 'ACTIVE') &
            (SickLeave.is_active == True)
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
    status = CharField(max_length=20, default='PLANNED')

    class Meta:
        table_name = 'leaves'

    def save(self, *args, **kwargs):
        if not self.employee_position:
            raise ValueError("Поле employee_position является обязательным.")
            
        if self.end_date < self.start_date:
            raise ValueError("Дата окончания не может быть раньше даты начала.")
            
        # Валидация перечислений
        valid_types = ['ANNUAL', 'UNPAID', 'STUDY']
        valid_statuses = ['PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELLED']
        
        if self.leave_type not in valid_types:
            raise ValueError(f"Недопустимый тип отпуска. Разрешены: {valid_types}")
        if self.status not in valid_statuses:
            raise ValueError(f"Недопустимый статус. Разрешены: {valid_statuses}")

        # Проверка пересечения периодов с другими активными записями
        overlapping_leave = Leave.select().where(
            (Leave.employee_position == self.employee_position) &
            (Leave.is_active == True) &
            (Leave.id != self.id) &
            (
                ((Leave.start_date <= self.start_date) & (Leave.end_date >= self.start_date)) |
                ((Leave.start_date <= self.end_date) & (Leave.end_date >= self.end_date)) |
                ((Leave.start_date >= self.start_date) & (Leave.end_date <= self.end_date))
            )
        ).exists()

        overlapping_sick = SickLeave.select().where(
            (SickLeave.employee_position == self.employee_position) &
            (SickLeave.is_active == True) &
            (
                ((SickLeave.start_date <= self.start_date) & (SickLeave.end_date >= self.start_date)) |
                ((SickLeave.start_date <= self.end_date) & (SickLeave.end_date >= self.end_date)) |
                ((SickLeave.start_date >= self.start_date) & (SickLeave.end_date <= self.end_date))
            )
        ).exists()

        if overlapping_leave or overlapping_sick:
            raise ValueError("Период отпуска пересекается с существующими активными отпусками или больничными.")
            
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
    # Убрано unique=True, проверка уникальности certificate_number с учетом is_active в save()
    certificate_number = CharField(max_length=50)
    status = CharField(max_length=20)

    class Meta:
        table_name = 'sick_leaves'

    def save(self, *args, **kwargs):
        if not self.employee_position:
            raise ValueError("Поле employee_position является обязательным.")

        if self.end_date < self.start_date:
            raise ValueError("Дата окончания не может быть раньше даты начала.")
        
        # Валидация перечислений
        valid_statuses = ['OPEN', 'CLOSED', 'EXTENDED']
        if self.status not in valid_statuses:
            raise ValueError(f"Недопустимый статус. Разрешены: {valid_statuses}")

        # Проверка уникальности номера листа среди активных записей
        if self.certificate_number:
            existing_cert = SickLeave.select().where(
                (SickLeave.certificate_number == self.certificate_number) &
                (SickLeave.is_active == True) &
                (SickLeave.id != self.id)
            ).exists()
            if existing_cert:
                raise ValueError("Номер листка нетрудоспособности уже существует среди активных записей.")

        # Проверка пересечения периодов с другими активными записями
        overlapping_sick = SickLeave.select().where(
            (SickLeave.employee_position == self.employee_position) &
            (SickLeave.is_active == True) &
            (SickLeave.id != self.id) &
            (
                ((SickLeave.start_date <= self.start_date) & (SickLeave.end_date >= self.start_date)) |
                ((SickLeave.start_date <= self.end_date) & (SickLeave.end_date >= self.end_date)) |
                ((SickLeave.start_date >= self.start_date) & (SickLeave.end_date <= self.end_date))
            )
        ).exists()

        overlapping_leave = Leave.select().where(
            (Leave.employee_position == self.employee_position) &
            (Leave.is_active == True) &
            (
                ((Leave.start_date <= self.start_date) & (Leave.end_date >= self.start_date)) |
                ((Leave.start_date <= self.end_date) & (Leave.end_date >= self.end_date)) |
                ((Leave.start_date >= self.start_date) & (Leave.end_date <= self.end_date))
            )
        ).exists()

        if overlapping_sick or overlapping_leave:
            raise ValueError("Период больничного пересекается с существующими активными больничными или отпусками.")
        
        super().save(*args, **kwargs)

    def deactivate(self):
        """Мягкое удаление больничного"""
        self.is_active = False
        self.save()
        return True
