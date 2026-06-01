from contextlib import asynccontextmanager
from peewee import SqliteDatabase, Model, IntegerField, FloatField, BooleanField, PrimaryKeyField, Check
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import httpx

# ==================== БАЗА ДАННЫХ ====================
db = SqliteDatabase('workload.db')

class CalculatedLoad(Model):
    """Результат расчёта нагрузки преподавателя"""
    id = PrimaryKeyField()
    teacher_id = IntegerField(null=False, verbose_name="ID преподавателя")
    period_id = IntegerField(null=False, verbose_name="ID учебного периода")
    total_hours = FloatField(null=False, verbose_name="Общая нагрузка за период")
    is_active = BooleanField(default=True, verbose_name="Активна ли запись")

    class Meta:
        database = db
        table_name = 'calculated_loads'
        indexes = (
            (('teacher_id', 'period_id'), True),
        )
        constraints = [
            Check('teacher_id > 0'),
            Check('period_id > 0'),
            Check('total_hours >= 0')
        ]

def init_db():
    db.connect()
    db.create_tables([CalculatedLoad], safe=True)
    db.close()

# ==================== СХЕМЫ PYDANTIC ====================
class CalculateLoadRequest(BaseModel):
    teacher_id: int = Field(..., gt=0, description="ID преподавателя")
    period_id: int = Field(..., gt=0, description="ID учебного периода")

    @field_validator('teacher_id', 'period_id')
    @classmethod
    def validate_positive(cls, v: int, info) -> int:
        if v <= 0:
            raise ValueError(f'{info.field_name} должен быть больше 0')
        return v

class CalculatedLoadOut(BaseModel):
    id: int
    teacher_id: int
    period_id: int
    total_hours: float = Field(..., description="Общая нагрузка (округлено до 2 знаков)")

class CalculatedLoadUpdate(BaseModel):
    total_hours: Optional[float] = Field(None, ge=0, description="Новое значение нагрузки")

class DeleteResponse(BaseModel):
    result: bool

# ==================== КОНФИГУРАЦИЯ ====================
LOAD_ASSIGNMENT_URL = "http://localhost:8006"
CURRICULUM_PLAN_URL = "http://localhost:8004"
GROUP_URL = "http://localhost:8005"

# ==================== ФУНКЦИИ ЗАПРОСОВ К ДРУГИМ СЕРВИСАМ ====================
async def get_teacher_assignments(teacher_id: int) -> List[dict]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{LOAD_ASSIGNMENT_URL}/assignments?teacher_id={teacher_id}", timeout=5.0)
            if response.status_code != 200:
                raise HTTPException(502, f"Load Assignment Service ошибка: {response.status_code}")
            return response.json()
        except (httpx.TimeoutException, httpx.ConnectError):
            raise HTTPException(502, "Не удалось подключиться к Load Assignment Service")

async def get_curriculum_plan(plan_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CURRICULUM_PLAN_URL}/plans/{plan_id}", timeout=5.0)
            if response.status_code != 200:
                raise HTTPException(502, f"Curriculum Plan Service ошибка: {response.status_code}")
            return response.json()
        except (httpx.TimeoutException, httpx.ConnectError):
            raise HTTPException(502, "Не удалось подключиться к Curriculum Plan Service")

async def get_groups_count(plan_id: int) -> int:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{GROUP_URL}/groups?plan_id={plan_id}", timeout=5.0)
            if response.status_code != 200:
                raise HTTPException(502, f"Group Service ошибка: {response.status_code}")
            return len(response.json())
        except (httpx.TimeoutException, httpx.ConnectError):
            raise HTTPException(502, "Не удалось подключиться к Group Service")

async def calculate_total_hours(teacher_id: int, period_id: int) -> float:
    assignments = await get_teacher_assignments(teacher_id)
    total = 0.0
    for assignment in assignments:
        plan = await get_curriculum_plan(assignment['curriculum_plan_id'])
        groups_count = await get_groups_count(plan['id'])
        plan_hours = plan.get('total_hours', 0)
        total += plan_hours * groups_count
    return round(total, 2)

# ==================== LIFESPAN ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск Load Calculation Service...")
    init_db()
    print("База данных инициализирована")
    yield
    print("Остановка сервера...")
    if not db.is_closed():
        db.close()

