import datetime as dt
import logging
from peewee import *

logger = logging.getLogger(__name__)
db = SqliteDatabase('app.db')

# Константы для валидации перечислений
LEAVE_TYPES = ("ANNUAL", "UNPAID", "STUDY")
LEAVE_STATUSES = ("PLANNED", "ACTIVE", "COMPLETED", "CANCELLED")
SICK_LEAVE_STATUSES = ("OPEN", "CLOSED", "EXTENDED")


class BaseModel(Model):
    """Базовая модель с поддержкой мягкого удаления и временных меток."""
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=dt.datetime.now)
    updated_at = DateTimeField(default=dt.datetime.now)

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        self.updated_at = dt.datetime.now()
        return super().save(*args, **kwargs)

    def deactivate(self):
        """Мягкое удаление записи. Возвращает True при успехе."""
        self.is_active = False
        self.save()
        return True


class Profile(BaseModel):
    """Профиль сотрудника."""
    full_name = CharField(max_length=255)

    class Meta:
        table_name = "profiles"


class Position(BaseModel):
    """Справочник должностей."""
    title = CharField(max_length=255)
    code = CharField(max_length=50)
    department = CharField(max_length=100)

    class Meta:
        table_name = "positions"

    def save(self, *args, **kwargs):
        if len(self.title) > 255:
            raise ValueError("Название должности не может превышать 255 символов.")
        if len(self.code) > 50:
            raise ValueError("Код должности не может превышать 50 символов.")
        if len(self.department) > 100:
            raise ValueError("Подразделение не может превышать 100 символов.")
            
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
        has_active = EmployeePosition.select().where(
            (EmployeePosition.position == self) &
            (EmployeePosition.is_active == True)
        ).exists()

        if has_active:
            logger.warning(f"Невозможно удалить должность {self.id}: есть активные ставки")
            return False

        self.is_active = False
        self.save()
        return True


class EmployeePosition(BaseModel):
    """Ставка сотрудника."""
    profile = ForeignKeyField(Profile, backref="employee_positions")
    position = ForeignKeyField(Position, backref="employee_positions")
    start_date = DateField()
    end_date = DateField(null=True)
    rate = DecimalField(max_digits=3, decimal_places=2)
    is_primary = BooleanField(default=False)

    class Meta:
        table_name = "employee_positions"

    def save(self, *args, **kwargs):
        # Явная проверка существования внешних ключей
        if not self.profile or not Profile.get_or_none(Profile.id == self.profile_id):
            raise ValueError("Профиль сотрудника не существует.")
        if not self.position or not Position.get_or_none(Position.id == self.position_id):
            raise ValueError("Должность не существует.")

        if self.start_date > dt.date.today():
            raise ValueError("Дата начала ставки не может быть в будущем.")

        if not (0.1 <= self.rate <= 2.0):
            raise ValueError("Коэффициент ставки должен быть в диапазоне [0.1; 2.0].")

        if self.end_date and self.end_date < self.start_date:
            raise ValueError("Дата окончания не может быть раньше даты начала.")

        # Транзакция для гарантии атомарности переключения основной ставки
        with db.atomic():
            if self.is_primary:
                EmployeePosition.update(is_primary=False).where(
                    (EmployeePosition.profile == self.profile) &
                    (EmployeePosition.id != self.id) &
                    (EmployeePosition.is_active == True) &
                    (EmployeePosition.is_primary == True)
                ).execute()
            super().save(*args, **kwargs)

    def update_position(self, new_position_id):
        if self.position_id == new_position_id:
            return
            
        pos = Position.get_or_none(
            (Position.id == new_position_id) & (Position.is_active == True)
        )
        if not pos:
            raise ValueError("Указанная должность не существует или неактивна.")

        active_leaves = Leave.select().where(
            (Leave.employee_position == self) &
            (Leave.status == "ACTIVE") &
            (Leave.is_active == True)
        ).exists()

        active_sick = SickLeave.select().where(
            (SickLeave.employee_position == self) &
            (SickLeave.status == "ACTIVE") &
            (SickLeave.is_active == True)
        ).exists()

        if active_leaves or active_sick:
            raise ValueError(
                "Невозможно изменить должность: у сотрудника есть активные отпуска или больничные листы."
            )

        self.position_id = new_position_id
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()
        return True


