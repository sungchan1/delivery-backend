import asyncio
from abc import ABC, abstractmethod

from app.entities.collections.category_point.category_point_collection import (
    CategoryPointCollection,
)
from app.entities.collections.category_point.category_point_document import (
    CategoryPointDocument,
)
from app.entities.collections.shop.shop_document import ShopDocument
from app.entities.redis_repositories.category_point_redis_repository import (
    CategoryPointRedisRepository,
)


class CategoryPointCacheInvalidator(ABC):
    def __init__(self, shop: ShopDocument):
        self._shop = shop

    @abstractmethod
    async def invalidate(self) -> None:
        pass

    async def _delete_cache(self, point: CategoryPointDocument) -> None:
        """
        반드시 redis 에서 삭제가 성공한 후에 mongodb 에서 삭제해야 합니다.
        mongodb 에서 삭제된 후에 redis 삭제가 실패할 경우, redis 캐시를 다시 찾아서 삭제할 방법이 없기 때문입니다.
        """
        await CategoryPointRedisRepository.delete(point.cache_key)
        await CategoryPointCollection.delete_by_id(point.id)


class ShopCreationCategoryPointCacheInvalidator(CategoryPointCacheInvalidator):
    async def invalidate(self) -> None:
        list_of_point_tuple = await self._get_list_of_point_tuple()
        deleted = set()
        for tp in list_of_point_tuple:
            for point in tp:
                if point.id not in deleted:
                    await self._delete_cache(point)
                    deleted.add(point.id)

    async def _get_list_of_point_tuple(self) -> list[tuple[CategoryPointDocument, ...]]:
        # 함께 채우기
        return await asyncio.gather(
            *(
                CategoryPointCollection.get_all_within_polygon_and_code_ne(area.poly, code)
                for area in self._shop.delivery_areas
                for code in self._shop.category_codes
            )
        )
