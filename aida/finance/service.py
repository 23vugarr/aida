from fastapi import APIRouter, status
from aida.finance.schemas import ReponseModel, QueryRequest, TransactionResponse, TransactionCreate
from aida.finance.models import Transaction
from fastapi import HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from aida.config import get_db

router = APIRouter(
    prefix="/bank"
)


@router.get("/health")
def health_check():
    return ReponseModel(
        status=status.HTTP_200_OK,
        data={}
    )

@router.post("/transactions/", response_model=TransactionResponse, status_code=201)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = Transaction(type=transaction.type, amount=transaction.amount)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.get("/transactions/", response_model=List[TransactionResponse])
def get_all_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    return transactions

@router.post("/transactions/query/", response_model=List[TransactionResponse])
def run_custom_query(query_request: QueryRequest, db: Session = Depends(get_db)):
    try:
        result = db.execute(text(query_request.query))
        transactions = result.fetchall()

        response = []
        for row in transactions:
            print(row)
            print(type(row))
            print(row[0])
            transaction = TransactionResponse(
                id=row[0],
                type=row[1],
                amount=row[2],
                timestamp=row[3]
            )
            response.append(transaction)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid query: {str(e)}")
