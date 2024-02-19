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
    description: list[tuple[str, str]]
    temp: float
    temp_feel: float
    pressure: int
    humidity: int
    wind_spd: float
    wind_deg: int


class Forecast:
    def __init__(self, loc: Geolocation, weathers: list[tuple[datetime, Weather]]):
        self.loc = loc
        self.weathers = weathers

    def __str__(self):
        s = f"Location: {self.loc}\n"
        for dt, weather in self.weathers:
            s += f"Time: {dt}\n"
            s += f"Weather:\n{weather}\n"
        return s


class Current:
    def __init__(self, dt: datetime, sunrise: datetime, sunset: datetime, loc: Geolocation, weather: Weather):
        self.dt = dt
        self.sunrise = sunrise
        self.sunset = sunset
        self.loc = loc
        self.weather = weather

    def __str__(self):
        return f"Location: {self.loc}\nWeather: {self.weather}"
