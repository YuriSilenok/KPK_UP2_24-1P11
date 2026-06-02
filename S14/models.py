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
    discipline_id = IntegerField(null=False, constraints=[Check('discipline_id > 0')])
    group_id = IntegerField(null=False, constraints=[Check('group_id > 0')])
    total_hours = FloatField(null=False, default=0.0, constraints=[Check('total_hours >= 0')])
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = 'calculated_load'
        # Уникальная комбинация по обновлённому ТЗ из doc.md
        indexes = ((('teacher_id', 'period_id', 'discipline_id', 'group_id'), True),)

    def to_response(self):
        """Возвращает словарь только с полями, указанными в doc.md"""
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'period_id': self.period_id,
            'discipline_id': self.discipline_id,
            'group_id': self.group_id,
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


def get_active_loads(teacher_id=None, period_id=None, discipline_id=None, group_id=None, limit=100, offset=0):
    # Валидация параметров до построения запроса
    if limit < 1 or limit > 1000:
        raise ValueError("limit должен быть в диапазоне 1-1000")
    if offset < 0:
        raise ValueError("offset должен быть >= 0")
    if teacher_id is not None and teacher_id <= 0:
        raise ValueError("teacher_id должен быть > 0")
    if period_id is not None and period_id <= 0:
        raise ValueError("period_id должен быть > 0")
    if discipline_id is not None and discipline_id <= 0:
        raise ValueError("discipline_id должен быть > 0")
    if group_id is not None and group_id <= 0:
        raise ValueError("group_id должен быть > 0")
    
    query = CalculatedLoad.select().where(CalculatedLoad.is_active == True)
    if teacher_id is not None:
        query = query.where(CalculatedLoad.teacher_id == teacher_id)
    if period_id is not None:
        query = query.where(CalculatedLoad.period_id == period_id)
    if discipline_id is not None:
        query = query.where(CalculatedLoad.discipline_id == discipline_id)
    if group_id is not None:
        query = query.where(CalculatedLoad.group_id == group_id)
    
    return [load.to_response() for load in query.offset(offset).limit(limit)]


def get_active_load_by_id(load_id):
    if load_id <= 0:
        raise ValueError("load_id должен быть > 0")
        
    try:
        load = CalculatedLoad.get((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
        return load.to_response()
    except CalculatedLoad.DoesNotExist:
        return None


def create_load(teacher_id, period_id, discipline_id, group_id, total_hours=None):
    """
    Добавить CalculatedLoad.
    Если параметр total_hours не передан, ставится 0.0 по умолчанию.
    """
    if teacher_id <= 0:
        raise ValueError("teacher_id должен быть > 0")
    if period_id <= 0:
        raise ValueError("period_id должен быть > 0")
    if discipline_id <= 0:
        raise ValueError("discipline_id должен быть > 0")
    if group_id <= 0:
        raise ValueError("group_id должен быть > 0")
    
    if total_hours is None:
        total_hours = 0.0
    if total_hours < 0:
        raise ValueError("total_hours должен быть >= 0")
    
    with db_transaction():
        # Проверка уникальности комбинации четырёх параметров
        existing = CalculatedLoad.get_or_none(
            (CalculatedLoad.teacher_id == teacher_id) & 
            (CalculatedLoad.period_id == period_id) &
            (CalculatedLoad.discipline_id == discipline_id) &
            (CalculatedLoad.group_id == group_id)
        )
        
        if existing:
            if existing.is_active:
                raise UniqueConstraintError(
                    f"Запись уже существует для teacher={teacher_id}, period={period_id}, discipline={discipline_id}, group={group_id}"
                )
            else:
                # Реанимируем мягко удалённую запись, чтобы избежать конфликтов в СУБД
                existing.total_hours = total_hours
                existing.is_active = True
                existing.save()
                return existing.to_response()
        
        try:
            load = CalculatedLoad.create(
                teacher_id=teacher_id,
                period_id=period_id,
                discipline_id=discipline_id,
                group_id=group_id,
                total_hours=total_hours,
                is_active=True
            )
            return load.to_response()
        except IntegrityError:
            raise UniqueConstraintError("Ошибка базы данных: нарушение уникальности параметров")


def update_load(load_id, total_hours=None):
    if load_id <= 0:
        raise ValueError("load_id должен быть > 0")
        
    if total_hours is not None and total_hours < 0:
        raise ValueError("total_hours должен быть >= 0")
        
    with db_transaction():
        load = CalculatedLoad.get_or_none((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
        if not load:
            return None
            
        if total_hours is None:
            return load.to_response()
            
        load.total_hours = total_hours
        load.save()
        return load.to_response()


def delete_load(load_id):
    if load_id <= 0:
        raise ValueError("load_id должен быть > 0")
        
    with db_transaction():
        load = CalculatedLoad.get_or_none((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
        if not load:
            return False
            
        query = CalculatedLoad.update(is_active=False).where(
            (CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True)
        )
        rows_updated = query.execute()
        return rows_updated > 0


if __name__ == '__main__':
    init_db()
    print("Таблица calculated_load успешно создана со всеми новыми полями.")
