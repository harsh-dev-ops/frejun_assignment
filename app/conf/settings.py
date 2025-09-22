from typing import List
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from sqlalchemy import URL

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = Field(
        default=os.getenv("SECRET_KEY", "fallback-secret-key"),
    )
    
    ENV: str = Field(
        default=os.getenv("ENV", "development"),
    )
    
    DEBUG: bool = Field(
        default=os.getenv("DEBUG", "False").lower() == "true",
    )
    
    POSTGRES_DB: str = Field(
        default=os.getenv("POSTGRES_DB", "railway_db"),
    )
    
    POSTGRES_USER: str = Field(
        default=os.getenv("POSTGRES_USER", "user"),
    )
    
    POSTGRES_PASSWORD: str = Field(
        default=os.getenv("POSTGRES_PASSWORD", "password"),
    )
    
    POSTGRES_HOST: str = Field(
        default=os.getenv("POSTGRES_HOST", "localhost"),
    )
    
    POSTGRES_PORT: int = Field(
        default=int(os.getenv("POSTGRES_PORT", "5432")),
    )
    
    CLIENT_ORIGIN: str = Field(
        default=os.getenv("CLIENT_ORIGIN", "http://localhost:3000"),
    )
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        origins = os.getenv("ALLOWED_ORIGINS", self.CLIENT_ORIGIN)
        return [origin.strip() for origin in origins.split(",")]
    
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        )


settings = Settings()