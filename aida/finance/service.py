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
        # Create the chat completion request with the provided query
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""
                        Analyze the input query {query_request.query}:
                        If the query related to the database information retrieval, treat it as related to the provided database model and generate the correct SQL query to address it. Return the SQL query wrapped between --START_SQL and --END_SQL tokens for easy parsing.
                    
                    Example database model:
                        class Transaction(Base):  
                            __tablename__ = "transactions"  
                            tr_id = Column(Integer, primary_key=True, index=True)  
                            type = Column(String, index=True)  
                            amount = Column(Float, nullable=False)  
                            timestamp = Column(DateTime, default=datetime.utcnow) 

                    If the query does not contain the word database, treat it as a general question or user want to simply chat with you and provide a concise and accurate answer, wrapped between --START_GENERAL and --END_GENERAL tokens for easy parsing.
                    For general questions: Provide only the answer in plain text. Avoid any explanations, comments, or unnecessary output. For database-related queries, return the SQL query and only query without any explanation or comments.

                    """
                }
            ],
            model="llama3-8b-8192",
            # temperature=0.3,
            top_p=1,
        )   

        # Extract response content
        response_content = chat_completion.choices[0].message.content.strip()
        print(response_content, " FIRST OUT MODEL")
        # Tokens for SQL and general questions
        start_sql_token = "--START_SQL"
        end_sql_token = "--END_SQL"
        start_general_token = "--START_GENERAL"
        end_general_token = "--END_GENERAL"

        # Initialize variables to hold parsed content
        sql_query = None
        general_answer = None

        if start_sql_token in response_content and end_sql_token in response_content:
            print('DEBUG MODE SQL START')
            print(response_content.split(start_sql_token)[1])
            print('DEBUG MODE SQL END')

            sql_query = response_content.split(start_sql_token)[1].split(end_sql_token)[0].strip()

        if start_general_token in response_content and end_general_token in response_content:
            general_answer = response_content.split(start_general_token)[1].split(end_general_token)[0].strip()

        if sql_query:
            print('00000')
            print(sql_query, "SQL QUERY")
            result = db.execute(text(sql_query))
            transactions = result.fetchall()
            response = [list(row) for row in transactions]
            return response
        
        if general_answer:
            print('00000')
            print(general_answer, "GENERAL")
            return general_answer
        

        print(response_content,'RESPONSE CONTENT')

        raise HTTPException(status_code=400, detail="No SQL query or general answer found in the response.")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {str(e)}")
