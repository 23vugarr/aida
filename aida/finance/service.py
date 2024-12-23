from fastapi import APIRouter, status
from aida.finance.schemas import ReponseModel


router = APIRouter(
    prefix="/bank"
)


@router.get("/health")
def health_check():
    return ReponseModel(
        status=status.HTTP_200_OK,
        data={}
    )
