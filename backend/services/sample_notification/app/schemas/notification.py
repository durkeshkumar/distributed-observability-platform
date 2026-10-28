
from typing import Literal

from pydantic import BaseModel, Field


class NotificationRequest(BaseModel):
    order_id: str = Field(min_length=1, max_length=100)
    recipient: str = Field(min_length=1, max_length=255)
    channel: Literal["email", "sms"] = "email"
    message: str = Field(min_length=1, max_length=2000)
    simulation: Literal["success", "failure", "timeout"] = "success"


class NotificationResponse(BaseModel):
    notification_id: str
    order_id: str
    recipient: str
    channel: str
    status: str
    message: str
