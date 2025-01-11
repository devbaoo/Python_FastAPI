from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:Khacbao0712@localhost:5432/postgres'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
try:
    connection = engine.connect()
    print("Database connected successfully!")
except Exception as e:
    print("Error connecting to the database:", e)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
