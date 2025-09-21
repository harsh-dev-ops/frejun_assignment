from app.conf.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DB_URI = settings.SQLALCHEMY_DATABASE_URL
engine = create_engine(DB_URI, pool_pre_ping=True, pool_size=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

