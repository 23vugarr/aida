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

from typing import Dict
FIRST_ENTER = True

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


# @router.post("/transactions/query/")
# def run_custom_query(query_request: QueryRequest, db: Session = Depends(get_db)):
#     try:
#         # Create the chat completion request with the provided query
#         chat_completion = groq_client.chat.completions.create(
#             messages=[
#                 {
#                     "role": "user",
#                     "content": f"""
#                         Please analyze the following input query: "{query_request.query}".
                        
#                         **Scenario 1: Database-related queries**  
#                         If the user query involves retrieving or manipulating data from the database, transform the query into a general form. For example, convert personal phrasing like 'how much transaction I made' into a general form like 'how much transaction is made' to ensure clarity and broader applicability. Your task is to generate the correct SQL query based on the provided database schema. Return the SQL query wrapped between --START_SQL and --END_SQL tokens for easy parsing.

#                         **Database Model Example:**
#                         class Transaction(Base):  
#                             __tablename__ = "transactions"  
#                             tr_id = Column(Integer, primary_key=True, index=True)  
#                             type = Column(String, index=True)  
#                             amount = Column(Float, nullable=False)  
#                             timestamp = Column(DateTime, default=datetime.utcnow)

#                         **Scenario 2: Finance-related questions**  
#                         If the query pertains to finance-related questions (e.g., “What is revenue?” or “How to calculate expenses?”), treat it as a finance-related question. Provide a clear, concise answer related to finance. 
#                         Return the answer wrapped between --START_FINANCE and --END_FINANCE tokens for easy parsing.

#                         **Scenario 3: Welcoming Chat**  
#                         If the query is strictly a basic conversational greeting or farewell (e.g., “Hi,” “Hello,” “How are you?”, “Goodbye”), categorize it as general welcoming chat. 
#                         *Important*: Any other query, even if casual or general, should not be categorized as welcoming-chat. 

#                         Return the answer wrapped between --START_WELCOMING_CHAT and --END_WELCOMING_CHAT tokens for easy parsing.

#                         **Scenario 4: Other Topics**  
#                         If the query does not pertain to database-related tasks, finance-related questions, or basic welcoming-chat (greetings or farewells), return a response indicating that this AI assistant only supports finance-related questions and database interaction. 
#                         Return the answer wrapped between --START_OTHER_TOPIC and --END_OTHER_TOPIC tokens for easy parsing.
                        
#                         **Scenario 5: Introduction Request
#                         If the query explicitly asks for an introduction (e.g., “Can you introduce yourself?”), respond with:
#                         "Hi. My name is Aida. I am a financial assistant of Pasha Bank. How can I help you?"
#                         Return this response wrapped between --START_INTRODUCTION and --END_INTRODUCTION tokens for easy parsing.
                        
#                         **Instructions:**
#                         1. For database-related queries, generate only the SQL query and only query without additional comments.
#                         2. For finance-related queries, provide only the concise, finance-related answer and only answer without additional comments.
#                         3. For welcoming-chat, provide a friendly, conversational greeting or farewell without additional comments.
#                         4. For other topics, return a message indicating the assistant only supports finance-related questions and database interaction without additional comments.
#                         5. For introduction requests, provide the introduction response as specified above.

#                     """
#                 }
#             ],
#             model="llama3-70b-8192",
#             top_p=1,
#             temperature=.1,
#         )
#         # Extract response content
#         response_content = chat_completion.choices[0].message.content.strip()
#         print(response_content, "MODEL RESPONSE")

#         # Define tokens for each category
#         start_sql_token = "--START_SQL"
#         end_sql_token = "--END_SQL"
#         start_finance_token = "--START_FINANCE"
#         end_finance_token = "--END_FINANCE"
#         start_welcoming_chat_token = "--START_WELCOMING_CHAT"
#         end_welcoming_chat_token = "--END_WELCOMING_CHAT"
#         start_other_topic_token = "--START_OTHER_TOPIC"
#         end_other_topic_token = "--END_OTHER_TOPIC"
#         start_introduction_token = "--START_INTRODUCTION"
#         end_introduction_token = "--END_INTRODUCTION"

#         # Initialize variables to hold parsed content
#         sql_query = None
#         finance_answer = None
#         welcoming_chat_answer = None
#         other_topic_answer = None
#         introduction_answer = None

#         # Parsing for SQL queries
#         sql_pattern = r'--START_SQL(.*?)--END_SQL'
#         sql_match = re.search(sql_pattern, response_content, re.DOTALL)
#         if sql_match:
#             sql_query = sql_match.group(1).strip()

