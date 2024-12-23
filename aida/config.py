from fastapi import FastAPI
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from groq import Groq

DATABASE_URL = "sqlite:///./transactions.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # Needed for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

groq_client = Groq(
    api_key="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",
)
