
from typing import Literal

from pydantic import BaseModel, Field


class OrderRequest(BaseModel):
    customer_id: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    recipient: str = Field(min_length=1, max_length=255)
    notification_channel: Literal["email", "sms"] = "email"
    payment_simulation: Literal["success", "failure", "timeout"] = "success"
    notification_simulation: Literal["success", "failure", "timeout"] = "success"


class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    amount: float
    status: str
    payment_status: str
    notification_status: str
    message: str
