import os
from pydantic_settings import BaseSettings, SettingsConfigDict

#Модель ссылки для подключения к БД
class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str
    #Для получения данных из .env
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".env")
    )


#Создание образа модели
settings = Settings()

#Создание ссылки подключения к БД
def get_db_url():
    return (f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

def get_auth_data():
    return {"secret_key": settings.SECRET_KEY, "algorithm": settings.ALGORITHM}