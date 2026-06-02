from datetime import datetime
from peewee import *


database = SqliteDatabase("resource_pool.db")


class BaseModel(Model):
    class Meta:
        database = database


class ResourceCategory(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField(
        max_length=100, unique=True, constraints=[Check("length(name) >= 1")]
    )
    description = CharField(max_length=500, null=True)

    class Meta:
        table_name = "resource_categories"


class Person(BaseModel):
    id = AutoField(primary_key=True)
    login = CharField(max_length=50, unique=True)
    email = CharField(max_length=100, unique=True)

    class Meta:
        table_name = "persons"


class Asset(BaseModel):
    id = AutoField(primary_key=True)

    name = CharField(max_length=100, constraints=[Check("length(name) >= 1")])
    description = CharField(max_length=500, null=True)
    category_id = ForeignKeyField(
        ResourceCategory,
        backref="assets",
        on_delete="RESTRICT",
        column_name="category_id",
    )
    total_quantity = IntegerField(constraints=[Check("total_quantity >= 1")], default=1)
    unit = CharField(max_length=10, choices=["шт", "компл", "экз"], default="шт")
    status = CharField(
        max_length=20,
        choices=["available", "maintenance", "retired"],
        default="available",
    )

    is_active = BooleanField(default=True)

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "assets"
        # Уникальный составной индекс
        indexes = ((('name', 'category_id'), True),)

    @property
    def available_quantity(self):
        """Вычисление доступного количества с оптимизацией запроса"""
        from peewee import fn
        
        # Оптимизированный запрос с использованием подзапроса
        booked_sum = (
            Booking.select(fn.COALESCE(fn.SUM(Booking.amount), 0))
            .where((Booking.asset == self.id) & (Booking.booking_status == "active"))
            .scalar()
        )
        return self.total_quantity - booked_sum

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        try:
            result = super().save(*args, **kwargs)
            return result
        except Exception as e:
            self.updated_at = self._get_original_updated_at()
            raise e

    def _get_original_updated_at(self):
        if self.id:
            original = Asset.get_or_none(Asset.id == self.id)
            if original:
                return original.updated_at
        return self.updated_at

    def to_dict(self):
        """Безопасное преобразование в словарь"""
        category_id_value = None
        if self.category_id:
            if isinstance(self.category_id, ResourceCategory):
                category_id_value = self.category_id.id
            elif hasattr(self, '_data') and 'category_id' in self._data:
                category_id_value = self._data['category_id']
        
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category_id": category_id_value,
            "total_quantity": self.total_quantity,
            "available_quantity": self.available_quantity,
            "unit": self.unit,
            "status": self.status,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def disable(cls, asset_id):
        """
        Деактивация ресурса
        Returns:
            bool: True если ресурс деактивирован или уже неактивен,
                  False если ресурс не найден
        """
        asset = cls.get_or_none(cls.id == asset_id)
        if not asset:
            return False
        
        if not asset.is_active:
            return True
        
        affected = (
            cls.update(is_active=False)
            .where((cls.id == asset_id) & (cls.is_active == True))
            .execute()
        )
        return affected > 0

    @classmethod
    def get_active(cls, asset_id):
        """Получение активного ресурса по ID"""
        return cls.get_or_none((cls.id == asset_id) & (cls.is_active == True))

    @classmethod
    def get_filtered_list(cls, limit=20, offset=0, search=None, 
                          category_id=None, status=None, only_active=True):
        """
        Получение списка ресурсов с фильтрацией и пагинацией
        
        Args:
            limit: количество записей (1-100)
            offset: смещение (>=0)
            search: поиск по имени
            category_id: фильтр по категории
            status: фильтр по статусу
            only_active: показывать только активные ресурсы
        
        Returns:
            Список ресурсов
        """
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")
        if not isinstance(offset, int) or offset < 0:
            raise ValueError("offset must be >= 0")
        
        query = cls.select()
        
        if only_active:
            query = query.where(cls.is_active == True)
        
        if search:
            query = query.where(cls.name.contains(search))
        
        if category_id:
            query = query.where(cls.category_id == category_id)
        
        if status:
            query = query.where(cls.status == status)
        
        return query.limit(limit).offset(offset)

    @classmethod
    def search_by_name(cls, search_term, limit=20, offset=0, only_active=True):
        """
        Поиск ресурсов по имени
        
        Args:
            search_term: поисковый запрос
            limit: количество записей (1-100)
            offset: смещение (>=0)
            only_active: показывать только активные ресурсы
        """
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")
        if not isinstance(offset, int) or offset < 0:
            raise ValueError("offset must be >= 0")
        
        query = cls.select()
        
        if only_active:
            query = query.where(cls.is_active == True)
        
        query = query.where(cls.name.contains(search_term))
        return query.limit(limit).offset(offset)

    @classmethod
    def get_by_category(cls, category_id, limit=20, offset=0, only_active=True):
        """Получение ресурсов по категории"""
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")
        if not isinstance(offset, int) or offset < 0:
            raise ValueError("offset must be >= 0")
        
        query = cls.select().where(cls.category_id == category_id)
        
        if only_active:
            query = query.where(cls.is_active == True)
        
        return query.limit(limit).offset(offset)

    @classmethod
    def get_by_status(cls, status, limit=20, offset=0, only_active=True):
        """Получение ресурсов по статусу"""
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")
        if not isinstance(offset, int) or offset < 0:
            raise ValueError("offset must be >= 0")
        
        query = cls.select().where(cls.status == status)
        
        if only_active:
            query = query.where(cls.is_active == True)
        
        return query.limit(limit).offset(offset)


class Booking(BaseModel):
    id = AutoField(primary_key=True)
    asset = ForeignKeyField(Asset, backref="bookings", on_delete="CASCADE")
    booked_by = ForeignKeyField(Person, backref="bookings", on_delete="CASCADE")
    amount = IntegerField(constraints=[Check("amount >= 1")], default=1)
    start_dt = DateTimeField()
    end_dt = DateTimeField()
    reason = TextField(null=True)
    booking_status = CharField(
        max_length=20, choices=["active", "completed", "cancelled"], default="active"
    )
    created_dt = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "bookings"

    def save(self, *args, **kwargs):
        if self.start_dt and self.end_dt and self.start_dt >= self.end_dt:
            raise ValueError("start_dt must be less than end_dt")
        
        if self.booking_status == "active":
            asset_id = self.asset.id if hasattr(self.asset, 'id') else self.asset
            asset = Asset.get_or_none(Asset.id == asset_id)
            if asset:
                if self.amount > asset.available_quantity:
                    raise ValueError(f"Cannot book {self.amount} units. Only {asset.available_quantity} available")
        
        return super().save(*args, **kwargs)

    @classmethod
    def create_booking(cls, asset_id, person_id, amount, start_dt, end_dt, reason=None):
        """Создание нового бронирования"""
        asset = Asset.get_or_none(Asset.id == asset_id)
        if not asset or not asset.is_active:
            raise ValueError("Asset not found or inactive")
        
        person = Person.get_or_none(Person.id == person_id)
        if not person:
            raise ValueError("Person not found")
        
        if start_dt >= end_dt:
            raise ValueError("start_dt must be less than end_dt")
        
        if amount <= 0:
            raise ValueError("amount must be positive")
        
        if amount > asset.available_quantity:
            raise ValueError(f"Cannot book {amount} units. Only {asset.available_quantity} available")
        
        return cls.create(
            asset=asset_id,
            booked_by=person_id,
            amount=amount,
            start_dt=start_dt,
            end_dt=end_dt,
            reason=reason,
            booking_status="active"
        )

    @classmethod
    def get_active_bookings(cls, asset_id=None, person_id=None):
        """Получение активных бронирований"""
        query = cls.select().where(cls.booking_status == "active")
        
        if asset_id:
            query = query.where(cls.asset == asset_id)
        
        if person_id:
            query = query.where(cls.booked_by == person_id)
        
        return query

    @classmethod
    def complete_booking(cls, booking_id):
        """Завершение бронирования"""
        booking = cls.get_or_none(cls.id == booking_id)
        if not booking:
            return False
        
        if booking.booking_status == "active":
            booking.booking_status = "completed"
            booking.save()
            return True
        
        return False

    @classmethod
    def cancel_booking(cls, booking_id):
        """Отмена бронирования"""
        booking = cls.get_or_none(cls.id == booking_id)
        if not booking:
            return False
        
        if booking.booking_status == "active":
            booking.booking_status = "cancelled"
            booking.save()
            return True
        
        return False


def initialize_database():
    """Инициализация базы данных"""
    database.connect()
    database.create_tables([ResourceCategory, Asset, Person, Booking], safe=True)
    
    # Создание дополнительных индексов для оптимизации
    try:
        # Уникальный индекс для комбинации name и category_id
        database.execute_sql("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_name_category 
            ON assets (name, category_id)
        """)
        
        # Индексы для оптимизации поиска
        database.execute_sql("""
            CREATE INDEX IF NOT EXISTS idx_assets_status 
            ON assets (status)
        """)
        
        database.execute_sql("""
            CREATE INDEX IF NOT EXISTS idx_assets_is_active 
            ON assets (is_active)
        """)
        
        database.execute_sql("""
            CREATE INDEX IF NOT EXISTS idx_bookings_status 
            ON bookings (booking_status)
        """)
        
        database.execute_sql("""
            CREATE INDEX IF NOT EXISTS idx_bookings_dates 
            ON bookings (start_dt, end_dt)
        """)
    except Exception as e:
        print(f"Note: Index creation warning: {e}")
    
    # Заполнение тестовыми данными, если их нет
    if not ResourceCategory.select().exists():
        ResourceCategory.create(
            name="Спортивный инвентарь", description="Мячи, маты и т.д."
        )
        ResourceCategory.create(name="Библиотечный фонд", description="Книги, учебники")
        ResourceCategory.create(
            name="Лабораторное оборудование", description="Приборы и инструменты"
        )
    
    if not Person.select().exists():
        Person.create(login="teacher1", email="teacher1@gmail.com")
        Person.create(login="student1", email="student1@gmail.com")
    
    if not Asset.select().exists():
        sport_category = ResourceCategory.get(name="Спортивный инвентарь")
        
        Asset.create(
            name="мяч",
            description="Wilson Evolution",
            category_id=sport_category.id,
            total_quantity=100,
            unit="шт",
        )
        
        Asset.create(
            name="мат",
            category_id=sport_category.id,
            total_quantity=50,
            unit="шт",
            status="maintenance",
        )


def init_db():
    """Инициализация базы данных с выводом сообщения"""
    initialize_database()
    print("База данных инициализирована в соответствии со спецификацией doc.md")


def main():
    init_db()
    
    # Пример использования методов фильтрации
    print("\n--- Примеры использования ---")
    
    # Получение списка с фильтрацией
    assets = Asset.get_filtered_list(limit=10, offset=0, search="мяч")
    for asset in assets:
        print(f"Найден ресурс: {asset.name} (Доступно: {asset.available_quantity})")
    
    # Получение по категории
    sport_cat = ResourceCategory.get(name="Спортивный инвентарь")
    sport_assets = Asset.get_by_category(sport_cat.id)
    print(f"\nСпортивный инвентарь ({sport_assets.count()} шт):")
    for asset in sport_assets:
        print(f"  - {asset.name}")
    
    # Получение по статусу
    maintenance_assets = Asset.get_by_status("maintenance")
    print(f"\nРесурсы на обслуживании ({maintenance_assets.count()} шт):")
    for asset in maintenance_assets:
        print(f"  - {asset.name}")


if __name__ == "__main__":
    main()