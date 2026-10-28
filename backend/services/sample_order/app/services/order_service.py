
import asyncio
import uuid

import httpx
from fastapi import HTTPException

from services.sample_order.app.schemas.order import (
    OrderRequest,
    OrderResponse,
)

PAYMENT_SERVICE_URL = "http://127.0.0.1:8002"
NOTIFICATION_SERVICE_URL = "http://127.0.0.1:8003"
SERVICE_TIMEOUT_SECONDS = 5.0


async def create_order(order_data: OrderRequest) -> OrderResponse:
    order_id = f"ORD-{uuid.uuid4().hex[:10].upper()}"

    async with httpx.AsyncClient(
        timeout=SERVICE_TIMEOUT_SECONDS
    ) as client:
        # Step 1: Process payment.
        try:
            payment_response = await client.post(
                f"{PAYMENT_SERVICE_URL}/payments/process",
                json={
                    "order_id": order_id,
                    "amount": order_data.amount,
                    "simulation": order_data.payment_simulation,
                },
            )
            payment_response.raise_for_status()
            payment_data = payment_response.json()

        except httpx.TimeoutException as exc:
            raise HTTPException(
                status_code=504,
                detail={
                    "order_id": order_id,
                    "stage": "payment",
                    "error": "Payment service timed out",
                },
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail={
                    "order_id": order_id,
                    "stage": "payment",
                    "error": "Payment service returned an error",
                    "upstream_status": exc.response.status_code,
                },
            ) from exc

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail={
                    "order_id": order_id,
                    "stage": "payment",
                    "error": "Payment service is unavailable",
                },
            ) from exc

        # Step 2: Notify the customer after successful payment.
        try:
            notification_response = await client.post(
                f"{NOTIFICATION_SERVICE_URL}/notifications/send",
                json={
                    "order_id": order_id,
                    "recipient": order_data.recipient,
                    "channel": order_data.notification_channel,
                    "message": f"Your order {order_id} has been confirmed.",
                    "simulation": order_data.notification_simulation,
                },
            )
            notification_response.raise_for_status()
            notification_data = notification_response.json()

        except httpx.TimeoutException as exc:
            raise HTTPException(
                status_code=504,
                detail={
                    "order_id": order_id,
                    "stage": "notification",
                    "error": "Notification service timed out",
                    "payment_status": payment_data["status"],
                },
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail={
                    "order_id": order_id,
                    "stage": "notification",
                    "error": "Notification service returned an error",
                    "upstream_status": exc.response.status_code,
                    "payment_status": payment_data["status"],
                },
            ) from exc

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail={
                    "order_id": order_id,
                    "stage": "notification",
                    "error": "Notification service is unavailable",
                    "payment_status": payment_data["status"],
                },
            ) from exc

    return OrderResponse(
        order_id=order_id,
        customer_id=order_data.customer_id,
        amount=order_data.amount,
        status="completed",
        payment_status=payment_data["status"],
        notification_status=notification_data["status"],
        message="Order created, payment processed, and notification sent.",
    )
