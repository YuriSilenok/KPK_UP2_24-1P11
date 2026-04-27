from contextlib import asynccontextmanager
from peewee import SqliteDatabase, Model, CharField, IntegerField, Check
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

# ==================== БАЗА ДАННЫХ ====================
db = SqliteDatabase('groups.db')

class Group(Model):
    """Модель учебной группы"""
    name = CharField(max_length=20, unique=True, null=False, verbose_name="Название группы")
    course = IntegerField(null=False, constraints=[Check('course BETWEEN 1 AND 4')], verbose_name="Курс")
    specialty_code = CharField(max_length=8, null=False, verbose_name="Код специальности")
    student_count = IntegerField(null=False, default=0, verbose_name="Количество студентов")
    curator = CharField(max_length=100, null=True, verbose_name="Куратор")

    class Meta:
        database = db
        table_name = 'groups'

def init_db():
    """Функция инициализации базы данных"""
    db.connect()
    db.create_tables([Group], safe=True)
    db.close()

# ==================== СХЕМЫ PYDANTIC ====================
class GroupCreate(BaseModel):
    """Схема для создания группы"""
    name: str = Field(..., max_length=20, description="Название группы")
    course: int = Field(..., ge=1, le=4, description="Курс (1-4)")
    specialty_code: str = Field(..., min_length=8, max_length=8, description="Код специальности (8 цифр)")
    student_count: int = Field(default=0, ge=0, le=50, description="Количество студентов")
    curator: Optional[str] = Field(None, max_length=100, description="ФИО куратора")

class GroupUpdate(BaseModel):
    """Схема для обновления группы"""
    name: Optional[str] = Field(None, max_length=20, description="Название группы")
    course: Optional[int] = Field(None, ge=1, le=4, description="Курс (1-4)")
    student_count: Optional[int] = Field(None, ge=0, le=50, description="Количество студентов")
    curator: Optional[str] = Field(None, max_length=100, description="ФИО куратора")

class GroupOut(BaseModel):
    """Схема для ответа (вывода) группы"""
    id: int
    name: str
    course: int
    specialty_code: str
    student_count: int
    curator: Optional[str]

# ==================== LIFESPAN ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    print("🚀 Запуск сервера...")
    init_db()
    print("✅ База данных инициализирована")
    yield
    # Shutdown
    print("🛑 Остановка сервера...")
    if not db.is_closed():
        db.close()
    print("✅ Ресурсы освобождены")

# ==================== FASTAPI ПРИЛОЖЕНИЕ ====================
app = FastAPI(
    title="Group Service",
    description="Сервис управления учебными группами СПО",
    version="1.0",
    lifespan=lifespan
)

# ==================== ЭНДПОИНТЫ ====================
@app.post("/groups", response_model=GroupOut, status_code=201)
def create_group(group: GroupCreate):
    """Создание новой учебной группы"""
    try:
        db.connect()
        with db.atomic():
            if Group.select().where(Group.name == group.name).exists():
                raise HTTPException(400, f"Группа с названием '{group.name}' уже существует")
            
            new_group = Group.create(
                name=group.name,
                course=group.course,
                specialty_code=group.specialty_code,
                student_count=group.student_count,
                curator=group.curator
            )
        return new_group
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка при создании: {str(e)}")
    finally:
        db.close()

@app.put("/groups/{group_id}", response_model=GroupOut)
def update_group(group_id: int, group: GroupUpdate):
    """Обновление информации о группе"""
    try:
        db.connect()
        with db.atomic():
            if not Group.select().where(Group.id == group_id).exists():
                raise HTTPException(404, "Группа не найдена")
            
            update_data = {}
            if group.name is not None:
                if Group.select().where((Group.name == group.name) & (Group.id != group_id)).exists():
                    raise HTTPException(400, f"Группа с названием '{group.name}' уже существует")
                update_data['name'] = group.name
            if group.course is not None:
                update_data['course'] = group.course
            if group.student_count is not None:
                update_data['student_count'] = group.student_count
            if group.curator is not None:
                update_data['curator'] = group.curator
            
            if update_data:
                Group.update(update_data).where(Group.id == group_id).execute()
            
            updated = Group.get_by_id(group_id)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка при обновлении: {str(e)}")
    finally:
        db.close()

@app.delete("/groups/{group_id}")
def delete_group(group_id: int):
    """Удаление группы"""
    try:
        db.connect()
        with db.atomic():
            deleted = Group.delete().where(Group.id == group_id).execute()
        return {"deleted": bool(deleted), "message": "Группа удалена" if deleted else "Группа не найдена"}
    except Exception as e:
        raise HTTPException(500, f"Ошибка при удалении: {str(e)}")
    finally:
        db.close()

@app.get("/groups/{group_id}", response_model=GroupOut)
def get_group(group_id: int):
    """Получение группы по ID"""
    try:
        db.connect()
        try:
            group = Group.get_by_id(group_id)
            return group
        except Group.DoesNotExist:
            raise HTTPException(404, "Группа не найдена")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка при получении: {str(e)}")
    finally:
        db.close()

@app.get("/groups", response_model=List[GroupOut])
def list_groups(
    name: Optional[str] = None,
    course: Optional[int] = None,
    specialty_code: Optional[str] = None,
    curator: Optional[str] = None,
    min_students: Optional[int] = None,
    max_students: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
):
    """Получение списка групп с фильтрацией"""
    try:
        db.connect()
        query = Group.select()
        
        if name:
            query = query.where(Group.name.contains(name))
        if course:
            query = query.where(Group.course == course)
        if specialty_code:
            query = query.where(Group.specialty_code == specialty_code)
        if curator:
            query = query.where(Group.curator.contains(curator))
        if min_students is not None:
            query = query.where(Group.student_count >= min_students)
        if max_students is not None:
            query = query.where(Group.student_count <= max_students)
        
        return list(query.offset(offset).limit(limit))
    except Exception as e:
        raise HTTPException(500, f"Ошибка при получении списка: {str(e)}")
    finally:
        db.close()

@app.get("/")
def root():
    """Корневой эндпоинт"""
    return {
        "service": "Group Service",
        "version": "1.0",
        "description": "Сервис управления учебными группами СПО",
        "endpoints": {
            "POST /groups": "Создать группу",
            "GET /groups": "Список групп",
            "GET /groups/{id}": "Получить группу по ID",
            "PUT /groups/{id}": "Обновить группу",
            "DELETE /groups/{id}": "Удалить группу"
        }
    }

# ==================== ТОЧКА ВХОДА ====================
if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Запуск сервера Group Service...")
    print("Документация API: http://localhost:8001/docs")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8001)