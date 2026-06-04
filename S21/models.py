from peewee import *
from peewee import IntegrityError

db = SqliteDatabase('holiday.db')

class BaseModel(Model):
    class Meta:
        database = db

class HolidayType(BaseModel):
    """Справочник типов: holiday (праздник) или vacation (каникулы)"""
    id = PrimaryKeyField()
    name = CharField(max_length=50, null=False)
    code = CharField(
        max_length=8,
        unique=True,
        null=False
    )
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'holiday_type'

    def save(self, *args, **kwargs):
        """Валидация при сохранении HolidayType"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("name не может быть пустым")
        if len(self.name) > 50:
            raise ValueError("name не должен превышать 50 символов")
        if not self.code or len(self.code.strip()) == 0:
            raise ValueError("code не может быть пустым")
        if len(self.code) > 8:
            raise ValueError("code не должен превышать 8 символов")
        try:
            return super().save(*args, **kwargs)
        except IntegrityError:
            raise ValueError("HolidayType с таким кодом уже существует")

    @staticmethod
    def create_holiday_type(name, code, is_active=True):
        """
        Создание нового типа праздника
        """
        if not name or len(name.strip()) == 0:
            raise ValueError("name не может быть пустым")
        if not code or len(code.strip()) == 0:
            raise ValueError("code не может быть пустым")
        
        holiday_type = HolidayType(
            name=name,
            code=code,
            is_active=is_active
        )
        try:
            holiday_type.save()
        except IntegrityError:
            raise ValueError("HolidayType с таким кодом уже существует")
        return holiday_type

    @staticmethod
    def update_holiday_type(holiday_type_id, name=None, code=None, is_active=None):
        """
        Изменение типа праздника по ID
        """
        try:
            holiday_type = HolidayType.get_by_id(holiday_type_id)
        except HolidayType.DoesNotExist:
            return None
        
        if name is not None:
            if len(name.strip()) == 0:
                raise ValueError("name не может быть пустым")
            holiday_type.name = name
        
        if code is not None:
            if len(code.strip()) == 0:
                raise ValueError("code не может быть пустым")
            holiday_type.code = code
        
        if is_active is not None:
            holiday_type.is_active = is_active
        
        try:
            holiday_type.save()
        except IntegrityError:
            raise ValueError("HolidayType с таким кодом уже существует")
        return holiday_type

    @staticmethod
    def delete_holiday_type(holiday_type_id):
        """
        Мягкое удаление типа праздника (установка is_active = False)
        Возвращает True, если тип был успешно деактивирован, иначе False
        """
        try:
            holiday_type = HolidayType.get_by_id(holiday_type_id)
            holiday_type.is_active = False
            holiday_type.save()
            return True
        except HolidayType.DoesNotExist:
            return False

    @staticmethod
    def get_holiday_type_by_id(holiday_type_id):
        """
        Получение типа праздника по ID
        """
        try:
            return HolidayType.get_by_id(holiday_type_id)
        except HolidayType.DoesNotExist:
            return None

    @staticmethod
    def get_holiday_types_list(is_active=True):
        """
        Получить список типов праздников
        """
        query = HolidayType.select()
        if is_active is not None:
            query = query.where(HolidayType.is_active == is_active)
        return query


class Holiday(BaseModel):
    """Праздники"""
    id = PrimaryKeyField()
    name = CharField(max_length=100, null=False)
    date = DateField(null=False, index=True)
    type = ForeignKeyField(HolidayType, backref='holidays', null=False, index=True)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'holiday'

    def save(self, *args, **kwargs):
        """Валидация при сохранении Holiday"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("name не может быть пустым")
        if len(self.name) > 100:
            raise ValueError("name не должен превышать 100 символов")
        if not self.date:
            raise ValueError("date не может быть пустым")
        return super().save(*args, **kwargs)

    @staticmethod
    def create_holiday(name, date, type_id, is_active=True):
        """
        Создание нового праздника
        """
        if not name or len(name.strip()) == 0:
            raise ValueError("name не может быть пустым")
        if not date:
            raise ValueError("date не может быть пустым")
        
        try:
            holiday_type = HolidayType.get_by_id(type_id)
        except HolidayType.DoesNotExist:
            raise ValueError("HolidayType с указанным ID не существует")
        
        holiday = Holiday(
            name=name,
            date=date,
            type=holiday_type,
            is_active=is_active
        )
        holiday.save()
        return holiday

    @staticmethod
    def update_holiday(holiday_id, name=None, date=None, type_id=None, is_active=None):
        """
        Изменение праздника по ID
        """
        try:
            holiday = Holiday.get_by_id(holiday_id)
        except Holiday.DoesNotExist:
            return None
        
        if name is not None:
            if len(name.strip()) == 0:
                raise ValueError("name не может быть пустым")
            holiday.name = name
        
        if date is not None:
            holiday.date = date
        
        if type_id is not None:
            try:
                holiday_type = HolidayType.get_by_id(type_id)
                holiday.type = holiday_type
            except HolidayType.DoesNotExist:
                raise ValueError("HolidayType с указанным ID не существует")
        
        if is_active is not None:
            holiday.is_active = is_active
        
        holiday.save()
        return holiday

    @staticmethod
    def delete_holiday(holiday_id):
        """
        Мягкое удаление праздника (установка is_active = False)
        Возвращает True, если праздник был успешно деактивирован, иначе False
        """
        try:
            holiday = Holiday.get_by_id(holiday_id)
            holiday.is_active = False
            holiday.save()
            return True
        except Holiday.DoesNotExist:
            return False

    @staticmethod
    def get_holiday_by_id(holiday_id):
        """
        Получение праздника по ID
        """
        try:
            return Holiday.get_by_id(holiday_id)
        except Holiday.DoesNotExist:
            return None

    @staticmethod
    def get_holidays_list(date_from=None, date_to=None, type_id=None, is_active=True):
        """
        Получить список праздников по заданным параметрам
        """
        query = Holiday.select()
        
        if is_active is not None:
            query = query.where(Holiday.is_active == is_active)
        
        if date_from is not None:
            query = query.where(Holiday.date >= date_from)
        
        if date_to is not None:
            query = query.where(Holiday.date <= date_to)
        
        if type_id is not None:
            query = query.where(Holiday.type == type_id)
        
        return query


