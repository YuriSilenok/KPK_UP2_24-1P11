import re
from peewee import Model, SqliteDatabase, CharField, BooleanField, DoesNotExist

# Подключение к базе данных
db = SqliteDatabase('departments.db')


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
    db.connect()
    db.create_tables([Department], safe=True)
    db.close()


def create_department(name: str, phone: str) -> Department:
    """
    Создание нового отделения.
    Поля name и phone - ОБЯЗАТЕЛЬНЫ.
    is_active автоматически устанавливается в True.
    """
    # Валидация имени
    if not Department.validate_name(name):
        raise ValueError("Название должно быть от 3 до 255 символов")

    # Валидация телефона (обязательное поле)
    if not phone:
        raise ValueError("Телефон обязателен для заполнения")
    if not Department.validate_phone(phone):
        raise ValueError("Телефон должен быть в формате +7XXXXXXXXXX (ровно 12 символов)")

    db.connect()
    try:
        # Проверка уникальности имени
        if Department.select().where(Department.name == name).exists():
            raise ValueError("Отделение с таким названием уже существует")

        department = Department.create(name=name, phone=phone, is_active=True)
        return department
    finally:
        db.close()


def get_department(dept_id: int) -> Department:
    """
    Получение ТОЛЬКО активного отделения (is_active = True).
    Удалённые (soft delete) не возвращаются.
    """
    db.connect()
    try:
        department = Department.get(
            (Department.id == dept_id) & (Department.is_active == True)
        )
        return department
    except DoesNotExist:
        raise ValueError("Отделение не найдено или удалено")
    finally:
        db.close()


def update_department(dept_id: int, name: str = None, phone: str = None, is_active: bool = None) -> Department:
    """
    Изменение сущности.
    Можно обновить name, phone или is_active по отдельности или вместе.
    """
    db.connect()
    try:
        # Проверяем существование записи
        department = Department.get_or_none(Department.id == dept_id)
        if department is None:
            raise ValueError("Отделение не найдено")

        # Обновление name
        if name is not None:
            if not Department.validate_name(name):
                raise ValueError("Название должно быть от 3 до 255 символов")
            # Проверка уникальности (исключая текущую запись)
            if Department.select().where(
                (Department.name == name) & (Department.id != dept_id)
            ).exists():
                raise ValueError("Отделение с таким названием уже существует")
            department.name = name

        # Обновление phone
        if phone is not None:
            if not phone:
                raise ValueError("Телефон не может быть пустым")
            if not Department.validate_phone(phone):
                raise ValueError("Телефон должен быть в формате +7XXXXXXXXXX")
            department.phone = phone

        # Обновление is_active (для мягкого удаления)
        if is_active is not None:
            department.is_active = is_active

        department.save()
        return department
    finally:
        db.close()


def delete_department(dept_id: int) -> dict:
    """
    Мягкое удаление (soft delete).
    Устанавливает is_active = False.
    Возвращает {'deleted': True} если запись была активной,
    и {'deleted': False} если запись не найдена или уже удалена.
    """
    db.connect()
    try:
        department = Department.get_or_none(
            (Department.id == dept_id) & (Department.is_active == True)
        )
        if department is None:
            return {'deleted': False}

        department.is_active = False
        department.save()
        return {'deleted': True}
    finally:
        db.close()


def list_departments(name: str = None, is_active: bool = None) -> list:
    """
    Получение списка отделений с фильтрацией.
    - name: поиск по части названия (регистронезависимо)
    - is_active: True - только активные, False - только удалённые, None - все записи
    """
    db.connect()
    try:
        query = Department.select()

        if name is not None:
            query = query.where(Department.name.contains(name))

        if is_active is not None:
            query = query.where(Department.is_active == is_active)

        return list(query)
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")