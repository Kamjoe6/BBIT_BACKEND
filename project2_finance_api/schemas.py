from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class TransactionCreate(BaseModel):
    title: str = Field(..., min_length=2, example="KPLC Tokens")
    amount: float = Field(..., gt=0, example=1500.0)
    transaction_type: Literal["income", "expense"] = Field(..., example="expense")
    category: str = Field(default="General", example="Utilities")

class TransactionResponse(TransactionCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
