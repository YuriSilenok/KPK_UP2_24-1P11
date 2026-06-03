from peewee import *
from datetime import date

db = SqliteDatabase('academic_periods.db')

class BaseModel(Model):
    class Meta:
        database = db

class AcademicPeriod(BaseModel):
    """
    Модель учебного периода согласно ER-диаграмме и API doc.md
    """
    id = AutoField()
    name = CharField(max_length=100, null=False, unique=True)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    is_semester = BooleanField(default=False)
    is_module = BooleanField(default=False)
    parent_period_id = ForeignKeyField('self', null=True, backref='children')
    is_active = BooleanField(default=True)

    class Meta:
        pass

def init_db():
    db.connect()
    db.create_tables([AcademicPeriod], safe=True)
    db.close()

if __name__ == "__main__":
    init_db()
    print("Database ready.")
        
        name = data.get('name', '').strip()
        if not name: raise ValueError("Name is required")
        if len(name) > 100: raise ValueError("Name too long")

        if data.get('start_date') < date(2000, 1, 1):
            raise ValueError("Start date must be >= 2000-01-01")
        return AcademicPeriod.create(**data)

    @staticmethod
    def get_all_by_filters(is_semester=None, is_module=None, name_contains=None, parent_period_id=None):
        query = AcademicPeriod.select().where(AcademicPeriod.is_active == True)
        
        if is_semester is not None: query = query.where(AcademicPeriod.is_semester == is_semester)
        if is_module is not None: query = query.where(AcademicPeriod.is_module == is_module)
        if name_contains: query = query.where(AcademicPeriod.name.contains(name_contains))
        if parent_period_id is not None: query = query.where(AcademicPeriod.parent_period_id == parent_period_id)

        return [
            {
                "id": p.id, "name": p.name, "start_date": p.start_date.isoformat(),
                "end_date": p.end_date.isoformat(), "is_semester": p.is_semester,
                "is_module": p.is_module, "parent_period_id": p.parent_period_id,
                "is_active": p.is_active
            } for p in query
        ]

    @staticmethod
    def get_by_id(period_id):
        p = AcademicPeriod.get_or_none(id=period_id)
        if not p: return None
        return {
            "id": p.id, "name": p.name, "start_date": p.start_date.isoformat(),
            "end_date": p.end_date.isoformat(), "is_semester": p.is_semester,
            "is_module": p.is_module, "parent_period_id": p.parent_period_id,
            "is_active": p.is_active
        }
def init_db():
    db.connect()
    db.create_tables([AcademicPeriod], safe=True)
    db.close()

if __name__ == "__main__":
    init_db()
    print("Database ready.")
