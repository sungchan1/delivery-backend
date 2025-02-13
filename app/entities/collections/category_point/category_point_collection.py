from dataclasses import asdict

import pymongo
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.entities.category.category_codes import CategoryCode
from app.entities.collections.category_point.category_point_document import (
    CategoryPointDocument,
)
from app.entities.collections.geo_json import GeoJsonPoint
from app.utils.mongo import db


class CategoryPointCollection:
    _collection = AsyncIOMotorCollection(db, "category_points")

    @classmethod
    async def set_index(cls) -> None:
        await cls._collection.create_index(
            [
                ("point", pymongo.GEOSPHERE),
                ("codes", pymongo.ASCENDING),
            ]
        )
        await cls._collection.create_index("cache_key", unique=True)

    @classmethod
    async def insert_or_replace(
        cls, cache_key: str, point: GeoJsonPoint, codes: tuple[CategoryCode, ...]
    ) -> CategoryPointDocument:
        documnet_to_insert = {
            "cache_key": cache_key,
            "codes": codes,
            "point": asdict(point),
        }
        try:
            result = await cls._collection.insert_one(documnet_to_insert)
            _id = result.inserted_id
        except DuplicateKeyError:
            inserted_document = await cls._collection.find_one_and_replace(
                {"cache_key": cache_key},
                documnet_to_insert,
                return_document=ReturnDocument.AFTER,
            )
            _id = inserted_document["_id"]

        return CategoryPointDocument(
            codes=codes,
            point=point,
            cache_key=cache_key,
            _id=_id,
        )
