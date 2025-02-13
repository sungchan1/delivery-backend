import asyncio
from logging import getLogger

from pymongo.errors import PyMongoError
from redis.exceptions import RedisError

from app.entities.category.category_codes import CategoryCode
from app.entities.collections import CategoryPointCollection, ShopCollection
from app.entities.collections.geo_json import GeoJsonPoint
from app.entities.redis_repositories.category_point_redis_repository import (
    CategoryPointRedisRepository,
)

logger = getLogger(__name__)


class CategoryPointCache:
    def __init__(self, longitude: float, latitude: float):
        self.longitude = longitude
        self.latitude = latitude
        self.cache_key = f"{longitude}_{latitude}"
        self.point = GeoJsonPoint(coordinates=[self.longitude, self.latitude])

    async def get_codes(self) -> tuple[CategoryCode, ...]:
        if cached := await CategoryPointRedisRepository.get(self.cache_key):
            return cached

        codes = await self._get_codes()
        await self._set_cache(codes)
        return codes

    async def _get_codes(self) -> tuple[CategoryCode, ...]:
        li = [ShopCollection.exists_by_category_and_point_intersects(code, self.point) for code in CategoryCode]
        return tuple(code for code, exists in zip(CategoryCode, await asyncio.gather(*li)) if exists)

    async def _set_cache(self, codes: tuple[CategoryCode, ...]) -> None:
        try:
            await CategoryPointCollection.insert_or_replace(self.cache_key, self.point, codes)
            await CategoryPointRedisRepository.set(self.cache_key, codes)

        except PyMongoError:
            logger.error(
                f"Failed to insert or replace category point cache to mongodb: {self.cache_key}", exc_info=True
            )
        except RedisError:
            logger.error(f"Failed to insert or replace category point cache to redis: {self.cache_key}", exc_info=True)
