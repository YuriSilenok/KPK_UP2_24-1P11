from peewee import *
import datetime

db = SqliteDatabase('work_programs.db')

class BaseModel(Model):
    class Meta:
        database = db

class WorkProgram(BaseModel):
    title = CharField(null=False)
    file_path = CharField(null=False)
    version = CharField(null=False, default="1.0")
    created_at = DateTimeField(default=datetime.datetime.now, null=False)

class Specialty(BaseModel):
    code = CharField(unique=True, null=False)
    name = CharField(null=False)

class ProgramAssignment(BaseModel):
    program = ForeignKeyField(WorkProgram, backref='assignments', null=False)
    specialty = ForeignKeyField(Specialty, backref='programs', null=False)
    discipline_id = IntegerField(null=False) # То самое поле

    class Meta:
        indexes = (
            (('program', 'specialty', 'discipline_id'), True),
        )

def init_db():
    db.connect()
    db.create_tables([WorkProgram, Specialty, ProgramAssignment])
    print("БД инициализирована.")

if __name__ == "__main__":
    init_db()

