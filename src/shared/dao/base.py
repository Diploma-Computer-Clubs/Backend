from sqlalchemy import select, insert, update as sqlalchemy_update, delete as sqlalchemy_delete, func, update
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
    async def find_all_unique(cls, *options, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by).options(*options)
            result = await session.execute(query)
            return result.scalars().unique().all()

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
    async def update_list(cls, data: list[dict]) -> int:
        if not data:
            return 0

        primary_key_columns = [column.key for column in cls.model.__mapper__.primary_key]
        if not primary_key_columns:
            raise ValueError(f"Model {cls.model.__name__} does not have a primary key")

        async with async_session_maker() as session:
            async with session.begin():
                updated_rows = 0

                for item in data:
                    missing_keys = [key for key in primary_key_columns if key not in item]
                    if missing_keys:
                        raise ValueError(
                            f"Each update item must include primary key fields: {', '.join(missing_keys)}"
                        )

                    filter_by = {key: item[key] for key in primary_key_columns}
                    values = {key: value for key, value in item.items() if key not in primary_key_columns}

                    if not values:
                        continue

                    query = (
                        sqlalchemy_update(cls.model)
                        .filter_by(**filter_by)
                        .values(**values)
                        .execution_options(synchronize_session=False)
                    )
                    result = await session.execute(query)
                    updated_rows += result.rowcount or 0

                return updated_rows

    @classmethod
    async def delete(cls, **filter_by):
        if not filter_by:
            raise ValueError("Provide at least one filter for deletion")
        async with async_session_maker() as session:
            async with session.begin():
                query = sqlalchemy_delete(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                return result.rowcount
