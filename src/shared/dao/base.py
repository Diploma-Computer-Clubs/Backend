from sqlalchemy import select, insert, update as sqlalchemy_update, delete as sqlalchemy_delete, func
from sqlalchemy.exc import SQLAlchemyError
from src.shared.configurations.database import async_session_maker

class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls, *options, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by).options(*options)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_one_or_none(cls, *options, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by).options(*options)
            result = await session.execute(query)
            return result.unique().scalar_one_or_none()

    @classmethod
    async def count(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(func.count(cls.model.id)).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def add(cls, **values):
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                return new_instance

    @classmethod
    async def add_list(cls, data: list[dict]):
        async with async_session_maker() as session:
            query = insert(cls.model).values(data).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalars().all()

    @classmethod
    async def update(cls, filter_by: dict, **values):
        async with async_session_maker() as session:
            async with session.begin():
                query = (
                    sqlalchemy_update(cls.model)
                    .filter_by(**filter_by)
                    .values(**values)
                    .execution_options(synchronize_session="fetch")
                )
                result = await session.execute(query)
                return result.rowcount

    @classmethod
    async def delete(cls, **filter_by):
        if not filter_by:
            raise ValueError("Provide at least one filter for deletion")
        async with async_session_maker() as session:
            async with session.begin():
                query = sqlalchemy_delete(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                return result.rowcount
