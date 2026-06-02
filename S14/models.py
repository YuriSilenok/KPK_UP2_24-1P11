from peewee import SqliteDatabase, Model, IntegerField, FloatField, BooleanField, PrimaryKeyField, Check, IntegrityError

db = SqliteDatabase('workload.db')

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
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'period_id': self.period_id,
            'total_hours': self.total_hours
        }


def init_db():
    db.connect()
    db.create_tables([CalculatedLoad], safe=True)
    db.close()


def get_active_loads(teacher_id=None, period_id=None, limit=100, offset=0):
    if limit < 1 or limit > 1000:
        raise ValueError("limit должен быть в диапазоне 1-1000")
    if offset < 0:
        raise ValueError("offset должен быть >= 0")
    
    query = CalculatedLoad.select().where(CalculatedLoad.is_active == True)
    if teacher_id is not None:
        if teacher_id <= 0:
            raise ValueError("teacher_id должен быть > 0")
        query = query.where(CalculatedLoad.teacher_id == teacher_id)
    if period_id is not None:
        if period_id <= 0:
            raise ValueError("period_id должен быть > 0")
        query = query.where(CalculatedLoad.period_id == period_id)
    
    return [load.to_response() for load in query.offset(offset).limit(limit)]


def get_active_load_by_id(load_id):
    load = CalculatedLoad.get_or_none((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
    return load.to_response() if load else None


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
        load = CalculatedLoad.create(
            teacher_id=teacher_id,
            period_id=period_id,
            total_hours=total_hours,
            is_active=True
        )
        return load.to_response()
    except IntegrityError:
        raise ValueError("Запись с таким teacher_id и period_id уже существует")


def update_load(load_id, total_hours=None):
    existing = CalculatedLoad.get_or_none((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
    if existing is None:
        return None
    
    if total_hours is not None:
        if total_hours < 0:
            raise ValueError("total_hours должен быть >= 0")
        existing.total_hours = total_hours
        existing.save()
    
    return existing.to_response()


def delete_load(load_id):
    existing = CalculatedLoad.get_or_none((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
    if existing is None:
        return False
    existing.is_active = False
    existing.save()
    return True


if __name__ == '__main__':
    init_db()
    print("Таблица calculated_loads создана")