class VacationPeriod(BaseModel):
    """Каникулы (период)"""
    id = PrimaryKeyField()
    name = CharField(max_length=100, null=False)
    start_date = DateField(null=False, index=True)
    end_date = DateField(null=False, index=True)
    type = ForeignKeyField(HolidayType, backref='vacations', null=False, index=True)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        table_name = 'vacation_period'

    def save(self, *args, **kwargs):
        """Валидация при сохранении VacationPeriod"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("name не может быть пустым")
        if len(self.name) > 100:
            raise ValueError("name не должен превышать 100 символов")
        if not self.start_date:
            raise ValueError("start_date не может быть пустым")
        if not self.end_date:
            raise ValueError("end_date не может быть пустым")
        if self.end_date < self.start_date:
            raise ValueError("end_date должен быть >= start_date")
        return super().save(*args, **kwargs)

    @staticmethod
    def create_vacation_period(name, start_date, end_date, type_id, is_active=True):
        """
        Создание нового периода каникул
        """
        if not name or len(name.strip()) == 0:
            raise ValueError("name не может быть пустым")
        if not start_date:
            raise ValueError("start_date не может быть пустым")
        if not end_date:
            raise ValueError("end_date не может быть пустым")
        if end_date < start_date:
            raise ValueError("end_date должен быть >= start_date")
        
        try:
            holiday_type = HolidayType.get_by_id(type_id)
        except HolidayType.DoesNotExist:
            raise ValueError("HolidayType с указанным ID не существует")
        
        vacation = VacationPeriod(
            name=name,
            start_date=start_date,
            end_date=end_date,
            type=holiday_type,
            is_active=is_active
        )
        vacation.save()
        return vacation

    @staticmethod
    def update_vacation_period(vacation_id, name=None, start_date=None, end_date=None, type_id=None, is_active=None):
        """
        Изменение периода каникул по ID
        """
        try:
            vacation = VacationPeriod.get_by_id(vacation_id)
        except VacationPeriod.DoesNotExist:
            return None
        
        if name is not None:
            if len(name.strip()) == 0:
                raise ValueError("name не может быть пустым")
            vacation.name = name
        
        if start_date is not None:
            vacation.start_date = start_date
        
        if end_date is not None:
            vacation.end_date = end_date
        
        # Проверка что end_date >= start_date после обновления
        if vacation.end_date < vacation.start_date:
            raise ValueError("end_date должен быть >= start_date")
        
        if type_id is not None:
            try:
                holiday_type = HolidayType.get_by_id(type_id)
                vacation.type = holiday_type
            except HolidayType.DoesNotExist:
                raise ValueError("HolidayType с указанным ID не существует")
        
        if is_active is not None:
            vacation.is_active = is_active
        
        vacation.save()
        return vacation

    @staticmethod
    def delete_vacation_period(vacation_id):
        """
        Мягкое удаление периода каникул (установка is_active = False)
        Возвращает True, если период был успешно деактивирован, иначе False
        """
        try:
            vacation = VacationPeriod.get_by_id(vacation_id)
            vacation.is_active = False
            vacation.save()
            return True
        except VacationPeriod.DoesNotExist:
            return False

    @staticmethod
    def get_vacation_period_by_id(vacation_id):
        """
        Получение периода каникул по ID
        """
        try:
            return VacationPeriod.get_by_id(vacation_id)
        except VacationPeriod.DoesNotExist:
            return None

    @staticmethod
    def get_vacation_periods_list(type_id=None, is_active=True):
        """
        Получить список периодов каникул
        """
        query = VacationPeriod.select()
        
        if is_active is not None:
            query = query.where(VacationPeriod.is_active == is_active)
        
        if type_id is not None:
            query = query.where(VacationPeriod.type == type_id)
        
        return query


def init_db():
    """
    Инициализация базы данных.
    Создаёт таблицы.
    """
    with db.atomic():
        db.create_tables([HolidayType, Holiday, VacationPeriod], safe=True)


if __name__ == '__main__':
    init_db()
    print("База данных создана.")
