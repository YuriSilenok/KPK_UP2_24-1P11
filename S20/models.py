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
    academic_year = CharField(max_length=9, null=False)  # Формат 2025-2026, обязательный
    period_type = CharField(max_length=10, null=False)  # semester, module
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    parent_period_id = IntegerField(null=False, default=0)  # 0 — корневой период, иначе ID родителя (семестра для модуля)
    is_active = BooleanField(default=True)

    class Meta:
        indexes = (
            (('name', 'academic_year'), True),  # уникальная комбинация
        )
        constraints = [
            SQL("CHECK(name <> '')")
        ]

    def save(self, *args, **kwargs):
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("name must not be empty")
        if len(self.name) > 100:
            raise ValueError("name must be at most 100 characters")
        if self.period_type not in ('semester', 'module'): raise ValueError("period_type must be either 'semester' or 'module'")
        if not re.match(r'^\d{4}-\d{4}$', self.academic_year): raise ValueError("academic_year must be in format YYYY-YYYY")
        parts = self.academic_year.split('-')
        if int(parts[1]) != int(parts[0]) + 1:
            raise ValueError("academic_year must be consecutive years (e.g., 2025-2026)")
        if self.start_date < date(2000, 1, 1): raise ValueError("start_date must be >= 2000-01-01")
        if self.end_date <= self.start_date: raise ValueError("end_date must be greater than start_date")
        if self.period_type == 'semester' and self.parent_period_id != 0: raise ValueError("Semester must have parent_period_id = 0")
        if self.period_type == 'module' and self.parent_period_id == 0: raise ValueError("Module must have parent_period_id pointing to a semester")
        if self.period_type == 'module' and self.parent_period_id != 0:
            parent = AcademicPeriod.get_or_none(id=self.parent_period_id)
            if parent is None or parent.period_type != 'semester': raise ValueError("parent_period_id must reference an existing semester")
        
        # Проверка уникальности пары (name, academic_year)
        existing = AcademicPeriod.get_or_none(
            name=self.name,
            academic_year=self.academic_year
        )
        if existing is not None and existing.id != self.id:
            raise ValueError(f"AcademicPeriod with name '{self.name}' and academic_year '{self.academic_year}' already exists (id={existing.id})")
        
        super().save(*args, **kwargs)

    def soft_delete(self):
        self.is_active = False
        self.save()
        return {
            "id": self.id,
            "name": self.name,
            "academic_year": self.academic_year,
            "period_type": self.period_type,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "parent_period_id": self.parent_period_id,
            "is_active": self.is_active
        }

    @classmethod
    def name_contains(cls, term):
        return cls.select().where(cls.name.contains(term))

def init_db():
    db.connect()
    db.create_tables([AcademicPeriod], safe=True)
    db.close()

def get_db_init_handler():
    def handler():
        init_db()
        return {"message": "Database initialized"}
    return handler
    