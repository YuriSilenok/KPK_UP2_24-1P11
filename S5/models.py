from peewee import SqliteDatabase, Model, CharField

db = SqliteDatabase('departments.db')

class Department(Model):
    name = CharField(max_length=100, unique=True, null=False)
    phone = CharField(max_length=20, unique=True, null=False, default='')

    class Meta:
        database = db
        table_name = 'departments'

def init_db():
    db.connect()
    db.create_tables([Department], safe=True)
    db.close()

def create_department(name: str, phone: str = '') -> Department:
    db.connect()
    if Department.select().where(Department.name == name).exists():
        db.close()
        raise ValueError("Отделение с таким названием уже существует")
    new_dept = Department.create(name=name, phone=phone)
    db.close()
    return new_dept

def get_department(dept_id: int) -> Department:
    db.connect()
    try:
        dept = Department.get_by_id(dept_id)
        return dept
    except Department.DoesNotExist:
        raise ValueError("Отделение не найдено")
    finally:
        db.close()

def list_departments(name: str = None, limit: int = 100):
    db.connect()
    query = Department.select()
    if name:
        query = query.where(Department.name.contains(name))
    result = list(query.limit(limit))
    db.close()
    return result

def update_department(dept_id: int, name: str = None, phone: str = None) -> Department:
    db.connect()
    if not Department.select().where(Department.id == dept_id).exists():
        db.close()
        raise ValueError("Отделение не найдено")
    update_data = {}
    if name is not None:
        if Department.select().where((Department.name == name) & (Department.id != dept_id)).exists():
            db.close()
            raise ValueError("Отделение с таким названием уже существует")
        update_data['name'] = name
    if phone is not None:
        update_data['phone'] = phone
    if update_data:
        Department.update(update_data).where(Department.id == dept_id).execute()
    updated = Department.get_by_id(dept_id)
    db.close()
    return updated

def delete_department(dept_id: int) -> bool:
    db.connect()
    deleted = Department.delete().where(Department.id == dept_id).execute()
    db.close()
    return bool(deleted)

if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")
    # Пример использования:
    try:
        dept = create_department("Информационных технологий", "+7-123-456")
        print(f"Создано: {dept.id} - {dept.name}")
    except ValueError as e:
        print(e)
    # Получить список
    depts = list_departments()
    print(f"Всего отделений: {len(depts)}")