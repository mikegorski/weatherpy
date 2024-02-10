from dataclasses import dataclass
from datetime import datetime


@dataclass
class Geolocation:
    name: str
    country: str
    state: str
    lat: float
    lon: float

    def __str__(self):
        if self.state:
            joinable = [self.name, self.state, self.country, (self.lat, self.lon)]
        else:
            joinable = [self.name, self.country, (self.lat, self.lon)]
        return f"{', '.join(joinable[:-1])} {joinable[-1]}"


@dataclass
class Weather:
    description: list[str]
    temp: float
    temp_feel: float
    pressure: int
    humidity: int
    wind_spd: float
    wind_deg: int


class Forecast:
    def __init__(self, dt: datetime, loc: Geolocation, weathers: list[Weather]):
        self.dt = dt
        self.loc = loc
        self.weathers = weathers


class Current:
    def __init__(self, dt: datetime, sunrise: datetime, sunset: datetime, loc: Geolocation, weather: Weather):
        self.dt = dt
        self.sunrise = sunrise
        self.sunset = sunset
        self.loc = loc
        self.weather = weather

    def __str__(self):
        return f"Location: {self.loc}\nWeather: {self.weather}"
