from peewee import SqliteDatabase, Model, IntegerField, FloatField, BooleanField, PrimaryKeyField, Check, IntegrityError
from contextlib import contextmanager

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
        table_name = 'calculated_loads'
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
    try:
        load = CalculatedLoad.get_or_none((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
        return load.to_response() if load else None
    except Exception:
        return None


def create_load(teacher_id, period_id, total_hours=None):
    if teacher_id <= 0:
        raise ValueError("teacher_id должен быть > 0")
    if period_id <= 0:
        raise ValueError("period_id должен быть > 0")
    
    if total_hours is None:
        total_hours = 0.0
    if total_hours < 0:
        raise ValueError("total_hours должен быть >= 0")
    
    try:
        with db_transaction():
            load = CalculatedLoad.create(
                teacher_id=teacher_id,
                period_id=period_id,
                total_hours=total_hours,
                is_active=True
            )
            return load.to_response()
    except IntegrityError:
        raise UniqueConstraintError("Запись с таким teacher_id и period_id уже существует")


def update_load(load_id, total_hours=None):
    # Если total_hours не передан, обновление не требуется
    if total_hours is None:
        existing = CalculatedLoad.get_or_none((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
        return existing.to_response() if existing else None
    
    if total_hours < 0:
        raise ValueError("total_hours должен быть >= 0")
    
    try:
        with db_transaction():
            # Используем update() с явным фильтром для предотвращения race conditions
            query = CalculatedLoad.update(total_hours=total_hours).where(
                (CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True)
            )
            rows_updated = query.execute()
            
            if rows_updated == 0:
                return None
            
            # Получаем обновленную запись через get_or_none
            updated = CalculatedLoad.get_or_none(
                (CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True)
            )
            return updated.to_response() if updated else None
    except Exception:
        return None


def delete_load(load_id):
    try:
        with db_transaction():
            query = CalculatedLoad.update(is_active=False).where(
                (CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True)
            )
            rows_updated = query.execute()
            return rows_updated > 0
    except Exception:
        return False


if __name__ == '__main__':
    init_db()
    print("Таблица calculated_loads создана")