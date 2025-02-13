from bson import ObjectId
from fastapi import status
from httpx import AsyncClient

from app.entities.category.category_codes import CategoryCode
from app.entities.collections import ShopCollection
from app.entities.collections.geo_json import GeoJsonPolygon
from app.entities.collections.shop.shop_document import ShopDeliveryAreaSubDocument
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


async def test_api_delete_shop() -> None:
    # Given
    shop = await ShopCollection.insert_one(
        name="sandwich_pizza_shop",
        category_codes=[CategoryCode.SANDWICH, CategoryCode.PIZZA],
        delivery_areas=[
            ShopDeliveryAreaSubDocument(poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]))
        ],
    )
    # When
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/v1/shops/{shop.id}",
        )

    # Then
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await ShopCollection.find_by_id(shop.id) is None


async def test_api_delete_shop_when_delete_non_existing_shop_then_it_returns_400() -> None:
    # Given
    non_existing_shop_id = "64622be98d618c0d271a0238"

    # When
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/v1/shops/{non_existing_shop_id}",
        )

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_api_delete_shop_when_delete_invalid_shop_then_it_returns_422() -> None:
    # Given
    invalid_shop_id = "invalid_id"

    # When
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/v1/shops/{invalid_shop_id}",
        )

    # Then
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
