from fastapi import APIRouter, status
from aida.finance.schemas import ReponseModel, QueryRequest, TransactionResponse, TransactionCreate
from aida.finance.models import Transaction
from fastapi import HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from aida.config import get_db
from aida.config import groq_client
import re

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
                        Please analyze the following input query: "{query_request.query}".
                        
                        **Scenario 1: Database-related queries**  
                        If the query pertains to retrieving or manipulating data from the database, classify it as database-related. Your task is to generate the correct SQL query based on the provided database schema. 
                        Return the SQL query wrapped between --START_SQL and --END_SQL tokens for easy parsing.

                        **Database Model Example:**
                        class Transaction(Base):  
                            __tablename__ = "transactions"  
                            tr_id = Column(Integer, primary_key=True, index=True)  
                            type = Column(String, index=True)  
                            amount = Column(Float, nullable=False)  
                            timestamp = Column(DateTime, default=datetime.utcnow)

                        **Scenario 2: General questions or chit-chat**  
                        If the query does not refer to database-related tasks (e.g., "What is water?" or "Who is Albert Einstein?"), treat it as a general question or conversation. Provide a concise, clear, and factual answer. 
                        Return the answer wrapped between --START_GENERAL and --END_GENERAL tokens for easy parsing. 

                        **Instructions:**
                        1. For database-related queries, generate only the SQL query.
                        2. For general questions, provide only the concise answer, with no extra explanations or comments.
                    """
                }
            ],
            model="llama3-8b-8192",
            top_p=1,
        )

        # Extract response content
        response_content = chat_completion.choices[0].message.content.strip()
        print(response_content, "MODEL RESPONSE")

        # Tokens for SQL and general questions
        start_sql_token = "--START_SQL"
        end_sql_token = "--END_SQL"
        start_general_token = "--START_GENERAL"
        end_general_token = "--END_GENERAL"

        # Initialize variables to hold parsed content
        sql_query = None
        general_answer = None

        # Improved parsing using regular expressions for SQL
        sql_pattern = r'--START_SQL(.*?)--END_SQL'
        sql_match = re.search(sql_pattern, response_content, re.DOTALL)
        if sql_match:
            sql_query = sql_match.group(1).strip()

        # Improved parsing using regular expressions for general answers
        general_pattern = r'--START_GENERAL(.*?)--END_GENERAL'
        general_match = re.search(general_pattern, response_content, re.DOTALL)
        if general_match:
            general_answer = general_match.group(1).strip()

        # Handle SQL query
        if sql_query:
            print(f"Generated SQL Query: {sql_query}")
            result = db.execute(text(sql_query))
            transactions = result.fetchall()
            response = [list(row) for row in transactions]
            return response
        
        # Handle general answers
        if general_answer:
            print(f"General Answer: {general_answer}")
            return general_answer
        
        # If no valid response is found, raise an exception
        raise HTTPException(status_code=400, detail="No valid SQL query or general answer found in the response.")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {str(e)}")