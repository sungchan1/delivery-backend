from bson import ObjectId
from fastapi import status
from httpx import AsyncClient

from app.entities.category.category_codes import CategoryCode
from app.entities.collections import ShopCollection
from app.main import app


async def test_api_create_shop() -> None:
    # Given
    coordinates = [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]
    request_body = {
        "name": "test_name",
        "category_codes": [CategoryCode.CHICKEN.value],
        "delivery_areas": [{"type": "Polygon", "coordinates": coordinates}],
    }

    # When
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/shops",
            json=request_body,
        )

    # Then
    assert response.status_code == status.HTTP_200_OK
    shop = await ShopCollection._collection.find_one({"_id": ObjectId(response.json()["id"])})
    assert shop is not None
    assert shop["category_codes"] == request_body["category_codes"]
    assert len(shop["delivery_areas"]) == 1
    assert shop["delivery_areas"][0]["poly"]["coordinates"] == coordinates
