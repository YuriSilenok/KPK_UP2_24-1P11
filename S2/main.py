from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
import re

from models import db, Profile, NotificationSetting

app = FastAPI(title="Profile Service", description="Сервис профилей (вариант №2)", version="1.0.0")


'''Pydantic схемы (валидация)'''

class ProfileCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    phone: str = Field(max_length=20)
    email: EmailStr
    photo_url: Optional[str] = Field(None, max_length=500)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        phone_pattern = re.compile(r'^\+?[\d\s\-\(\)]{10,20}$')
        if not phone_pattern.match(v):
            raise ValueError("Неверный формат телефона")
        return v


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    photo_url: Optional[str] = Field(None, max_length=500)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            phone_pattern = re.compile(r'^\+?[\d\s\-\(\)]{10,20}$')
            if not phone_pattern.match(v):
                raise ValueError("Неверный формат телефона")
        return v


class ProfileResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str]
    phone: str
    email: str
    photo_url: Optional[str]

    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    phone_notification: Optional[bool] = None
    email_notification: Optional[bool] = None


class NotificationResponse(BaseModel):
    profile_id: int
    phone_notification: bool
    email_notification: bool

    class Config:
        from_attributes = True


'''Dependency для подключения БД'''

def get_db():
    db.connect()
    try:
        yield
    finally:
        db.close()


'''Эндпоинты'''

@app.post("/profiles", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile_data: ProfileCreate, _: None = Depends(get_db)):
    """Создание профиля"""
    if Profile.select().where(Profile.phone == profile_data.phone).exists():
        raise HTTPException(status_code=400, detail="Телефон уже существует")
    
    if Profile.select().where(Profile.email == profile_data.email).exists():
        raise HTTPException(status_code=400, detail="Email уже существует")
    
    profile = Profile.create(
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        middle_name=profile_data.middle_name,
        phone=profile_data.phone,
        email=profile_data.email,
        photo_url=profile_data.photo_url
    )
    
    NotificationSetting.create(profile=profile)
    
    return ProfileResponse(
        id=profile.id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        middle_name=profile.middle_name,
        phone=profile.phone,
        email=profile.email,
        photo_url=profile.photo_url
    )


@app.put("/profiles/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: int, profile_data: ProfileUpdate, _: None = Depends(get_db)):
    """Изменение профиля по ID"""
    try:
        profile = Profile.get_by_id(profile_id)
    except Profile.DoesNotExist:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    
    if profile_data.phone is not None and profile_data.phone != profile.phone:
        if Profile.select().where(Profile.phone == profile_data.phone).exists():
            raise HTTPException(status_code=400, detail="Телефон уже существует")
        profile.phone = profile_data.phone
    
    if profile_data.email is not None and profile_data.email != profile.email:
        if Profile.select().where(Profile.email == profile_data.email).exists():
            raise HTTPException(status_code=400, detail="Email уже существует")
        profile.email = profile_data.email
    
    if profile_data.first_name is not None:
        profile.first_name = profile_data.first_name
    if profile_data.last_name is not None:
        profile.last_name = profile_data.last_name
    if profile_data.middle_name is not None:
        profile.middle_name = profile_data.middle_name
    if profile_data.photo_url is not None:
        profile.photo_url = profile_data.photo_url
    
    profile.save()
    
    return ProfileResponse(
        id=profile.id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        middle_name=profile.middle_name,
        phone=profile.phone,
        email=profile.email,
        photo_url=profile.photo_url
    )


@app.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: int, _: None = Depends(get_db)):
    """Удаление профиля по ID"""
    try:
        profile = Profile.get_by_id(profile_id)
    except Profile.DoesNotExist:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    
    profile.delete_instance()
    return JSONResponse(content={"deleted": True, "profile_id": profile_id})


@app.get("/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: int, _: None = Depends(get_db)):
    """Получить профиль по ID"""
    try:
        profile = Profile.get_by_id(profile_id)
    except Profile.DoesNotExist:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    
    return ProfileResponse(
        id=profile.id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        middle_name=profile.middle_name,
        phone=profile.phone,
        email=profile.email,
        photo_url=profile.photo_url
    )


@app.get("/profiles", response_model=List[ProfileResponse])
async def get_profiles(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    _: None = Depends(get_db)
):
    """Получить список профилей по заданным параметрам"""
    query = Profile.select()
    
    if first_name:
        query = query.where(Profile.first_name == first_name)
    if last_name:
        query = query.where(Profile.last_name == last_name)
    if phone:
        query = query.where(Profile.phone == phone)
    if email:
        query = query.where(Profile.email == email)
    
    profiles = list(query)
    
    return [
        ProfileResponse(
            id=p.id,
            first_name=p.first_name,
            last_name=p.last_name,
            middle_name=p.middle_name,
            phone=p.phone,
            email=p.email,
            photo_url=p.photo_url
        )
        for p in profiles
    ]


@app.patch("/profiles/{profile_id}/notifications", response_model=NotificationResponse)
async def update_notification_settings(
    profile_id: int,
    notification_data: NotificationUpdate,
    _: None = Depends(get_db)
):
    """Изменить настройки уведомлений"""
    try:
        profile = Profile.get_by_id(profile_id)
    except Profile.DoesNotExist:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    
    try:
        settings = NotificationSetting.get(NotificationSetting.profile == profile.id)
    except NotificationSetting.DoesNotExist:
        raise HTTPException(status_code=404, detail="Настройки уведомлений не найдены")
    
    if notification_data.phone_notification is not None:
        settings.phone_notification = notification_data.phone_notification
    if notification_data.email_notification is not None:
        settings.email_notification = notification_data.email_notification
    
    settings.save()
    
    return NotificationResponse(
        profile_id=profile.id,
        phone_notification=settings.phone_notification,
        email_notification=settings.email_notification
    )


@app.get("/profiles/{profile_id}/notifications", response_model=NotificationResponse)
async def get_notification_settings(profile_id: int, _: None = Depends(get_db)):
    """Получить настройки уведомлений по profile_id"""
    try:
        profile = Profile.get_by_id(profile_id)
    except Profile.DoesNotExist:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    
    try:
        settings = NotificationSetting.get(NotificationSetting.profile == profile.id)
    except NotificationSetting.DoesNotExist:
        raise HTTPException(status_code=404, detail="Настройки уведомлений не найдены")
    
    return NotificationResponse(
        profile_id=profile.id,
        phone_notification=settings.phone_notification,
        email_notification=settings.email_notification
    )


'''Точка входа'''
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)