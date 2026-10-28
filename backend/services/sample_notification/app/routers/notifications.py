
from fastapi import APIRouter

from services.sample_notification.app.schemas.notification import (
    NotificationRequest,
    NotificationResponse,
)
from services.sample_notification.app.services.notification_service import (
    send_notification,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/send", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationRequest,
) -> NotificationResponse:
    return await send_notification(notification_data)
