from pydantic import BaseModel
from typing import Dict, Any


class ReponseModel(BaseModel):
    status: int
    data: Dict[str, Any]
