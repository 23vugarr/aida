from fastapi import FastAPI
from aida.finance.service import router as FinanceRouter

app = FastAPI()
app.include_router(
    FinanceRouter
)


@app.get("/test")
def test_func():
    return {
        "test": "test"
    }
