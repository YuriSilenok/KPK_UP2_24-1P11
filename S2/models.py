'''База данных профелей'''


import os
from peewee import (
    SqliteDatabase,
    Model,
    AutoField,
    IntegerField,
    CharField,
    TextField,
    BooleanField,
    ForeignKeyField,
)

DB_PATH = os.path.join(os.path.dirname(__file__), "profile_service.db")
db = SqliteDatabase(DB_PATH, pragmas={"foreign_keys": 1})


class BaseModel(Model):
    '''Базовая модель'''
    class Meta:
        database = db


class Profile(BaseModel):
    """Профиль пользователя"""
    id = AutoField(primary_key=True)
    first_name = CharField(max_length=100, null=False)
    last_name = CharField(max_length=100, null=False)
    middle_name = CharField(max_length=100, null=True)
    phone = CharField(max_length=20, unique=True, null=False)
    email = CharField(max_length=255, unique=True, null=False)
    photo_url = TextField(null=True)

    class Meta:
        table_name = "profiles"


class NotificationSetting(BaseModel):
    """Настройки уведомлений"""
    profile = ForeignKeyField(
        Profile,
        backref="notification",
        unique=True,
        on_delete="CASCADE",
        null=False
    )
    phone_notification = BooleanField(default=True)
    email_notification = BooleanField(default=True)

    class Meta:
        table_name = "notification_settings"


def init_db():
    """Инициализация базы данных"""
    db.connect()
    db.create_tables([Profile, NotificationSetting], safe=True)
    db.close()


if __name__ == "__main__":
    print("Инициализация базы данных для Profile Service (вариант №2)...")
    init_db()
    print("База данных готова.")
