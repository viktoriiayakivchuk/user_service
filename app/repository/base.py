from typing import Generic, Type, TypeVar, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get(self, id: Any) -> ModelType | None:
        result = await self.db_session.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def create(self, obj_in_data: dict) -> ModelType:
        db_obj = self.model(**obj_in_data)
        self.db_session.add(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in_data: dict) -> ModelType:
        for field in obj_in_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in_data[field])
        self.db_session.add(db_obj)
        return db_obj