from peewee import *
from datetime import date, datetime

db = SqliteDatabase('employee_status.db')

class BaseModel(Model):
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class Position(BaseModel):
    title = CharField(max_length=255, unique=True)
    code = CharField(max_length=50, unique=True)
    department = CharField(max_length=255, null=True)

    class Meta:
        table_name = 'positions'

    def deactivate(self):
        active_count = EmployeePosition.select().where(
            (EmployeePosition.position == self) & 
            (EmployeePosition.is_active == True)
        ).count()
        
        if active_count > 0:
            raise ValueError("Cannot deactivate position with active employee assignments.")
        
        self.is_active = False
        self.save()

class EmployeePosition(BaseModel):
    profile_id = IntegerField()
    position = ForeignKeyField(Position, backref='employee_positions')
    rate = FloatField()
    is_primary = BooleanField(default=False)
    start_date = DateField()
    end_date = DateField(null=True)

    class Meta:
        table_name = 'employee_positions'

    def save(self, *args, **kwargs):
        if not (0.1 <= self.rate <= 2.0):
            raise ValueError("Rate must be between 0.1 and 2.0")

        if self.start_date > date.today():
            raise ValueError("Start date cannot be in the future")
        
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("End date must be after start date")

        if self.is_primary:
            current_primary = EmployeePosition.get_or_none(
                (EmployeePosition.profile_id == self.profile_id) &
                (EmployeePosition.is_primary == True) &
                (EmployeePosition.is_active == True) &
                (EmployeePosition.id != self.id)
            )
            
            if current_primary:
                current_primary.is_primary = False
                current_primary.save()

        if self.id:
            try:
                old_instance = EmployeePosition.get_by_id(self.id)
                if old_instance.position.id != self.position.id:
                    has_active_leave = Leave.select().where(
                        (Leave.employee_position == self) & (Leave.is_active == True)
                    ).exists()
                    
                    has_active_sick = SickLeave.select().where(
                        (SickLeave.employee_position == self) & (SickLeave.is_active == True)
                    ).exists()

                    if has_active_leave or has_active_sick:
                        raise ValueError("Cannot change position while there are active leaves or sick leaves.")
            except EmployeePosition.DoesNotExist:
                pass

        return super().save(*args, **kwargs)

class Leave(BaseModel):
    employee_position = ForeignKeyField(EmployeePosition, backref='leaves')
    start_date = DateField()
    end_date = DateField()
    leave_type = CharField(max_length=20)
    status = CharField(max_length=20, default='pending')

    class Meta:
        table_name = 'leaves'

    def save(self, *args, **kwargs):
        if self.leave_type not in ['annual', 'unpaid', 'study']:
            raise ValueError("Invalid leave type")
        if self.status not in ['pending', 'approved', 'rejected']:
            raise ValueError("Invalid status")

        if self.end_date < self.start_date:
            raise ValueError("End date must be after start date")

        if not self.employee_position.is_active:
            raise ValueError("Cannot create leave for inactive position")

        return super().save(*args, **kwargs)

class SickLeave(BaseModel):
    employee_position = ForeignKeyField(EmployeePosition, backref='sick_leaves')
    start_date = DateField()
    end_date = DateField()
    certificate_number = CharField(max_length=100, unique=True)
    status = CharField(max_length=20, default='active')

    class Meta:
        table_name = 'sick_leaves'

    def save(self, *args, **kwargs):
        if self.status not in ['active', 'closed']:
            raise ValueError("Invalid status")

        if self.end_date < self.start_date:
            raise ValueError("End date must be after start date")
        
        if self.start_date > date.today():
            raise ValueError("Start date cannot be in the future")

        if not self.employee_position.is_active:
            raise ValueError("Cannot create sick leave for inactive position")

        return super().save(*args, **kwargs)

def init_db():
    db.connect()
    db.create_tables([Position, EmployeePosition, Leave, SickLeave], safe=True)

if __name__ == '__main__':
    init_db()
