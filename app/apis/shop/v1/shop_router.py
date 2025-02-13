from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from app.dtos.shop.shop_creation_response import ShopCreationResponse
from app.services.shop_service import ShopCreationRequest, create_shop

router = APIRouter(prefix="/v1/shops", tags=["Shop"], redirect_slashes=False)


@router.post(
    "",
    description="shop 을 생성합니다.",
    response_class=ORJSONResponse,
)
async def api_create_shop(shop_creation_request: ShopCreationRequest) -> ShopCreationResponse:
    shop = await create_shop(shop_creation_request)
    return ShopCreationResponse(id=str(shop.id))
