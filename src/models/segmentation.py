from enum import Enum
from pydantic import BaseModel


class Category(Enum):
    LANE_SINGLE_YELLOW = "lane/single yellow"
    LANE_DOUBLE_WHITE = "lane/double white"
    AREA_ALTERNATIVE = "area/alternative"
    AREA_DRIVABLE = "area/drivable"
    AREA_UNKNOWN = "area/unknown"
    LANE_SINGLE_OTHER = "lane/single other"
    LANE_ROAD_CURB = "lane/road curb"
    LANE_CROSSWALK = "lane/crosswalk"
    LANE_DOUBLE_OTHER = "lane/double other"
    LANE_SINGLE_WHITE = "lane/single white"
    LANE_DOUBLE_YELLOW = "lane/double yellow"


class Direction(Enum):
    PARALLEL = "parallel"
    VERTICAL = "vertical"


class Style(Enum):
    DASHED = "dashed"
    SOLID = "solid"


class Segmentation(BaseModel):
    name: str
    category: Category
    id: int
    direction: Direction | None = None
    style: Style | None = None
    poly2d: str
