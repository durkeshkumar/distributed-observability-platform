
from fastapi import APIRouter

from services.sample_order.app.schemas.order import (
    OrderRequest,
    OrderResponse,
)
from services.sample_order.app.services.order_service import create_order

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse)
async def submit_order(order_data: OrderRequest) -> OrderResponse:
    return await create_order(order_data)
