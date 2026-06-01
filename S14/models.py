from contextlib import asynccontextmanager
from peewee import SqliteDatabase, Model, IntegerField, FloatField, BooleanField, PrimaryKeyField
from peewee import IntegrityError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import httpx

db = SqliteDatabase('workload.db')

class CalculatedLoad(Model):
    id = PrimaryKeyField()
    teacher_id = IntegerField(null=False, constraints=[Check('teacher_id > 0')])
    period_id = IntegerField(null=False, constraints=[Check('period_id > 0')])
    total_hours = FloatField(null=False, constraints=[Check('total_hours >= 0')])
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = 'calculated_loads'
        indexes = ((('teacher_id', 'period_id'), True),)

def init_db():
    db.connect()
    db.create_tables([CalculatedLoad], safe=True)
    db.close()

class CalculateLoadRequest(BaseModel):
    teacher_id: int = Field(..., gt=0)
    period_id: int = Field(..., gt=0)

class CalculatedLoadOut(BaseModel):
    id: int
    teacher_id: int
    period_id: int
    total_hours: float = Field(..., description="Округлено до 2 знаков")

    @field_validator('total_hours', mode='before')
    @classmethod
    def round_total_hours(cls, v: float) -> float:
        return round(v, 2)

class CalculatedLoadUpdate(BaseModel):
    total_hours: Optional[float] = Field(None, ge=0)

    @field_validator('total_hours', mode='before')
    @classmethod
    def round_update_hours(cls, v: Optional[float]) -> Optional[float]:
        return round(v, 2) if v is not None else v

class DeleteResponse(BaseModel):
    result: bool

LOAD_ASSIGNMENT_URL = "http://localhost:8006"
CURRICULUM_PLAN_URL = "http://localhost:8004"
GROUP_URL = "http://localhost:8005"

async def get_teacher_assignments(teacher_id: int) -> List[dict]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{LOAD_ASSIGNMENT_URL}/assignments?teacher_id={teacher_id}", timeout=5.0)
            if response.status_code != 200:
                raise HTTPException(502, "Load Assignment Service error")
            return response.json()
        except:
            raise HTTPException(502, "Load Assignment Service unavailable")

async def get_curriculum_plan(plan_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CURRICULUM_PLAN_URL}/plans/{plan_id}", timeout=5.0)
            if response.status_code != 200:
                raise HTTPException(502, "Curriculum Plan Service error")
            return response.json()
        except:
            raise HTTPException(502, "Curriculum Plan Service unavailable")

async def get_groups_count(plan_id: int) -> int:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{GROUP_URL}/groups?plan_id={plan_id}", timeout=5.0)
            if response.status_code != 200:
                raise HTTPException(502, "Group Service error")
            return len(response.json())
        except:
            raise HTTPException(502, "Group Service unavailable")

async def calculate_total_hours(teacher_id: int, period_id: int) -> float:
    assignments = await get_teacher_assignments(teacher_id)
    total = 0.0
    for assignment in assignments:
        plan = await get_curriculum_plan(assignment['curriculum_plan_id'])
        groups_count = await get_groups_count(plan['id'])
        total += plan.get('total_hours', 0) * groups_count
    return round(total, 2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    if not db.is_closed():
        db.close()

app = FastAPI(title="Load Calculation Service", lifespan=lifespan)

@app.post("/calculate", response_model=CalculatedLoadOut, status_code=201)
async def calculate_and_save(request: CalculateLoadRequest):
    try:
        db.connect()
        total_hours = await calculate_total_hours(request.teacher_id, request.period_id)
        with db.atomic():
            try:
                new_load = CalculatedLoad.create(
                    teacher_id=request.teacher_id,
                    period_id=request.period_id,
                    total_hours=total_hours,
                    is_active=True
                )
            except IntegrityError:
                raise HTTPException(400, "Расчёт для этого преподавателя и периода уже существует")
        return CalculatedLoadOut.model_validate(new_load)
    except HTTPException:
        raise
    finally:
        db.close()

@app.put("/loads/{load_id}", response_model=CalculatedLoadOut)
def update_load(load_id: int, update_data: CalculatedLoadUpdate):
    try:
        db.connect()
        with db.atomic():
            existing = CalculatedLoad.get_or_none((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
            if not existing:
                raise HTTPException(404, "Not found")
            if update_data.total_hours is not None:
                CalculatedLoad.update(total_hours=update_data.total_hours).where(CalculatedLoad.id == load_id).execute()
        return CalculatedLoadOut.model_validate(CalculatedLoad.get_by_id(load_id))
    except HTTPException:
        raise
    finally:
        db.close()

@app.delete("/loads/{load_id}", response_model=DeleteResponse)
def delete_load(load_id: int):
    try:
        db.connect()
        with db.atomic():
            existing = CalculatedLoad.get_or_none((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
            if not existing:
                return DeleteResponse(result=False)
            CalculatedLoad.update(is_active=False).where(CalculatedLoad.id == load_id).execute()
            return DeleteResponse(result=True)
    finally:
        db.close()

@app.get("/loads/{load_id}", response_model=CalculatedLoadOut)
def get_load(load_id: int):
    try:
        db.connect()
        load = CalculatedLoad.get_or_none((CalculatedLoad.id == load_id) & (CalculatedLoad.is_active == True))
        if not load:
            raise HTTPException(404, "Not found")
        return CalculatedLoadOut.model_validate(load)
    except HTTPException:
        raise
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
        db.connect()
        query = CalculatedLoad.select().where(CalculatedLoad.is_active == True)
        if teacher_id:
            if teacher_id <= 0:
                raise HTTPException(400, "teacher_id должен быть > 0")
            query = query.where(CalculatedLoad.teacher_id == teacher_id)
        if period_id:
            if period_id <= 0:
                raise HTTPException(400, "period_id должен быть > 0")
            query = query.where(CalculatedLoad.period_id == period_id)
        if limit < 1 or limit > 1000:
            raise HTTPException(400, "limit должен быть 1-1000")
        if offset < 0:
            raise HTTPException(400, "offset должен быть >= 0")
        loads = list(query.offset(offset).limit(limit))
        return [CalculatedLoadOut.model_validate(load) for load in loads]
    except HTTPException:
        raise
    finally:
        db.close()

@app.get("/teachers/{teacher_id}/loads", response_model=List[CalculatedLoadOut])
def get_teacher_loads(teacher_id: int, limit: int = 100, offset: int = 0):
    try:
        db.connect()
        if teacher_id <= 0:
            raise HTTPException(400, "teacher_id должен быть > 0")
        if limit < 1 or limit > 1000:
            raise HTTPException(400, "limit должен быть 1-1000")
        if offset < 0:
            raise HTTPException(400, "offset должен быть >= 0")
        loads = list(CalculatedLoad.select().where(
            (CalculatedLoad.teacher_id == teacher_id) & (CalculatedLoad.is_active == True)
        ).offset(offset).limit(limit))
        return [CalculatedLoadOut.model_validate(load) for load in loads]
    except HTTPException:
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)