from app.entities.category.category_codes import CategoryCode
from app.entities.collections.category_point.category_point_collection import (
    CategoryPointCollection,
)
from app.entities.collections.geo_json import GeoJsonPoint


async def test_insert_or_replace() -> None:
    # Given
    cache_key = "1_1"
    point = GeoJsonPoint(coordinates=[1, 1])
    codes = (CategoryCode.CHICKEN, CategoryCode.PIZZA)

    # When
    category_point = await CategoryPointCollection.insert_or_replace(cache_key, point, codes)
    category_point_upserted = await CategoryPointCollection.insert_or_replace(cache_key, point, codes)

    # Then
    result = await CategoryPointCollection._collection.find_one({"_id": category_point.id})
    assert category_point.cache_key == result["cache_key"]
    assert category_point.point.coordinates == result["point"]["coordinates"]
    assert category_point.codes == tuple(CategoryCode(code) for code in result["codes"])
    assert category_point_upserted.cache_key == result["cache_key"]
    assert category_point_upserted.point.coordinates == result["point"]["coordinates"]
    assert category_point_upserted.codes == tuple(CategoryCode(code) for code in result["codes"])
