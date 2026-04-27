from contextlib import asynccontextmanager
from peewee import SqliteDatabase, Model, CharField, BooleanField
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

db = SqliteDatabase('departments.db')

class Department(Model):
    """Модель отделения/факультета"""
    name = CharField(max_length=100, null=False, verbose_name="Название отделения")
    code = CharField(max_length=5, unique=True, null=False, verbose_name="Код отделения")
    phone = CharField(max_length=20, null=True, verbose_name="Телефон")
    manager = CharField(max_length=100, null=True, verbose_name="Заведующий отделением")
    building = CharField(max_length=50, null=True, verbose_name="Корпус/адрес")
    is_active = BooleanField(null=False, default=True, verbose_name="Активно")

    class Meta:
        database = db
        table_name = 'departments'

def init_db():
    """Функция инициализации базы данных"""
    db.connect()
    db.create_tables([Department], safe=True)
    db.close()

class DepartmentCreate(BaseModel):
    """Схема для создания отделения"""
    name: str = Field(..., max_length=100, description="Название отделения")
    code: str = Field(..., min_length=5, max_length=5, description="Код отделения (5 символов)")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон")
    manager: Optional[str] = Field(None, max_length=100, description="Заведующий отделением")
    building: Optional[str] = Field(None, max_length=50, description="Корпус/адрес")
    is_active: bool = Field(default=True, description="Активно ли отделение")

class DepartmentUpdate(BaseModel):
    """Схема для обновления отделения"""
    name: Optional[str] = Field(None, max_length=100, description="Название отделения")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон")
    manager: Optional[str] = Field(None, max_length=100, description="Заведующий отделением")
    building: Optional[str] = Field(None, max_length=50, description="Корпус/адрес")
    is_active: Optional[bool] = Field(None, description="Активно ли отделение")

class DepartmentOut(BaseModel):
    """Схема для ответа (вывода) отделения"""
    id: int
    name: str
    code: str
    phone: Optional[str]
    manager: Optional[str]
    building: Optional[str]
    is_active: bool

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    print("Запуск сервера Department Service...")
    init_db()
    print("База данных инициализирована")
    yield
    # Shutdown
    print("Остановка сервера...")
    if not db.is_closed():
        db.close()
    print("Ресурсы освобождены")

app = FastAPI(
    title="Department Service",
    description="Сервис управления отделениями/факультетами СПО",
    version="1.0",
    lifespan=lifespan
)

@app.post("/departments", response_model=DepartmentOut, status_code=201)
def create_department(department: DepartmentCreate):
    """Создание нового отделения"""
    try:
        db.connect()
        with db.atomic():
            if Department.select().where(Department.code == department.code).exists():
                raise HTTPException(400, f"Отделение с кодом '{department.code}' уже существует")
            
            new_department = Department.create(
                name=department.name,
                code=department.code,
                phone=department.phone,
                manager=department.manager,
                building=department.building,
                is_active=department.is_active
            )
        return new_department
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка при создании: {str(e)}")
    finally:
        db.close()

@app.put("/departments/{department_id}", response_model=DepartmentOut)
def update_department(department_id: int, department: DepartmentUpdate):
    """Обновление информации об отделении"""
    try:
        db.connect()
        with db.atomic():
            if not Department.select().where(Department.id == department_id).exists():
                raise HTTPException(404, "Отделение не найдено")
            
            update_data = {}
            if department.name is not None:
                update_data['name'] = department.name
            if department.phone is not None:
                update_data['phone'] = department.phone
            if department.manager is not None:
                update_data['manager'] = department.manager
            if department.building is not None:
                update_data['building'] = department.building
            if department.is_active is not None:
                update_data['is_active'] = department.is_active
            
            if update_data:
                Department.update(update_data).where(Department.id == department_id).execute()
            
            updated = Department.get_by_id(department_id)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка при обновлении: {str(e)}")
    finally:
        db.close()

@app.delete("/departments/{department_id}")
def delete_department(department_id: int):
    """Удаление отделения"""
    try:
        db.connect()
        with db.atomic():
            deleted = Department.delete().where(Department.id == department_id).execute()
        return {"deleted": bool(deleted), "message": "Отделение удалено" if deleted else "Отделение не найдено"}
    except Exception as e:
        raise HTTPException(500, f"Ошибка при удалении: {str(e)}")
    finally:
        db.close()

@app.get("/departments/{department_id}", response_model=DepartmentOut)
def get_department(department_id: int):
    """Получение отделения по ID"""
    try:
        db.connect()
        try:
            department = Department.get_by_id(department_id)
            return department
        except Department.DoesNotExist:
            raise HTTPException(404, "Отделение не найдено")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка при получении: {str(e)}")
    finally:
        db.close()

@app.get("/departments", response_model=List[DepartmentOut])
def list_departments(
    name: Optional[str] = None,
    code: Optional[str] = None,
    manager: Optional[str] = None,
    building: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
):
    """Получение списка отделений с фильтрацией"""
    try:
        db.connect()
        query = Department.select()
        
        if name:
            query = query.where(Department.name.contains(name))
        if code:
            query = query.where(Department.code == code)
        if manager:
            query = query.where(Department.manager.contains(manager))
        if building:
            query = query.where(Department.building.contains(building))
        if is_active is not None:
            query = query.where(Department.is_active == is_active)
        
        return list(query.offset(offset).limit(limit))
    except Exception as e:
        raise HTTPException(500, f"Ошибка при получении списка: {str(e)}")
    finally:
        db.close()

@app.get("/")
def root():
    """Корневой эндпоинт"""
    return {
        "service": "Department Service",
        "version": "1.0",
        "description": "Сервис управления отделениями/факультетами СПО",
        "endpoints": {
            "POST /departments": "Создать отделение",
            "GET /departments": "Список отделений",
            "GET /departments/{id}": "Получить отделение по ID",
            "PUT /departments/{id}": "Обновить отделение",
            "DELETE /departments/{id}": "Удалить отделение"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Запуск сервера Department Service...")
    print("Документация API: http://localhost:8000/docs")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)