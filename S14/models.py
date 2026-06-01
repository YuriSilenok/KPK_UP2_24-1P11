from peewee import SqliteDatabase, Model, IntegerField, FloatField, BooleanField, PrimaryKeyField, Check

db = SqliteDatabase('workload.db')

class CalculatedLoad(Model):
    id = PrimaryKeyField()
    teacher_id = IntegerField(null=False, constraints=[Check('teacher_id > 0')])
    period_id = IntegerField(null=False, constraints=[Check('period_id > 0')])
    total_hours = FloatField(null=False, constraints=[Check('total_hours >= 0')])
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = 'calculated_loads'
        indexes = ((('teacher_id', 'period_id'), True),)

def init_db():
    db.connect()
    db.create_tables([CalculatedLoad], safe=True)
    db.close()

if __name__ == '__main__':
    init_db()