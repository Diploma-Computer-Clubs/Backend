from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy import func, String
from src.shared.configurations.config import get_db_url
from datetime import datetime
from typing import Annotated

#Ссылка на БД
DATABASE_URL = get_db_url()

#Настройка аннотаций для колонок
int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=func.now)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]
str_password = Annotated[str, mapped_column(String(128), nullable=False)]

#Абстрактный класс для наследования моделей
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    #На основе имени класса создаст имя таблицы в нижнем регистре с "s" в конце
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    #Добавление колонок в каждую таблицу
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

#Создание движка с БД
engine = create_async_engine(DATABASE_URL)

#Создание сессии подключения к БД
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)