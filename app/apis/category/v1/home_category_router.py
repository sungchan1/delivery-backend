from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from app.dtos.category.category_response import CategoryResponse
from app.dtos.category.coordinates_request import CoordinatesRequest
from app.services.category_service import get_distinct_home_categories

router = APIRouter(prefix="/v1/home_categories", tags=["Home Category"], redirect_slashes=False)


@router.get(
    "/distinct",
    description="distinct 쿼리를 날려서 카테고리 목록을 구합니다.",
    response_class=ORJSONResponse,
)
async def api_get_categories_distinct(coordinates: Annotated[CoordinatesRequest, Depends()]) -> CategoryResponse:
    return CategoryResponse(categories=await get_distinct_home_categories(coordinates.longitude, coordinates.latitude))
