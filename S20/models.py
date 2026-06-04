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
    is_semester = BooleanField()
    is_module = BooleanField()
    parent_period_id = ForeignKeyField('self', null=True, backref='children')
    is_active = BooleanField(default=True)

    class Meta:
        indexes = ((('name',), True),)
        constraints = [
            Check("start_date >= '2000-01-01'"),
            Check("end_date > start_date")
        ]

    def soft_delete(self):
        if not self.id:
            return False
            
        try:
            self.is_active = False
            return bool(self.save()) 
        except DatabaseError:
            return False

def init_db():
    db.connect()
    db.create_tables([AcademicPeriod])
    db.close()

if __name__ == "__main__":
    init_db()
    print("Database ready.")
