# app/database.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

DATABASE_URL = "postgresql+psycopg2://vfarmadmin:admin123@localhost:5432/userdb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
