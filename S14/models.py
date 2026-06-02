from peewee import SqliteDatabase, Model, IntegerField, FloatField, BooleanField, PrimaryKeyField, Check, IntegrityError
from contextlib import contextmanager

# Инициализация базы данных
db = SqliteDatabase('workload.db')

@contextmanager
def db_transaction():
    """Контекстный менеджер для транзакций"""
    with db.atomic():
        yield


class CalculatedLoad(Model):
    id = PrimaryKeyField()
    teacher_id = IntegerField(null=False, constraints=[Check('teacher_id > 0')])
    period_id = IntegerField(null=False, constraints=[Check('period_id > 0')])
    total_hours = FloatField(null=False, default=0.0, constraints=[Check('total_hours >= 0')])
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        # Замечание 1: Унифицировали название таблицы в соответствии с doc.md
        table_name = 'calculated_load'
        indexes = ((('teacher_id', 'period_id'), True),)

    def to_response(self):
        """Возвращает словарь только с полями, указанными в doc.md"""
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'period_id': self.period_id,
            'total_hours': self.total_hours
        }


class UniqueConstraintError(Exception):
    """Исключение для нарушения уникальности"""
    pass


def init_db():
    """Функция инициализирующая БД"""
    db.connect()
    db.create_tables([CalculatedLoad], safe=True)
    db.close()


def get_active_loads(teacher_id=None, period_id=None, limit=100, offset=0):
    # Валидация параметров до построения запроса
    if limit < 1 or limit > 1000:
        raise ValueError("limit должен быть в диапазоне 1-1000")
    if offset < 0:
        raise ValueError("offset должен быть >= 0")
    if teacher_id is not None and teacher_id <= 0:
        raise ValueError("teacher_id должен быть > 0")
    if period_id is not None and period_id <= 0:
        raise ValueError("period_id должен быть > 0")
    
    query = CalculatedLoad.select().where(CalculatedLoad.is_active == True)
    if teacher_id is not None:
        query = query.where(CalculatedLoad.teacher_id == teacher_id)
    if period_id is not None:
        query = query.where(CalculatedLoad.period_id == period_id)
    
    return [load.to_response() for load in query.offset(offset).limit(limit)]


def get_active_load_by_id(load_id):
    # Замечание 7: Явная валидация входного идентификатора
    if load_id <= 0:
        raise ValueError("load_id должен быть > 0")
        
    # Замечание 2: Перехватываем строго исключение DoesNotExist вместо общего Exception
    try:
        load = CalculatedLoad.get((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
        return load.to_response()
    except CalculatedLoad.DoesNotExist:
        return None


def create_load(teacher_id, period_id, total_hours=None):
    """
    Добавить CalculatedLoad.
    
    Замечание 6: Если параметр total_hours не передан (равен None), 
    ему автоматически присваивается значение по умолчанию 0.0, как требует doc.md.
    """
    if teacher_id <= 0:
        raise ValueError("teacher_id должен быть > 0")
    if period_id <= 0:
        raise ValueError("period_id должен быть > 0")
    
    if total_hours is None:
        total_hours = 0.0
    if total_hours < 0:
        raise ValueError("total_hours должен быть >= 0")
    
    with db_transaction():
        # Замечание 5: Явная проверка уникальности до вызова create()
        # Ищем вообще любую запись с этой парой ключей (даже удаленную)
        existing = CalculatedLoad.get_or_none(
            (CalculatedLoad.teacher_id == teacher_id) & 
            (CalculatedLoad.period_id == period_id)
        )
        
        if existing:
            # Если запись есть и она активна — это жесткий конфликт уникальности
            if existing.is_active:
                raise UniqueConstraintError(
                    f"Запись уже существует для teacher_id={teacher_id} и period_id={period_id}"
                )
            else:
                # Если запись была мягко удалена (is_active=False), то вместо создания дубля
                # мы её «реанимируем» и обновляем часы. Так мы не поймаем IntegrityError от БД.
                existing.total_hours = total_hours
                existing.is_active = True
                existing.save()
                return existing.to_response()
        
        try:
            load = CalculatedLoad.create(
                teacher_id=teacher_id,
                period_id=period_id,
                total_hours=total_hours,
                is_active=True
            )
            return load.to_response()
        except IntegrityError:
            raise UniqueConstraintError(
                f"Ошибка уникальности: пара teacher_id={teacher_id} и period_id={period_id} уже занята"
            )


def update_load(load_id, total_hours=None):
    # Замечание 7: Явная валидация load_id
    if load_id <= 0:
        raise ValueError("load_id должен быть > 0")
        
    if total_hours is not None and total_hours < 0:
        raise ValueError("total_hours должен быть >= 0")
        
    with db_transaction():
        # Замечания 3 и 4: Получаем запись ДО обновления (проверка существования + защита от race condition)
        load = CalculatedLoad.get_or_none((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
        if not load:
            return None  # Четкий возврат None, если записи нет или она архивирована
            
        # Если total_hours не передан, ничего не меняем, возвращаем текущее состояние
        if total_hours is None:
            return load.to_response()
            
        load.total_hours = total_hours
        load.save()
        return load.to_response()


def delete_load(load_id):
    # Замечание 7: Явная валидация load_id
    if load_id <= 0:
        raise ValueError("load_id должен быть > 0")
        
    with db_transaction():
        # Замечание 4: Сначала проверяем состояние записи, чтобы избежать race condition
        load = CalculatedLoad.get_or_none((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
        if not load:
            return False
            
        # Надежное обновление через execute(), гарантирующее точный результат для бота
        query = CalculatedLoad.update(is_active=False).where(
            (CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True)
        )
        rows_updated = query.execute()
        return rows_updated > 0


if __name__ == '__main__':
    init_db()
    print("Таблица calculated_load успешно создана и готова к работе.")
