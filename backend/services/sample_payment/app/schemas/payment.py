
from typing import Literal

from pydantic import BaseModel, Field


class PaymentRequest(BaseModel):
    order_id: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    simulation: Literal["success", "failure", "timeout"] = "success"


class PaymentResponse(BaseModel):
    payment_id: str
    order_id: str
    amount: float
    status: str
    message: str
