import os
from peewee import *
from datetime import date
import re

db = SqliteDatabase('academic_periods.db')

class BaseModel(Model):
    class Meta:
        database = db

class AcademicPeriod(BaseModel):
    id = AutoField()
    name = CharField(max_length=100, null=False)
    academic_year = CharField(max_length=9, null=False)
    period_type = CharField(max_length=10, null=False, default='semester')
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    parent_period_id = IntegerField(null=True, default=0)
    is_active = BooleanField(default=True)

    class Meta:
        indexes = (
            (('name', 'academic_year'), True),
        )
        constraints = [
            SQL("CHECK(name <> '')")
        ]

    def save(self, *args, **kwargs):
        # Проверка имени
        stripped_name = self.name.strip()
        if not stripped_name:
            raise ValueError("name must not be empty or consist only of spaces")
        if len(stripped_name) < 1:
            raise ValueError("name must be at least 1 character")
        if len(stripped_name) > 100:
            raise ValueError("name must be at most 100 significant characters")
        self.name = stripped_name
        
        # Проверка period_type
        if self.period_type not in ('semester', 'module'):
            raise ValueError("period_type must be either 'semester' or 'module'")
        
        # Проверка academic_year
        if not re.match(r'^\d{4}-\d{4}$', self.academic_year):
            raise ValueError("academic_year must be in format YYYY-YYYY")
        
        # Проверка дат
        if self.start_date < date(2000, 1, 1):
            raise ValueError("start_date must be >= 2000-01-01")
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be greater than start_date")
        
        # Проверка parent_period_id
        parent_id = self.parent_period_id if self.parent_period_id is not None else 0
        
        if self.period_type == 'semester' and parent_id != 0:
            raise ValueError("Semester must have parent_period_id = 0")
        if self.period_type == 'module' and parent_id == 0:
            raise ValueError("Module must have parent_period_id pointing to a semester")
        
        if self.period_type == 'module' and parent_id != 0:
            parent = AcademicPeriod.get_or_none(id=parent_id)
            if parent is None or parent.period_type != 'semester':
                raise ValueError("parent_period_id must reference an existing semester")
        
        # Приводим None к 0 перед сохранением
        if self.parent_period_id is None:
            self.parent_period_id = 0
        
        # Проверка уникальности name + academic_year (исключая текущую запись)
        existing = AcademicPeriod.get_or_none(
            name=self.name, 
            academic_year=self.academic_year
        )
        if existing and existing.id != self.id:
            raise ValueError("Period with this name and academic_year already exists")
        
        super().save(*args, **kwargs)

    def soft_delete(self):
        """Мягкое удаление - соответствует требованию 'Удалить учебный период по ID'"""
        if self.is_active:
            self.is_active = False
            self.save()
            return True
        return False

    @classmethod
    def get_all_by_filters(cls, term=None, academic_year=None, period_type=None, parent_period_id=None):
        """Получить список учебных периодов по заданным параметрам - возвращает ВСЕ периоды (и активные, и нет)"""
        query = cls.select()  # ← БЕЗ фильтрации по is_active
        
        if term:
            query = query.where(cls.name.contains(term))
        if academic_year:
            query = query.where(cls.academic_year == academic_year)
        if period_type:
            query = query.where(cls.period_type == period_type)
        if parent_period_id is not None:
            query = query.where(cls.parent_period_id == parent_period_id)
        
        result = []
        for period in query:
            result.append({
                "id": period.id,
                "name": period.name,
                "academic_year": period.academic_year,
                "start_date": period.start_date.isoformat(),
                "end_date": period.end_date.isoformat(),
                "period_type": period.period_type,
                "parent_period_id": period.parent_period_id,
                "is_active": period.is_active
            })
        return result

    @classmethod
    def get_by_id(cls, period_id):
        """Получить учебный период по ID - возвращает даже неактивные"""
        return cls.get_or_none(id=period_id)  # ← БЕЗ фильтрации по is_active


def init_db():
    db.connect()
    db.create_tables([AcademicPeriod], safe=True)
    db.close()

def get_db_init_handler():
    def handler():
        init_db()
        return {"message": "Database initialized"}
    return handler
