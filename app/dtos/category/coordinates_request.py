import dataclasses
from typing import Annotated

from fastapi import Query


@dataclasses.dataclass
class CoordinatesRequest:
    longitude: Annotated[
        float,
        Query(..., example=127.00592, gt=124, lt=132),
    ]
    latitude: Annotated[
        float,
        Query(..., example=37.49006, gt=33, lt=39),
    ]

    def __post_init__(self) -> None:
        self.longitude = round(self.longitude, 5)
        self.latitude = round(self.latitude, 5)
