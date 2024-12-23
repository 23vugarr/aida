from pydantic import BaseModel, Field
from typing import Optional
from typing import Dict, Any
from datetime import datetime


class ReponseModel(BaseModel):
    status: int
    data: Dict[str, Any]

class TransactionCreate(BaseModel):
    type: str = Field(..., example="deposit")
    amount: float = Field(..., gt=0, example=100.0)

class TransactionResponse(BaseModel):
    tr_id: int
    type: str
    amount: float
    timestamp: datetime

    class Config:
        orm_mode = True

class QueryRequest(BaseModel):
    query: str = Field(..., example="get transactions where amount is lower than average amount")
