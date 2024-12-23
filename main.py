from aida.finance.service import router as FinanceRouter
from fastapi import FastAPI



app = FastAPI()
app.include_router(
    FinanceRouter, tags=["finance"]
)


@app.get("/test")
def test_func():
    return {
        "test": "test"
    }
