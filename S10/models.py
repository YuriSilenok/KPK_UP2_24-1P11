import datetime as dt
import logging
from peewee import *

logger = logging.getLogger(__name__)
db = SqliteDatabase('app.db')

# Константы для валидации перечислений
LEAVE_TYPES = ("ANNUAL", "UNPAID", "STUDY")
LEAVE_STATUSES = ("PLANNED", "ACTIVE", "COMPLETED", "CANCELLED")
SICK_LEAVE_STATUSES = ("OPEN", "CLOSED", "EXTENDED")


class ApiError(Exception):
    """Базовое исключение API с кодом ответа."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(ApiError):
    """Запись не найдена (404)."""
    def __init__(self, message: str = "Сущность не найдена"):
        super().__init__(message, status_code=404)


class ValidationError(ApiError):
    """Ошибка валидации входных данных (400)."""
    def __init__(self, message: str = "Ошибка валидации входных данных"):
        super().__init__(message, status_code=400)


class ConflictError(ApiError):
    """Конфликт бизнес-логики (409)."""
    def __init__(self, message: str = "Конфликт бизнес-логики"):
        super().__init__(message, status_code=409)


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

    @classmethod
    def get_active(cls, pk):
        obj = cls.get_or_none((cls.id == pk) & (cls.is_active == True))
        if not obj:
            raise NotFoundError("Должность не найдена или неактивна.")
        return obj

    def save(self, *args, **kwargs):
        if len(self.title) > 255:
            raise ValidationError("Название должности не может превышать 255 символов.")
        if len(self.code) > 50:
            raise ValidationError("Код должности не может превышать 50 символов.")
        if len(self.department) > 100:
            raise ValidationError("Подразделение не может превышать 100 символов.")

        if self.code:
            existing = Position.select().where(
                (Position.code == self.code) &
                (Position.is_active == True) &
                (Position.id != self.id)
            ).exists()
            if existing:
                raise ConflictError("Код должности уже существует среди активных записей.")
        super().save(*args, **kwargs)

    def deactivate(self):
        has_active = EmployeePosition.select().where(
            (EmployeePosition.position == self) &
            (EmployeePosition.is_active == True)
        ).exists()

        if has_active:
            logger.warning(f"Невозможно удалить должность {self.id}: есть активные ставки")
            raise ConflictError("Невозможно удалить должность: есть активные связанные ставки сотрудников.")

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

    @classmethod
    def get_active(cls, pk):
        obj = cls.get_or_none((cls.id == pk) & (cls.is_active == True))
        if not obj:
            raise NotFoundError("Ставка сотрудника не найдена или неактивна.")
        return obj

    def save(self, *args, **kwargs):
        if not self.profile or not Profile.get_or_none(Profile.id == self.profile_id):
            raise ValidationError("Профиль сотрудника не существует.")
        if not self.position or not Position.get_or_none(Position.id == self.position_id):
            raise ValidationError("Должность не существует.")

        if self.start_date > dt.date.today():
            raise ValidationError("Дата начала ставки не может быть в будущем.")

        if not (0.1 <= self.rate <= 2.0):
            raise ValidationError("Коэффициент ставки должен быть в диапазоне [0.1; 2.0].")

        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("Дата окончания не может быть раньше даты начала.")

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
            raise NotFoundError("Указанная должность не существует или неактивна.")

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
            raise ConflictError(
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

    @classmethod
    def get_active(cls, pk):
        obj = cls.get_or_none((cls.id == pk) & (cls.is_active == True))
        if not obj:
            raise NotFoundError("Отпуск не найден или неактивен.")
        return obj

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
            raise ValidationError("Ставка сотрудника не существует.")

        if self.start_date > dt.date.today():
            raise ValidationError("Дата начала отпуска не может быть в будущем.")

        if self.end_date < self.start_date:
            raise ValidationError("Дата окончания не может быть раньше даты начала.")

        if self.leave_type not in LEAVE_TYPES:
            raise ValidationError(f"Недопустимый тип отпуска. Разрешены: {LEAVE_TYPES}")
        if self.status not in LEAVE_STATUSES:
            raise ValidationError(f"Недопустимый статус. Разрешены: {LEAVE_STATUSES}")

        if self._check_overlap():
            raise ConflictError(
                "Период отпуска пересекается с существующими активными отпусками или больничными."
            )

        super().save(*args, **kwargs)

    def deactivate(self):
        # Проверка возможности удаления: нельзя удалить отпуск, если он ACTIVE
        if self.status == "ACTIVE":
            raise ConflictError("Невозможно удалить активный отпуск. Сначала измените его статус.")
        
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

    @classmethod
    def get_active(cls, pk):
        obj = cls.get_or_none((cls.id == pk) & (cls.is_active == True))
        if not obj:
            raise NotFoundError("Больничный не найден или неактивен.")
        return obj

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
            raise ValidationError("Ставка сотрудника не существует.")

        if self.start_date > dt.date.today():
            raise ValidationError("Дата начала больничного не может быть в будущем.")

        if self.end_date < self.start_date:
            raise ValidationError("Дата окончания не может быть раньше даты начала.")

        if self.status not in SICK_LEAVE_STATUSES:
            raise ValidationError(f"Недопустимый статус. Разрешены: {SICK_LEAVE_STATUSES}")

        if self.certificate_number:
            existing = SickLeave.select().where(
                (SickLeave.certificate_number == self.certificate_number) &
                (SickLeave.is_active == True) &
                (SickLeave.id != self.id)
            ).exists()
            if existing:
                raise ConflictError(
                    "Номер листка нетрудоспособности уже существует среди активных записей."
                )

        if self._check_overlap():
            raise ConflictError(
                "Период больничного пересекается с существующими активными больничными или отпусками."
            )

        super().save(*args, **kwargs)

    def deactivate(self):
        # Проверка возможности удаления: нельзя удалить открытый больничный
        if self.status == "OPEN":
            raise ConflictError("Невозможно удалить открытый больничный. Сначала закройте его.")
        
        self.is_active = False
        self.save()
        return True
