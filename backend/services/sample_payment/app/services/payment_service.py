
import asyncio
import uuid

from fastapi import HTTPException

from services.sample_payment.app.schemas.payment import (
    PaymentRequest,
    PaymentResponse,
)


async def process_payment(
    payment_data: PaymentRequest,
) -> PaymentResponse:
    if payment_data.simulation == "timeout":
        # Simulate a slow payment provider.
        await asyncio.sleep(15)

    if payment_data.simulation == "failure":
        raise HTTPException(
            status_code=502,
            detail="Simulated payment provider failure",
        )

    return PaymentResponse(
        payment_id=f"PAY-{uuid.uuid4().hex[:12].upper()}",
        order_id=payment_data.order_id,
        amount=payment_data.amount,
        status="completed",
        message="Payment processed successfully",
    )
