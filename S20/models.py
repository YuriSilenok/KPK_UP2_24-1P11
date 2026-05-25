import os
from peewee import *
from datetime import date
import re

db = SqliteDatabase('academic_periods.db')

class BaseModel(Model):
    class Meta:
        database = db

class AcademicPeriod(BaseModel):
    name = CharField(max_length=100)
    academic_year = CharField(max_length=9, null=False)  # Формат 2025-2026, необязательный
    period_type = CharField(max_length=10)  # semester, module
    start_date = DateField()
    end_date = DateField()
    parent_period_id = IntegerField(default=0)  # 0 — корневой период, иначе ID родителя (семестра для модуля)
    is_active = BooleanField(default=True)

    class Meta:
        indexes = (
            (('name', 'academic_year'), True),  # уникальная комбинация
        )
        constraints = [SQL('UNIQUE(name, academic_year)')]

    def save(self, *args, **kwargs):
        if self.period_type not in ('semester', 'module'): raise ValueError("period_type must be either 'semester' or 'module'")
        if len(self.name.strip()) < 1: raise ValueError("name must be at least 1 character")
        if not re.match(r'^\d{4}-\d{4}$', self.academic_year): raise ValueError("academic_year must be in format YYYY-YYYY")
        if self.start_date < date(2000, 1, 1): raise ValueError("start_date must be >= 2000-01-01")
        if self.end_date <= self.start_date: raise ValueError("end_date must be greater than start_date")
        if self.period_type == 'semester' and self.parent_period_id != 0: raise ValueError("Semester must have parent_period_id = 0")
        if self.period_type == 'module' and self.parent_period_id == 0: raise ValueError("Module must have parent_period_id pointing to a semester")
        if self.period_type == 'module' and self.parent_period_id != 0:
            parent = AcademicPeriod.get_or_none(id=self.parent_period_id)
            if parent is None or parent.period_type != 'semester': raise ValueError("parent_period_id must reference an existing semester")
        super().save(*args, **kwargs)

def init_db():
    db.connect()
    db.create_tables([AcademicPeriod], safe=True)
    db.close()

def get_db_init_handler():
    def handler():
        init_db()
        return {"message": "Database initialized"}
    return handler