from dataclasses import dataclass
from datetime import datetime


@dataclass
class Geolocation:
    """
    Geolocation dataclass representing a geographical location.

    Args:
        name (str): The name of the location.
        country (str): The country of the location.
        state (str): The state of the location.
        lat (float): The latitude of the location.
        lon (float): The longitude of the location.

    Returns:
        str: A string representation of the geolocation."""

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
    """
    Weather dataclass representing weather information.

    Args:
        description (list[tuple[str, str]]): The description of the weather.
        temp (float): The temperature.
        temp_feel (float): The perceived temperature.
        pressure (int): The atmospheric pressure.
        humidity (int): The humidity.
        wind_spd (float): The wind speed.
        wind_deg (int): The wind direction in degrees."""

    description: list[tuple[str, str]]
    temp: float
    temp_feel: float
    pressure: int
    humidity: int
    wind_spd: float
    wind_deg: int


class Forecast:
    """
    Forecast class representing a weather forecast.

    Args:
        loc (Geolocation): The geolocation of the forecast.
        weathers (list[tuple[datetime, Weather]]): The list of weather data for different times.
    """

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
    """
    Current class representing current weather information.

    Args:
        dt (datetime): The current date and time.
        sunrise (datetime): The time of sunrise.
        sunset (datetime): The time of sunset.
        loc (Geolocation): The geolocation of the current weather.
        weather (Weather): The weather information.
    """

    def __init__(self, dt: datetime, sunrise: datetime, sunset: datetime, loc: Geolocation, weather: Weather):
        self.dt = dt
        self.sunrise = sunrise
        self.sunset = sunset
        self.loc = loc
        self.weather = weather

    def __str__(self):
        return f"Location: {self.loc}\nWeather: {self.weather}"
