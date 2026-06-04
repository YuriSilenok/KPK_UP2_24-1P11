from peewee import (
    Model,
    SqliteDatabase,
    PrimaryKeyField,
    IntegerField,
    BooleanField
)

# Инициализация локальной базы данных SQLite для сервиса
db = SqliteDatabase('load_assignment.db')


class BaseModel(Model):
    class Meta:
        database = db


class LoadAssignment(BaseModel):
    id = PrimaryKeyField()
    
    # Идентификаторы сущностей из внешних микросервисов (логические FK)
    teacher_id = IntegerField()
    discipline_id = IntegerField()
    group_id = IntegerField()
    
    # Статус активности записи (bool в соответствии с ответом API)
    is_active = BooleanField(default=True)

    class Meta:
        table_name = 'load_assignments'
        # Ограничение уникальности комбинации полей согласно спецификации API
        indexes = (
            (('teacher_id', 'discipline_id', 'group_id'), True),
        )


def init_db():
    """Функция создания таблиц при старте сервиса."""
    db.connect()
    db.create_tables([LoadAssignment], safe=True)
    db.close()
    print("База данных Load Assignment Service успешно инициализирована.")


if __name__ == "__main__":
    init_db()
