from typing import List
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = Field(
        default=os.getenv("SECRET_KEY", "fallback-secret-key"),
        description="Secret key for encryption"
    )
    
    ENV: str = Field(
        default=os.getenv("ENV", "development"),
        description="Environment name"
    )
    
    DEBUG: bool = Field(
        default=os.getenv("DEBUG", "False").lower() == "true",
        description="Debug mode"
    )
    
    POSTGRES_DB: str = Field(
        default=os.getenv("POSTGRES_DB", "railway_db"),
        description="PostgreSQL database name"
    )
    
    POSTGRES_USER: str = Field(
        default=os.getenv("POSTGRES_USER", "user"),
        description="PostgreSQL username"
    )
    
    POSTGRES_PASSWORD: str = Field(
        default=os.getenv("POSTGRES_PASSWORD", "password"),
        description="PostgreSQL password"
    )
    
    POSTGRES_HOST: str = Field(
        default=os.getenv("POSTGRES_HOST", "localhost"),
        description="PostgreSQL host"
    )
    
    POSTGRES_PORT: int = Field(
        default=int(os.getenv("POSTGRES_PORT", "5432")),
        description="PostgreSQL port"
    )
    
    CLIENT_ORIGIN: str = Field(
        default=os.getenv("CLIENT_ORIGIN", "http://localhost:3000"),
        description="Client origin URL"
    )
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        origins = os.getenv("ALLOWED_ORIGINS", self.CLIENT_ORIGIN)
        return [origin.strip() for origin in origins.split(",")]
    
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB or "",
        )


settings = Settings()