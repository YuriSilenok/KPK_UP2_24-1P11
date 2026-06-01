from contextlib import asynccontextmanager
from peewee import SqliteDatabase, Model, IntegerField, FloatField, BooleanField
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

# ==================== БАЗА ДАННЫХ ====================
db = SqliteDatabase('workload.db')

class CalculatedLoad(Model):
    """Результат расчёта нагрузки преподавателя"""
    teacher_id = IntegerField(null=False, verbose_name="ID преподавателя")
    period_id = IntegerField(null=False, verbose_name="ID учебного периода")
    total_hours = FloatField(null=False, verbose_name="Общая нагрузка за период")
    is_active = BooleanField(default=True, verbose_name="Активна ли запись")

    class Meta:
        database = db
        table_name = 'calculated_loads'

def init_db():
    """Функция инициализации базы данных"""
    db.connect()
    db.create_tables([CalculatedLoad], safe=True)
    db.close()

# ==================== СХЕМЫ PYDANTIC ====================
class CalculateLoadRequest(BaseModel):
    """Запрос на расчёт нагрузки"""
    teacher_id: int = Field(..., gt=0, description="ID преподавателя")
    period_id: int = Field(..., gt=0, description="ID учебного периода")

class CalculatedLoadOut(BaseModel):
    """Схема для ответа"""
    id: int
    teacher_id: int
    period_id: int
    total_hours: float
    is_active: bool

class CalculatedLoadUpdate(BaseModel):
    """Ручное обновление нагрузки"""
    total_hours: Optional[float] = Field(None, ge=0, description="Общая нагрузка")

# ==================== LIFESPAN ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    print("Запуск Load Calculation Service...")
    init_db()
    print("База данных инициализирована")
    yield
    print("Остановка сервера...")
    if not db.is_closed():
        db.close()
    print("Ресурсы освобождены")

# ==================== FASTAPI ПРИЛОЖЕНИЕ ====================
app = FastAPI(
    title="Load Calculation Service",
    description="Сервис автоматического расчёта нагрузки преподавателя",
    version="1.0",
    lifespan=lifespan
)

# ==================== ФУНКЦИЯ РАСЧЁТА (ЗАГЛУШКА) ====================
async def calculate_total_hours(teacher_id: int, period_id: int) -> float:
    """
    Автоматический расчёт нагрузки преподавателя за период.
    В реальном микросервисе здесь были бы запросы к:
    - Load Assignment Service (закрепления преподавателя)
    - Curriculum Plan Service (часы по плану)
    - Group Service (количество групп)
    """
    # Заглушка: возвращает тестовое значение
    # При реальной интеграции заменить на httpx запросы к другим сервисам
    return round(teacher_id * period_id * 18, 2)

# ==================== ЭНДПОИНТЫ ====================
@app.post("/calculate", response_model=CalculatedLoadOut, status_code=201)
async def calculate_and_save(request: CalculateLoadRequest):
    """Автоматический расчёт нагрузки и сохранение результата"""
    try:
        total_hours = await calculate_total_hours(request.teacher_id, request.period_id)
        
        db.connect()
        with db.atomic():
            existing = CalculatedLoad.get_or_none(
                (CalculatedLoad.teacher_id == request.teacher_id) &
                (CalculatedLoad.period_id == request.period_id) &
                (CalculatedLoad.is_active == True)
            )
            if existing:
                raise HTTPException(400, "Расчёт для этого преподавателя и периода уже существует")
            
            new_load = CalculatedLoad.create(
                teacher_id=request.teacher_id,
                period_id=request.period_id,
                total_hours=total_hours,
                is_active=True
            )
        return new_load
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка при расчёте: {str(e)}")
    finally:
        db.close()

@app.put("/loads/{load_id}", response_model=CalculatedLoadOut)
def update_load(load_id: int, update_data: CalculatedLoadUpdate):
    """Ручное изменение нагрузки"""
    try:
        db.connect()
        with db.atomic():
            existing = CalculatedLoad.get_or_none(
                (CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True)
            )
            if not existing:
                raise HTTPException(404, "Запись не найдена")
            
            if update_data.total_hours is not None:
                CalculatedLoad.update(total_hours=update_data.total_hours).where(
                    CalculatedLoad.id == load_id
                ).execute()
            
            updated = CalculatedLoad.get_by_id(load_id)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка при обновлении: {str(e)}")
    finally:
        db.close()

@app.delete("/loads/{load_id}")
def delete_load(load_id: int):
    """Мягкое удаление"""
    try:
        db.connect()
        with db.atomic():
            existing = CalculatedLoad.get_or_none(
                (CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True)
            )
            if not existing:
                return False
            
            CalculatedLoad.update(is_active=False).where(CalculatedLoad.id == load_id).execute()
            return True
    except Exception as e:
        raise HTTPException(500, f"Ошибка при удалении: {str(e)}")
    finally:
        db.close()

@app.get("/loads/{load_id}", response_model=CalculatedLoadOut)
def get_load(load_id: int):
    """Получение расчёта по ID"""
    try:
        db.connect()
        load = CalculatedLoad.get_or_none(
            (CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True)
        )
        if not load:
            raise HTTPException(404, "Запись не найдена")
        return load
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка при получении: {str(e)}")
    finally:
        db.close()

@app.get("/loads", response_model=List[CalculatedLoadOut])
def list_loads(
    teacher_id: Optional[int] = None,
    period_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
):
    """Список расчётов с фильтрацией"""
    try:
        db.connect()
        query = CalculatedLoad.select().where(CalculatedLoad.is_active == True)
        
        if teacher_id:
            query = query.where(CalculatedLoad.teacher_id == teacher_id)
        if period_id:
            query = query.where(CalculatedLoad.period_id == period_id)
        
        return list(query.offset(offset).limit(limit))
    except Exception as e:
        raise HTTPException(500, f"Ошибка при получении списка: {str(e)}")
    finally:
        db.close()

@app.get("/teachers/{teacher_id}/loads", response_model=List[CalculatedLoadOut])
def get_teacher_loads(teacher_id: int):
    """Вся нагрузка преподавателя по всем периодам"""
    try:
        db.connect()
        loads = list(CalculatedLoad.select().where(
            (CalculatedLoad.teacher_id == teacher_id) & (CalculatedLoad.is_active == True)
        ))
        return loads
    except Exception as e:
        raise HTTPException(500, f"Ошибка при получении: {str(e)}")
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "service": "Load Calculation Service",
        "version": "1.0",
        "description": "Автоматический расчёт нагрузки преподавателя",
        "formula": "total_hours = sum(plan_hours × groups_count)",
        "endpoints": {
            "POST /calculate": "Автоматический расчёт и сохранение",
            "GET /loads": "Список расчётов",
            "GET /loads/{id}": "Получить расчёт по ID",
            "PUT /loads/{id}": "Ручное изменение",
            "DELETE /loads/{id}": "Мягкое удаление",
            "GET /teachers/{id}/loads": "Нагрузка преподавателя"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)