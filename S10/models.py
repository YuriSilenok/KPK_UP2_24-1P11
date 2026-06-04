import datetime
from peewee import *

db = SqliteDatabase('employee_status.db')

# ---------- Модели ----------
class BaseModel(Model):
    class Meta:
        database = db

class Employee(BaseModel):
    class Meta:
        db_table = "employees"

    id = AutoField()
    user_id = IntegerField(unique=True, null=False) 
    hire_date = DateField(null=False)
    status = CharField(max_length=20, default='active', null=False) 
    is_active = BooleanField(default=True)
    updated_at = DateTimeField(default=datetime.datetime.now) 

    @classmethod
    def filter_employees(cls, user_id=None, status=None, hire_date_from=None, hire_date_to=None, limit=None, offset=None):
        """Прямая фильтрация по полям модели с обработкой пагинации"""
        query = cls.select()
        
        if user_id is not None:
            query = query.where(cls.user_id == user_id)
        if status is not None:
            query = query.where(cls.status == status)
        if hire_date_from is not None:
            query = query.where(cls.hire_date >= hire_date_from)
        if hire_date_to is not None:
            query = query.where(cls.hire_date <= hire_date_to)
            
        if limit is not None:
            query = query.limit(int(limit))
        if offset is not None:
            query = query.offset(int(offset))
            
        return query

def init_db():
    db.connect()
    db.create_tables([Employee], safe=True)
    db.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully with single table 'employees'.")
