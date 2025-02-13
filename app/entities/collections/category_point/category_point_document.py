import dataclasses

from app.entities.category.category_codes import CategoryCode
from app.entities.collections.base_document import BaseDocument
from app.entities.collections.geo_json import GeoJsonPoint


@dataclasses.dataclass
class CategoryPointDocument(BaseDocument):
    cache_key: str  # 위도 경도를 문자 포맷팅 해서 넣을 예정
    codes: tuple[CategoryCode, ...]
    point: GeoJsonPoint
