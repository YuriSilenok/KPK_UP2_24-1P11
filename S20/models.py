from peewee import *
from datetime import date

db = SqliteDatabase('academic_periods.db')

class BaseModel(Model):
    class Meta:
        database = db

class AcademicPeriod(BaseModel):
    id = AutoField()
    name = CharField(max_length=100, null=False)
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    is_semester = BooleanField(default=False)
    is_module = BooleanField(default=False)
    parent_period_id = ForeignKeyField('self', null=True, column_name='parent_period_id')
    is_active = BooleanField(default=True)

    class Meta:
        indexes = ((('name',), True),)

    def soft_delete(self):
        self.is_active = False
        self.save()
        return True

class AcademicPeriodService:
    @staticmethod
    def create_period(data):
        if data.get('end_date') <= data.get('start_date'):
            raise ValueError("end_date must be greater than start_date")
        if data.get('start_date') < date(2000, 1, 1):
            raise ValueError("Start date must be >= 2000-01-01")
            
        return AcademicPeriod.create(**data)

    @staticmethod
    def get_all_by_filters(is_semester=None, is_module=None, name_contains=None, parent_period_id=None):
        query = AcademicPeriod.select().where(AcademicPeriod.is_active == True)
        return list(query.dicts())

    @staticmethod
    def get_by_id(period_id):
        return AcademicPeriod.get_or_none(id=period_id)

def init_db():
    db.connect()
    db.create_tables([AcademicPeriod], safe=True)
    db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
