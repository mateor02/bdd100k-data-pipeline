from enum import Enum
from pydantic import BaseModel


class TrafficLightColor(Enum):
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    NONE = "none"


class Category(Enum):
    CAR = "car"
    TRUCK = "truck"
    BUS = "bus"
    PERSON = "person"
    RIDER = "rider"
    BICYCLE = "bicycle"
    BIKE = "bike"
    MOTORCYCLE = "motorcycle"
    MOTOR = "motor"
    TRAFFIC_LIGHT = "traffic light"
    TRAFFIC_SIGN = "traffic sign"
    TRAIN = "train"


class Object(BaseModel):
    name: str
    category: Category
    id: int
    occluded: bool
    truncated: bool
    trafficLightColor: TrafficLightColor
    x1: float
    y1: float
    x2: float
    y2: float
