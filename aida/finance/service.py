from fastapi import APIRouter, status
from aida.finance.schemas import ReponseModel, QueryRequest, TransactionResponse, TransactionCreate
from aida.finance.models import Transaction
from fastapi import HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from aida.config import get_db
from aida.config import groq_client


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
    transaction = db.query(Transaction).filter(Transaction.tr_id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.get("/transactions/", response_model=List[TransactionResponse])
def get_all_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    return transactions

@router.post("/transactions/query/")
def run_custom_query(query_request: QueryRequest, db: Session = Depends(get_db)):
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""Based on this model of the database, write me the correct SQL query in SQL format to get all transactions where {query_request.query}. Example model is:

class Transaction(Base):
    __tablename__ = "transactions"

    tr_id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

Return only the SQL code without any explanation.
""",
                }
            ],
            model="llama3-8b-8192",
        )


        sql_query = chat_completion.choices[0].message.content.strip().replace("```", "")
        print(sql_query)

        result = db.execute(text(sql_query))
        print(result)
        transactions = result.fetchall()


        response = [list(row) for row in transactions]

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {str(e)}")
