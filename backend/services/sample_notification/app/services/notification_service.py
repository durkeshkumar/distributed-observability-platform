
import asyncio
import uuid

from fastapi import HTTPException

from services.sample_notification.app.schemas.notification import (
    NotificationRequest,
    NotificationResponse,
)


async def send_notification(
    notification_data: NotificationRequest,
) -> NotificationResponse:
    if notification_data.simulation == "timeout":
        await asyncio.sleep(15)

    if notification_data.simulation == "failure":
        raise HTTPException(
            status_code=502,
            detail="Simulated notification provider failure",
        )

    return NotificationResponse(
        notification_id=f"NOT-{uuid.uuid4().hex[:12].upper()}",
        order_id=notification_data.order_id,
        recipient=notification_data.recipient,
        channel=notification_data.channel,
        status="sent",
        message="Notification processed successfully",
    )