# ==================== FASTAPI ПРИЛОЖЕНИЕ ====================
app = FastAPI(
    title="Load Calculation Service",
    description="Сервис автоматического расчёта нагрузки преподавателя",
    version="1.0",
    lifespan=lifespan
)

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def validate_positive(value: Optional[int], param_name: str):
    if value is not None and value <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{param_name} должен быть больше 0")

def validate_limit(limit: int):
    if limit < 1 or limit > 1000:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "limit должен быть в диапазоне 1-1000")

def validate_offset(offset: int):
    if offset < 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "offset должен быть >= 0")

# ==================== ЭНДПОИНТЫ ====================
@app.post("/calculate", response_model=CalculatedLoadOut, status_code=201)
async def calculate_and_save(request: CalculateLoadRequest):
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
        return CalculatedLoadOut(
            id=new_load.id,
            teacher_id=new_load.teacher_id,
            period_id=new_load.period_id,
            total_hours=new_load.total_hours
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка при расчёте: {str(e)}")
    finally:
        db.close()

@app.put("/loads/{load_id}", response_model=CalculatedLoadOut)
def update_load(load_id: int, update_data: CalculatedLoadUpdate):
    try:
        db.connect()
        with db.atomic():
            existing = CalculatedLoad.get_or_none(
                (CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True)
            )
            if not existing:
                raise HTTPException(404, "Запись не найдена")
            
            # Если total_hours = None, оставляем старое значение (изменения нет)
            if update_data.total_hours is not None:
                CalculatedLoad.update(total_hours=update_data.total_hours).where(
                    CalculatedLoad.id == load_id
                ).execute()
                new_total_hours = update_data.total_hours
            else:
                new_total_hours = existing.total_hours
            
            return CalculatedLoadOut(
                id=load_id,
                teacher_id=existing.teacher_id,
                period_id=existing.period_id,
                total_hours=new_total_hours
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка при обновлении: {str(e)}")
    finally:
        db.close()

@app.delete("/loads/{load_id}", response_model=DeleteResponse)
def delete_load(load_id: int):
    try:
        db.connect()
        with db.atomic():
            existing = CalculatedLoad.get_or_none(
                (CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True)
            )
            if not existing:
                return DeleteResponse(result=False)
            
            CalculatedLoad.update(is_active=False).where(CalculatedLoad.id == load_id).execute()
            return DeleteResponse(result=True)
    except Exception as e:
        raise HTTPException(500, f"Ошибка при удалении: {str(e)}")
    finally:
        db.close()

@app.get("/loads/{load_id}", response_model=CalculatedLoadOut)
def get_load(load_id: int):
    try:
        db.connect()
        load = CalculatedLoad.get_or_none(
            (CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True)
        )
        if not load:
            raise HTTPException(404, "Запись не найдена")
        return CalculatedLoadOut(
            id=load.id,
            teacher_id=load.teacher_id,
            period_id=load.period_id,
            total_hours=load.total_hours
        )
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
    try:
        validate_positive(teacher_id, "teacher_id")
        validate_positive(period_id, "period_id")
        validate_limit(limit)
        validate_offset(offset)
        
        db.connect()
        query = CalculatedLoad.select().where(CalculatedLoad.is_active == True)
        
        if teacher_id is not None:
            query = query.where(CalculatedLoad.teacher_id == teacher_id)
        if period_id is not None:
            query = query.where(CalculatedLoad.period_id == period_id)
        
        loads = list(query.offset(offset).limit(limit))
        
        return [
            CalculatedLoadOut(
                id=load.id,
                teacher_id=load.teacher_id,
                period_id=load.period_id,
                total_hours=load.total_hours
            )
            for load in loads
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка при получении списка: {str(e)}")
    finally:
        db.close()

@app.get("/teachers/{teacher_id}/loads", response_model=List[CalculatedLoadOut])
def get_teacher_loads(
    teacher_id: int,
    limit: int = 100,
    offset: int = 0
):
    try:
        if teacher_id <= 0:
            raise HTTPException(400, "teacher_id должен быть больше 0")
        validate_limit(limit)
        validate_offset(offset)
        
        db.connect()
        loads = list(CalculatedLoad.select().where(
            (CalculatedLoad.teacher_id == teacher_id) & (CalculatedLoad.is_active == True)
        ).offset(offset).limit(limit))
        
        return [
            CalculatedLoadOut(
                id=load.id,
                teacher_id=load.teacher_id,
                period_id=load.period_id,
                total_hours=load.total_hours
            )
            for load in loads
        ]
    except HTTPException:
        raise
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
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)