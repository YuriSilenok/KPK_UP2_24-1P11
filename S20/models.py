import re
from datetime import date

from peewee import *

db = SqliteDatabase('academic_periods.db')

class BaseModel(Model):
    class Meta:
        database = db

class AcademicPeriod(BaseModel):
    id = AutoField()

    name = CharField(max_length=100, null=False)
    academic_year = CharField(max_length=9, null=False)

    period_type = CharField(
        max_length=10,
        null=False,
        default='semester'
    )

    start_date = DateField(null=False)
    end_date = DateField(null=False)

    parent_period_id = IntegerField(
        null=False,
        default=0
    )

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
        self.name = self.name.strip()

        if not self.name:
            raise ValueError(
                "name must not be empty or consist only of spaces"
            )

        if len(self.name) > 100:
            raise ValueError(
                "name must be at most 100 characters"
            )

        # Проверка period_type
        if self.period_type not in ("semester", "module"):
            raise ValueError(
                "period_type must be semester or module"
            )

        # Проверка academic_year
        match = re.match(
            r'^(\d{4})-(\d{4})$',
            self.academic_year
        )

        if not match:
            raise ValueError(
                "academic_year must be in format YYYY-YYYY"
            )

        start_year = int(match.group(1))
        end_year = int(match.group(2))

        if end_year != start_year + 1:
            raise ValueError(
                "academic_year must contain consecutive years"
            )

        # Проверка дат
        if self.start_date < date(2000, 1, 1):
            raise ValueError(
                "start_date must be >= 2000-01-01"
            )

        if self.end_date <= self.start_date:
            raise ValueError(
                "end_date must be greater than start_date"
            )

        # Проверка parent_period_id
        if self.period_type == "semester":

            if self.parent_period_id != 0:
                raise ValueError(
                    "semester must have parent_period_id = 0"
                )

        if self.period_type == "module":

            if self.parent_period_id == 0:
                raise ValueError(
                    "module must reference a semester"
                )

            parent = AcademicPeriod.get_or_none(
                id=self.parent_period_id
            )

            if parent is None:
                raise ValueError(
                    "parent period does not exist"
                )

            if parent.period_type != "semester":
                raise ValueError(
                    "parent period must be a semester"
                )

        try:
            return super().save(*args, **kwargs)

        except IntegrityError:
            raise ValueError(
                "Period with this name and academic_year already exists"
            )

    def soft_delete(self):
        """
        Удалить учебный период по ID
        """

        if self.is_active:
            self.is_active = False
            self.save()

            return {
                "result": True
            }

        return {
            "result": False
        }

    @classmethod
    def get_by_id(cls, period_id):
        """
        Получить учебный период по ID
        """

        period = cls.get_or_none(
            cls.id == period_id,
            cls.is_active == True
        )

        if period is None:
            return None

        return {
            "id": period.id,
            "name": period.name,
            "academic_year": period.academic_year,


"start_date": period.start_date.isoformat(),
            "end_date": period.end_date.isoformat(),
            "period_type": period.period_type,
            "parent_period_id": period.parent_period_id,
            "is_active": period.is_active
        }

    @classmethod
    def get_all_by_filters(
        cls,
        name_contains=None,
        academic_year=None,
        period_type=None,
        parent_period_id=None
    ):
        """
        Получить список учебных периодов
        """

        query = cls.select().where(
            cls.is_active == True
        )

        if name_contains:
            query = query.where(
                cls.name.contains(name_contains)
            )

        if academic_year:
            query = query.where(
                cls.academic_year == academic_year
            )

        if period_type:
            query = query.where(
                cls.period_type == period_type
            )

        if parent_period_id is not None:
            query = query.where(
                cls.parent_period_id == parent_period_id
            )

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

def init_db():
    db.connect(reuse_if_open=True)

    db.create_tables(
        [AcademicPeriod],
        safe=True
    )

    db.close()

def get_db_init_handler():

    def handler():
        init_db()

        return {
            "message": "Database initialized"
        }

    return handler
