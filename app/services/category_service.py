from app.entities.category.category_codes import CategoryCode
from app.entities.collections import ShopCollection
from app.entities.collections.geo_json import GeoJsonPoint


async def get_distinct_home_categories(longitude: float, latitude: float) -> tuple[CategoryCode, ...]:
    return tuple(
        code
        for code in await ShopCollection.get_distinct_category_codes_by_point_intersects(
            GeoJsonPoint(coordinates=[longitude, latitude])
        )
    )
