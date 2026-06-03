from datetime import datetime
from peewee import *

db = SqliteDatabase("resource_pool.db")


class BaseModel(Model):
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)


class ResourceCategory(BaseModel):
    id = AutoField(primary_key=True)
    title = CharField(
        max_length=100, unique=True, constraints=[Check("length(title) >= 1")]
    )
    details = CharField(max_length=500)
    is_active = BooleanField(default=True)

    class Meta:
        table_name = "resource_categories"


class Resource(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField(max_length=100, constraints=[Check("length(name) >= 1")])
    description = CharField(max_length=500)
    category_id = ForeignKeyField(
        ResourceCategory, backref="resources", on_delete="RESTRICT"
    )
    total_quantity = IntegerField(constraints=[Check("total_quantity >= 1")])
    available_quantity = IntegerField(constraints=[Check("available_quantity >= 0")])
    unit = CharField(max_length=10, choices=["шт", "компл", "экз"], default="шт")
    status = CharField(
        max_length=20,
        choices=["available", "maintenance", "retired"],
        default="available",
    )
    is_active = BooleanField(default=True)

    class Meta:
        table_name = "resources"
        indexes = ((("name", "category_id"), True),)


def init_db():
    db.connect()
    db.create_tables([ResourceCategory, Resource], safe=True)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
