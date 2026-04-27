from enum import Enum
from pydantic import BaseModel


class TimeOfDay(Enum):
    DAYTIME = "daytime"
    NIGHT = "night"
    DAWN_DUSK = "dawn/dusk"


class Weather(Enum):
    SNOWY = "snowy"
    PARTLY_CLOUDY = "partly cloudy"
    CLEAR = "clear"
    OVERCAST = "overcast"
    RAINY = "rainy"
    FOGGY = "foggy"


class Scene(Enum):
    RESIDENTIAL = "residential"
    PARKING_LOT = "parking lot"
    HIGHWAY = "highway"
    CITY_STREET = "city street"
    GAS_STATIONS = "gas stations"
    TUNNEL = "tunnel"


class Clip(BaseModel):
    name: str
    weather: Weather
    scene: Scene
    timeofday: TimeOfDay
