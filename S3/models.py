import os
from peewee import SqliteDatabase, Model, CharField, TextField, BooleanField, ForeignKeyField, DateTimeField
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db = SqliteDatabase(os.path.join(BASE_DIR, "role_service.db"))

class BaseModel(Model):
    class Meta:
        database = db

class Role(BaseModel):
    name = CharField(max_length=50, unique=True, null=False)
    description = TextField(max_length=200, null=True)
    is_active = BooleanField(default=True, null=False)

class Permission(BaseModel):
    name = CharField(max_length=100, unique=True, null=False)
    resource = CharField(max_length=100, null=False)
    action = CharField(max_length=50, null=False)

class RolePermission(BaseModel):
    role = ForeignKeyField(Role, backref="permissions", null=False, on_delete="CASCADE")
    permission = ForeignKeyField(Permission, backref="roles", null=False, on_delete="CASCADE")
    granted_at = DateTimeField(default=datetime.now, null=False)

def init_db():
    db.connect()
    db.create_tables([Role, Permission, RolePermission], safe=True)
    db.close()

if __name__ == "__main__":
    init_db()
    print("База данных создана")