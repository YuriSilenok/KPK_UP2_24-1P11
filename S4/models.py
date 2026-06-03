"""База данных Permission Service (Вариант №4)"""
from peewee import (
    Model,
    CharField,
    IntegerField,
    AutoField,
    ForeignKeyField,
    SqliteDatabase,
    Check
)

# Подключение к локальной базе данных SQLite для Варианта 4
DB = SqliteDatabase('permission_service_s4.db')


class BaseModel(Model):
    """Базовая модель для настройки подключения"""
    class Meta:
        database = DB


class Permission(BaseModel):
    """Класс системного разрешения (права доступа)"""
    id = AutoField()
    code = CharField(null=False, unique=True, index=True, max_length=50)
    description = CharField(null=False, max_length=255)

    class Meta:
        table_name = 'permissions'


class RolePermission(BaseModel):
    """Таблица связи ролей с правами доступа"""
    id = AutoField()
    
    # role_id поступает из внешнего Role Service. NULL запрещен.
    role_id = IntegerField(null=False)
    
    permission_id = ForeignKeyField(
        Permission, 
        backref='roles', 
        column_name='permission_id',
        null=False
    )

    class Meta:
        table_name = 'role_permissions'
        indexes = (
            (('role_id', 'permission_id'), True),
        )


class UserPermissionOverride(BaseModel):
    """Таблица персональных исключений (переопределений) для пользователей"""
    id = AutoField()
    
    # user_id поступает из чужого Auth/User Service. NULL запрещен.
    user_id = IntegerField(null=False)
    
    permission_id = ForeignKeyField(
        Permission, 
        backref='user_overrides', 
        column_name='permission_id',
        null=False
    )
    
    action_type = CharField(
        null=False, 
        max_length=10,
        constraints=[Check("action_type IN ('allow', 'deny')")]
    )

    class Meta:
        table_name = 'user_permission_overrides'
        indexes = (
            (('user_id', 'permission_id'), True),
        )


def init_db():
    """Создаёт таблицы базы данных"""
    with DB:
        DB.create_tables([
            Permission, 
            RolePermission, 
            UserPermissionOverride
        ])


if __name__ == "__main__":
    init_db()
    print("S4 Permission Service: БД успешно инициализирована.")
