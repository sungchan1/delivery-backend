import dataclasses
from typing import Sequence

from app.entities.category.categories import Category
from app.entities.category.category_codes import CategoryCode


@dataclasses.dataclass
class CategoryResponse:
    categories: Sequence[Category]