class Leave(BaseModel):
    """Отпуск сотрудника."""
    employee_position = ForeignKeyField(EmployeePosition, backref="leaves")
    start_date = DateField()
    end_date = DateField()
    leave_type = CharField(max_length=20)
    status = CharField(max_length=20, default="PLANNED")

    class Meta:
        table_name = "leaves"

    def _check_overlap(self):
        overlap_leave = Leave.select().where(
            (Leave.employee_position == self.employee_position) &
            (Leave.is_active == True) &
            (Leave.id != self.id) &
            (Leave.start_date <= self.end_date) &
            (Leave.end_date >= self.start_date)
        ).exists()

        overlap_sick = SickLeave.select().where(
            (SickLeave.employee_position == self.employee_position) &
            (SickLeave.is_active == True) &
            (SickLeave.start_date <= self.end_date) &
            (SickLeave.end_date >= self.start_date)
        ).exists()

        return overlap_leave or overlap_sick

    def save(self, *args, **kwargs):
        if not self.employee_position or not EmployeePosition.get_or_none(EmployeePosition.id == self.employee_position_id):
            raise ValueError("Ставка сотрудника не существует.")

        if self.start_date > dt.date.today():
            raise ValueError("Дата начала отпуска не может быть в будущем.")

        if self.end_date < self.start_date:
            raise ValueError("Дата окончания не может быть раньше даты начала.")

        if self.leave_type not in LEAVE_TYPES:
            raise ValueError(f"Недопустимый тип отпуска. Разрешены: {LEAVE_TYPES}")
        if self.status not in LEAVE_STATUSES:
            raise ValueError(f"Недопустимый статус. Разрешены: {LEAVE_STATUSES}")

        if self._check_overlap():
            raise ValueError(
                "Период отпуска пересекается с существующими активными отпусками или больничными."
            )

        super().save(*args, **kwargs)

    def deactivate(self):
        self.is_active = False
        self.save()
        return True


class SickLeave(BaseModel):
    """Больничный лист."""
    employee_position = ForeignKeyField(EmployeePosition, backref="sick_leaves")
    start_date = DateField()
    end_date = DateField()
    certificate_number = CharField(max_length=50)
    status = CharField(max_length=20, default="OPEN")

    class Meta:
        table_name = "sick_leaves"

    def _check_overlap(self):
        overlap_sick = SickLeave.select().where(
            (SickLeave.employee_position == self.employee_position) &
            (SickLeave.is_active == True) &
            (SickLeave.id != self.id) &
            (SickLeave.start_date <= self.end_date) &
            (SickLeave.end_date >= self.start_date)
        ).exists()

        overlap_leave = Leave.select().where(
            (Leave.employee_position == self.employee_position) &
            (Leave.is_active == True) &
            (Leave.start_date <= self.end_date) &
            (Leave.end_date >= self.start_date)
        ).exists()

        return overlap_sick or overlap_leave

    def save(self, *args, **kwargs):
        if not self.employee_position or not EmployeePosition.get_or_none(EmployeePosition.id == self.employee_position_id):
            raise ValueError("Ставка сотрудника не существует.")

        if self.start_date > dt.date.today():
            raise ValueError("Дата начала больничного не может быть в будущем.")

        if self.end_date < self.start_date:
            raise ValueError("Дата окончания не может быть раньше даты начала.")

        if self.status not in SICK_LEAVE_STATUSES:
            raise ValueError(f"Недопустимый статус. Разрешены: {SICK_LEAVE_STATUSES}")

        if self.certificate_number:
            existing = SickLeave.select().where(
                (SickLeave.certificate_number == self.certificate_number) &
                (SickLeave.is_active == True) &
                (SickLeave.id != self.id)
            ).exists()
            if existing:
                raise ValueError(
                    "Номер листка нетрудоспособности уже существует среди активных записей."
                )

        if self._check_overlap():
            raise ValueError(
                "Период больничного пересекается с существующими активными больничными или отпусками."
            )

        super().save(*args, **kwargs)

    def deactivate(self):
        self.is_active = False
        self.save()
        return True
