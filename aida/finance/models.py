from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from aida.config import Base
from aida.config import engine


class Transaction(Base):
    __tablename__ = "transactions"

    tr_id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
