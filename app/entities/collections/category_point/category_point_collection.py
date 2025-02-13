from dataclasses import asdict

import pymongo
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.results import DeleteResult

from app.entities.category.category_codes import CategoryCode
from app.entities.collections.category_point.category_point_document import (
    CategoryPointDocument,
)
from app.entities.collections.geo_json import GeoJsonPoint, GeoJsonPolygon
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

    @classmethod
    async def delete_by_id(cls, _id: ObjectId) -> int:
        result: DeleteResult = await cls._collection.delete_one({"_id": _id})
        return result.deleted_count

    @classmethod
    async def get_all_within_polygon_and_code_ne(
        cls, polygon: GeoJsonPolygon, code: CategoryCode
    ) -> tuple[CategoryPointDocument, ...]:
        return tuple(
            CategoryPointDocument(
                cache_key=result["cache_key"],
                codes=tuple(CategoryCode(code) for code in result["codes"]),
                point=GeoJsonPoint(coordinates=result["point"]["coordinates"]),
                _id=result["_id"],
            )
            for result in await cls._collection.find(
                {"point": {"$geoWithin": {"$geometry": asdict(polygon)}}, "codes": {"$ne": code.value}}
            ).to_list(length=None)
        )
