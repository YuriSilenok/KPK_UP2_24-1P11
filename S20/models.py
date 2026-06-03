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
    parent_period_id = OneToOneField('self', null=False, backref='child')
    is_active = BooleanField(default=True)

    class Meta:
        indexes = ((('name',), True),)
    def soft_delete(self):
        self.is_active = False
        self.save()
        return True

def init_db():
    db.connect()
    db.create_tables([AcademicPeriod])
    db.close()

if __name__ == "__main__":
    init_db()
    print("Database ready.")
