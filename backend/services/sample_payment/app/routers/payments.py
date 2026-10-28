
from fastapi import APIRouter

from services.sample_payment.app.schemas.payment import (
    PaymentRequest,
    PaymentResponse,
)
from services.sample_payment.app.services.payment_service import (
    process_payment,
)

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/process", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentRequest,
) -> PaymentResponse:
    return await process_payment(payment_data)
