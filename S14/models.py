from peewee import SqliteDatabase, Model, IntegerField, FloatField, BooleanField, PrimaryKeyField, Check

db = SqliteDatabase('workload.db')

class CalculatedLoad(Model):
    id = PrimaryKeyField()
    teacher_id = IntegerField(null=False, constraints=[Check('teacher_id > 0')])
    period_id = IntegerField(null=False, constraints=[Check('period_id > 0')])
    total_hours = FloatField(null=True, constraints=[Check('total_hours >= 0')])
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = 'calculated_loads'
        indexes = ((('teacher_id', 'period_id'), True),)

def init_db():
    db.connect()
    db.create_tables([CalculatedLoad], safe=True)
    db.close()

def get_active_loads(teacher_id=None, period_id=None, limit=100, offset=0):
    query = CalculatedLoad.select().where(CalculatedLoad.is_active == True)
    if teacher_id is not None and teacher_id > 0:
        query = query.where(CalculatedLoad.teacher_id == teacher_id)
    if period_id is not None and period_id > 0:
        query = query.where(CalculatedLoad.period_id == period_id)
    if limit < 1:
        limit = 100
    if limit > 1000:
        limit = 1000
    if offset < 0:
        offset = 0
    return list(query.offset(offset).limit(limit))

def get_active_load_by_id(load_id):
    return CalculatedLoad.get_or_none((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))

def create_load(teacher_id, period_id, total_hours=None):
    return CalculatedLoad.create(
        teacher_id=teacher_id,
        period_id=period_id,
        total_hours=total_hours,
        is_active=True
    )

def update_load(load_id, total_hours=None):
    query = CalculatedLoad.update(total_hours=total_hours).where(
        (CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True)
    )
    return query.execute() > 0

def delete_load(load_id):
    query = CalculatedLoad.update(is_active=False).where(
        (CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True)
    )
    return query.execute() > 0

if __name__ == '__main__':
    init_db()
    print("Таблица calculated_loads создана")