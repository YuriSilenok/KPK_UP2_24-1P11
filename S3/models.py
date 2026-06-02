import os
from peewee import SqliteDatabase, Model, AutoField, CharField, TextField, BooleanField, ForeignKeyField, DateTimeField, IntegerField
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db = SqliteDatabase(os.path.join(BASE_DIR, "role_service.db"))

class BaseModel(Model):
    class Meta:
        database = db

class Role(BaseModel):
    id = AutoField()
    name = CharField(max_length=50, unique=True, null=False)
    description = TextField(max_length=200, null=True)
    is_active = BooleanField(default=True, null=False)

class RolePermission(BaseModel):
    id = AutoField()
    role_id = ForeignKeyField(Role, backref="role_permissions", null=False, on_delete="CASCADE")
    permission_id = IntegerField(null=False)
    granted_at = DateTimeField(default=datetime.now, null=False)

    class Meta:
        indexes = (
            (('role_id', 'permission_id'), True),
        )

def init_db():
    db.connect()
    db.create_tables([Role, RolePermission], safe=True)
    db.close()

def get_db():
    return db

if __name__ == "__main__":
    init_db()
    print("База данных инициализирована.")