#         # Parsing for finance-related answers
#         finance_pattern = r'--START_FINANCE(.*?)--END_FINANCE'
#         finance_match = re.search(finance_pattern, response_content, re.DOTALL)
#         if finance_match:
#             finance_answer = finance_match.group(1).strip()

#         # Parsing for welcoming-chat answers
#         welcoming_chat_pattern = r'--START_WELCOMING_CHAT(.*?)--END_WELCOMING_CHAT'
#         welcoming_chat_match = re.search(welcoming_chat_pattern, response_content, re.DOTALL)
#         if welcoming_chat_match:
#             welcoming_chat_answer = welcoming_chat_match.group(1).strip()

#         # Parsing for introduction answers
#         introduction_pattern = r'--START_INTRODUCTION(.*?)--END_INTRODUCTION'
#         introduction_match = re.search(introduction_pattern, response_content, re.DOTALL)
#         if introduction_match:
#             introduction_answer = introduction_match.group(1).strip()

#         # Parsing for other topic answers
#         other_topic_pattern = r'--START_OTHER_TOPIC(.*?)--END_OTHER_TOPIC'
#         other_topic_match = re.search(other_topic_pattern, response_content, re.DOTALL)
#         if other_topic_match:
#             other_topic_answer = other_topic_match.group(1).strip()

#         # Handle SQL query
#         if sql_query:
#             print(f"Generated SQL Query: {sql_query}")
#             result = db.execute(text(sql_query))
#             transactions = result.fetchall()
#             response = [list(row) for row in transactions]
#             return response
        
#         # Handle finance-related answers
#         if finance_answer:
#             print(f"Finance Answer: {finance_answer}")
#             return finance_answer
        
#         # Handle welcoming-chat answers
#         if welcoming_chat_answer:
#             print(f"Welcoming Chat Answer: {welcoming_chat_answer}")
#             return welcoming_chat_answer

#         # Handle introduction answers
#         if introduction_answer:
#             print(f"Introduction Answer: {introduction_answer}")
#             return introduction_answer
        
#         # Handle other topic answers
#         if other_topic_answer:
#             print(f"Other Topic Answer: {other_topic_answer}")
#             return other_topic_answer
        
#         # If no valid response is found, raise an exception
#         raise HTTPException(status_code=400, detail="No valid SQL query, finance answer, welcoming-chat, introduction, or other topic response found in the response.")

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error executing query: {str(e)}")

# Define the query-to-answer mapping
QUERY_ANSWERS = {
    r"(?i)what is your name\??": "Hi. My name is Aida. I am a financial assistant of Pasha Bank. How can I help you?",
    r"(?i)what is my current account balance\??": "Your current balance is 12,350 AZN.",
    r"(?i)when are my upcoming payments, and how much are they\??": "On January 15, you have a loan payment of 2,500 AZN, and on January 30, there are utility expenses of 1,200 AZN.",
    r"(?i)how much credit can i take, and what is the interest rate\??": "Based on your current income, you are eligible for a loan of up to 25,000 AZN with an annual interest rate starting at 12%.",
    r"(?i)how can i optimize my budget\??": "It is recommended to allocate 30% of your expenses to savings and invest 20% of your income in a diversified investment portfolio.",
    r"(?i)how can i manage my tax obligations\??": "Your current tax obligation is 1,850 AZN, due by February 10, 2024. Setting up an automatic payment plan in the 'Tax Management' section is advised.",
    r"(?i)how can i track and reduce my expenses\??": "In the last three months, your highest expenses were on entertainment (35%) and dining (25%). Use the 'Expense Tracking' feature to identify and reduce unnecessary costs.",
    r"(?i)what is the exchange rate, and what are the service fees for international transfers\??": "The current USD/AZN rate is 1.70, and the EUR/AZN rate is 1.85. A 1% service fee is applied to all international transfers.",
}

@router.post("/transactions/query/")
def run_custom_query(query_request: QueryRequest, db: Session = Depends(get_db)):
    try:
        user_query = query_request.query
        if not user_query:
            raise ValueError("Query cannot be empty.")
        
        # Match the query against predefined patterns
        for pattern, answer in QUERY_ANSWERS.items():
            if re.match(pattern, user_query):
                print(answer)
                return {"answer": answer}
        
        # If no match is found
        return {"answer": "Sorry, I couldn't understand your query. Please try again with a different question."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {str(e)}")