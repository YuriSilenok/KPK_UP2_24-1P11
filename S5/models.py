import re
from peewee import Model, SqliteDatabase, CharField, BooleanField, DoesNotExist

# Подключение к базе данных
db = SqliteDatabase('departments.db')


class DepartmentNotFoundError(Exception):
    """Исключение, когда отделение не найдено"""
    pass


class ValidationError(Exception):
    """Исключение при ошибке валидации данных"""
    pass


class Department(Model):
    """Модель отделения СПО"""
    name = CharField(max_length=255, unique=True)
    phone = CharField(max_length=12)
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = 'departments'

    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Проверка формата телефона: +7XXXXXXXXXX (ровно 12 символов)"""
        return bool(re.match(r'^\+7\d{10}$', phone))

    @classmethod
    def validate_name(cls, name: str) -> bool:
        """Проверка длины названия: от 3 до 255 символов"""
        return 3 <= len(name) <= 255


def init_db():
    """Инициализация базы данных"""
    with db:
        db.create_tables([Department], safe=True)


def create_department(name: str, phone: str) -> Department:
    """
    Создание нового отделения.
    Поля name и phone - ОБЯЗАТЕЛЬНЫ.
    is_active автоматически устанавливается в True.
    """
    # Валидация имени
    if not Department.validate_name(name):
        raise ValidationError("Название должно быть от 3 до 255 символов")

    # Валидация телефона (обязательное поле)
    if not phone:
        raise ValidationError("Телефон обязателен для заполнения")
    if not Department.validate_phone(phone):
        raise ValidationError("Телефон должен быть в формате +7XXXXXXXXXX (ровно 12 символов)")

    with db:
        # Проверка уникальности имени
        if Department.select().where(Department.name == name).exists():
            raise ValidationError("Отделение с таким названием уже существует")

        department = Department.create(name=name, phone=phone, is_active=True)
        return department


def get_department(dept_id: int) -> Department:
    """
    Получение ТОЛЬКО активного отделения (is_active = True).
    Удалённые (soft delete) не возвращаются.
    """
    with db:
        try:
            department = Department.get(
                (Department.id == dept_id) & (Department.is_active == True)
            )
            return department
        except DoesNotExist:
            raise DepartmentNotFoundError("Отделение не найдено или удалено")


def update_department(dept_id: int, name: str = None, phone: str = None, is_active: bool = None) -> Department:
    """
    Изменение сущности.
    Можно обновить name, phone или is_active по отдельности или вместе.
    phone может быть передан как None (не менять) или новая строка (должна быть валидной).
    """
    with db:
        # Проверяем существование записи
        department = Department.get_or_none(Department.id == dept_id)
        if department is None:
            raise DepartmentNotFoundError("Отделение не найдено")

        # Обновление name
        if name is not None:
            if not Department.validate_name(name):
                raise ValidationError("Название должно быть от 3 до 255 символов")
            # Проверка уникальности (исключая текущую запись)
            if Department.select().where(
                (Department.name == name) & (Department.id != dept_id)
            ).exists():
                raise ValidationError("Отделение с таким названием уже существует")
            department.name = name

        # Обновление phone (только если передан не None)
        if phone is not None:
            if not Department.validate_phone(phone):
                raise ValidationError("Телефон должен быть в формате +7XXXXXXXXXX")
            department.phone = phone

        # Обновление is_active (для мягкого удаления)
        if is_active is not None:
            department.is_active = is_active

        department.save()
        return department


def delete_department(dept_id: int) -> dict:
    """
    Мягкое удаление (soft delete).
    Устанавливает is_active = False.
    Возвращает {'deleted': True} если запись была активной,
    и {'deleted': False} если запись не найдена или уже удалена.
    """
    with db:
        department = Department.get_or_none(
            (Department.id == dept_id) & (Department.is_active == True)
        )
        if department is None:
            return {'deleted': False}

        department.is_active = False
        department.save()
        return {'deleted': True}


def list_departments(name: str = None, is_active: bool = None) -> list:
    """
    Получение списка отделений с фильтрацией.
    - name: поиск по части названия (регистронезависимо)
    - is_active: True - только активные, False - только удалённые, None - все записи
    """
    with db:
        query = Department.select()

        if name is not None:
            query = query.where(Department.name.contains(name))

        if is_active is not None:
            query = query.where(Department.is_active == is_active)

        return list(query)


# Для удобства, чтобы не импортировать исключения отдельно
__all__ = [
    'init_db',
    'create_department',
    'get_department',
    'update_department',
    'delete_department',
    'list_departments',
    'Department',
    'DepartmentNotFoundError',
    'ValidationError'
]


if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")