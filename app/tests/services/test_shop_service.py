from app.dtos.shop.shop_creation_request import ShopCreationRequest
from app.entities.caches.category_point.category_point_cache import CategoryPointCache
from app.entities.category.category_codes import CategoryCode
from app.entities.collections import ShopCollection
from app.entities.collections.category_point.category_point_collection import (
    CategoryPointCollection,
)
from app.entities.collections.geo_json import GeoJsonPoint, GeoJsonPolygon
from app.entities.collections.shop.shop_document import ShopDeliveryAreaSubDocument
from app.services.category_service import get_home_categories_cached
from app.services.shop_service import create_shop, delete_shop
from app.utils.redis_ import redis


async def test_create_shop_invalidates_point() -> None:
    # Given
    await ShopCollection.insert_one(
        name="sandwich_pizza_shop",
        category_codes=[CategoryCode.SANDWICH, CategoryCode.PIZZA],
        delivery_areas=[
            ShopDeliveryAreaSubDocument(poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]))
        ],
    )
    shop_creation_request = ShopCreationRequest(
        name="chicken_sandwich_shop",
        category_codes={CategoryCode.CHICKEN, CategoryCode.SANDWICH},
        delivery_areas=[GeoJsonPolygon(coordinates=[[[8, 0], [8, 14], [14, 14], [14, 0], [8, 0]]])],
    )
    not_be_removed1 = await CategoryPointCollection.insert_or_replace(
        "3_3",
        GeoJsonPoint(coordinates=[3, 3]),
        (
            CategoryCode.SANDWICH,
            CategoryCode.PIZZA,
        ),
    )
    to_be_removed = await CategoryPointCollection.insert_or_replace(
        "9_9",
        GeoJsonPoint(coordinates=[9, 9]),
        (
            CategoryCode.SANDWICH,
            CategoryCode.PIZZA,
        ),
    )
    not_be_removed2 = await CategoryPointCollection.insert_or_replace(
        "9.2_9.2",
        GeoJsonPoint(coordinates=[9.2, 9.2]),
        (
            CategoryCode.SANDWICH,
            CategoryCode.PIZZA,
            CategoryCode.CHICKEN,
        ),
    )

    # When
    shop = await create_shop(shop_creation_request)

    # Then
    result = await CategoryPointCollection._collection.find({}, {"_id": True}).to_list(None)

    assert len(result) == 2
    ids = [item["_id"] for item in result]
    assert not_be_removed1.id in ids
    assert not_be_removed2.id in ids

    result_shop = await ShopCollection._collection.find_one({"_id": shop.id})
    assert shop.name == result_shop["name"]

    async def test_one_shop_deleted_then_cache_should_be_deleted() -> None:
        # Given
        shop_to_be_removed = await ShopCollection.insert_one(
            name="sandwich_pizza_shop",
            category_codes=[CategoryCode.SANDWICH, CategoryCode.PIZZA],
            delivery_areas=[
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=[[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]])
                )
            ],
        )
        await ShopCollection.insert_one(
            name="sandwich_pizza_shop2",
            category_codes=[CategoryCode.SANDWICH, CategoryCode.PIZZA],
            delivery_areas=[
                ShopDeliveryAreaSubDocument(
                    poly=GeoJsonPolygon(coordinates=[[[5, 5], [5, 10], [10, 10], [10, 5], [5, 5]]])
                )
            ],
        )
        await get_home_categories_cached(3.0, 3.0)
        cache_key_to_be_removed = CategoryPointCache(3.0, 3.0).cache_key
        await get_home_categories_cached(9.0, 9.0)
        cache_key_not_to_be_removed = CategoryPointCache(9.0, 9.0).cache_key

        # When
        await delete_shop(shop_to_be_removed.id)

        # Then
        result = await CategoryPointCollection._collection.find({}).to_list(None)
        assert len(result) == 1
        assert result[0]["cache_key"] == cache_key_not_to_be_removed
        assert await redis.get(cache_key_to_be_removed) is None
        assert await redis.get(cache_key_not_to_be_removed) == "pizza,sandwich"
