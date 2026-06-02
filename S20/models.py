import os
from peewee import *
from datetime import date
import re
from typing import Optional, List, Dict, Any

db = SqliteDatabase('academic_periods.db')

class BaseModel(Model):
    class Meta:
        database = db

class AcademicPeriod(BaseModel):
    id = AutoField()
    name = CharField(max_length=100, null=False)
    academic_year = CharField(max_length=9, null=False)  # Формат 2025-2026
    period_type = CharField(max_length=10, null=False, default='semester')  # semester, module
    start_date = DateField(null=False)
    end_date = DateField(null=False)
    # ИСПРАВЛЕНИЕ 7: Используем null=True вместо 0 для корневых записей
    parent_period_id = ForeignKeyField(
        'self', 
        null=True, 
        backref='child_periods',
        on_delete='CASCADE'
    )
    is_active = BooleanField(default=True)
    
    class Meta:
        indexes = (
            (('name', 'academic_year'), True),  # уникальная комбинация
        )
        constraints = [
            SQL("CHECK(name <> '')"),
            # ИСПРАВЛЕНИЕ 6: Явная проверка на уровне БД для последовательных годов
            SQL("CHECK(academic_year ~ '^\\d{4}-\\d{4}$')")
        ]

    def save(self, *args, **kwargs):
        # Валидация имени
        stripped_name = self.name.strip()
        if not stripped_name:
            raise ValueError("name must not be empty or consist only of spaces")
        if len(stripped_name) > 100:
            raise ValueError("name must be at most 100 significant characters")
        self.name = stripped_name

        # Валидация типа периода
        if self.period_type not in ('semester', 'module'):
            raise ValueError("period_type must be either 'semester' or 'module'")

        # ИСПРАВЛЕНИЕ 6: Валидация формата academic_year
        match = re.match(r'^(\d{4})-(\d{4})$', self.academic_year)
        if not match:
            raise ValueError("academic_year must be in format YYYY-YYYY")
        
        start_year = int(match.group(1))
        end_year = int(match.group(2))
        if end_year != start_year + 1:
            raise ValueError("academic_year must contain consecutive years (e.g., 2025-2026)")

        # Валидация дат
        if self.start_date < date(2000, 1, 1):
            raise ValueError("start_date must be >= 2000-01-01")
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be greater than start_date")

        # Валидация parent_period_id
        if self.period_type == 'semester' and self.parent_period_id is not None:
            raise ValueError("Semester must have parent_period_id = NULL")
        
        # ИСПРАВЛЕНИЕ 3: Оптимизация проверки parent для модуля
        if self.period_type == 'module':
            if self.parent_period_id is None:
                raise ValueError("Module must have parent_period_id pointing to a semester")
            
            # Проверяем только если parent_period_id еще не загружен
            if not isinstance(self.parent_period_id, AcademicPeriod):
                try:
                    parent = AcademicPeriod.get_by_id_raw(self.parent_period_id.id if hasattr(self.parent_period_id, 'id') else self.parent_period_id)
                    if parent is None or parent.period_type != 'semester':
                        raise ValueError("parent_period_id must reference existing semester")
                except AcademicPeriod.DoesNotExist:
                    raise ValueError("parent_period_id must reference existing semester")

        # Проверка на уникальность (убираем дублирование с IntegrityError)
        existing = AcademicPeriod.get_or_none(
            (AcademicPeriod.name == self.name) &
            (AcademicPeriod.academic_year == self.academic_year) &
            (AcademicPeriod.id != self.id)
        )
        if existing is not None:
            raise ValueError("AcademicPeriod with this name and academic_year already exists")
        
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            # ИСПРАВЛЕНИЕ 4: Убираем дублирование ошибки - IntegrityError теперь только для БД
            raise ValueError("Database integrity error: record already exists")

    def soft_delete(self):
        """ИСПРАВЛЕНИЕ 2: Возвращаем структурированный ответ"""
        if self.is_active:
            self.is_active = False
            self.save()
            return {"result": True, "message": "Period successfully deleted"}
        return {"result": False, "message": "Period is already deleted"}

    @classmethod
    def get_all_by_filters(
        cls,
        name_contains: Optional[str] = None,
        academic_year: Optional[str] = None,
        period_type: Optional[str] = None,
        parent_period_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """ИСПРАВЛЕНИЕ 1: Возвращаем список словарей вместо query"""
        query = cls.select().where(cls.is_active == True)

        if name_contains:
            query = query.where(cls.name.contains(name_contains))
        if academic_year:
            query = query.where(cls.academic_year == academic_year)
        if period_type:
            query = query.where(cls.period_type == period_type)
        if parent_period_id is not None:
            query = query.where(cls.parent_period_id == parent_period_id)

        # Конвертируем в список словарей
        return [
            {
                "id": period.id,
                "name": period.name,
                "academic_year": period.academic_year,
                "start_date": period.start_date.isoformat(),
                "end_date": period.end_date.isoformat(),
                "period_type": period.period_type,
                "parent_period_id": period.parent_period_id.id if period.parent_period_id else None,
                "is_active": period.is_active
            }
            for period in query
        ]

    @classmethod
    def get_by_id(cls, period_id: int) -> Dict[str, Any]:
        """ИСПРАВЛЕНИЕ 5: Возвращаем стандартизированный ответ"""
        period = cls.get_or_none(id=period_id)
        
        if period is None:
            return {"result": None, "message": "Period not found"}
        
        return {
            "result": {
                "id": period.id,
                "name": period.name,
                "academic_year": period.academic_year,
                "start_date": period.start_date.isoformat(),
                "end_date": period.end_date.isoformat(),
                "period_type": period.period_type,
                "parent_period_id": period.parent_period_id.id if period.parent_period_id else None,
                "is_active": period.is_active
            }
        }
    
    @classmethod
    def get_by_id_raw(cls, period_id: int):
        """Вспомогательный метод для внутренней использования"""
        return cls.get_or_none(id=period_id)

def init_db():
    db.connect()
    db.create_tables([AcademicPeriod], safe=True)
    db.close()

def get_db_init_handler():
    def handler():
        init_db()
        return {"message": "Database initialized"}
    return handler
