import requests
from datetime import datetime
from .exceptions import BadRequest
from .models import Geolocation, Forecast, Weather, Current
from .urls import (
    build_direct_geocoding_url,
    build_reverse_geocoding_url,
    build_current_weather_url,
    build_forecast_weather_url,
    build_ip_url
)


def get_ip_address() -> str:
    resp = requests.get(url=build_ip_url())
    return resp.text


def api_token_valid(token: str) -> bool:
    resp = requests.get(
        url=build_direct_geocoding_url(q="London", appid=token)
    )
    return resp.status_code == 200


def get_locations_by_name(name: str, token: str) -> list[Geolocation]:
    resp = requests.get(
        url=build_direct_geocoding_url(q=name, limit=5, appid=token)
    )
    if not resp.status_code == 200:
        return []
    locs: list[Geolocation] = []
    for loc in resp.json():
        if "state" not in loc:
            loc["state"] = ""
        locs.append(
            Geolocation(name=loc["name"], country=loc["country"], state=loc["state"], lat=loc["lat"], lon=loc["lon"])
        )
    return locs


def get_locations_by_coords(lat: float, lon: float, token: str) -> list[Geolocation]:
    resp = requests.get(
        url=build_reverse_geocoding_url(lat=lat, lon=lon, limit=5, appid=token)
    )
    if not resp.status_code == 200:
        return []
    locs: list[Geolocation] = []
    for loc in resp.json():
        if "state" not in loc:
            loc["state"] = ""
        locs.append(
            Geolocation(name=loc["name"], country=loc["country"], state=loc["state"], lat=loc["lat"], lon=loc["lon"])
        )
    return locs


def get_current_weather(lat: float, lon: float, units: str, token: str) -> Current:
    resp = requests.get(
        url=build_current_weather_url(lat=lat, lon=lon, units=units, limit=5, appid=token)
    )
    data = resp.json()
    if not resp.status_code == 200:
        raise BadRequest(code=data["cod"], message=data["message"])
    geolocation = Geolocation(
        name=data["name"],
        country=data["sys"]["country"],
        state="",
        lat=data["coord"]["lat"],
        lon=data["coord"]["lon"]
    )
    weather: Weather = Weather(
        description=[x["description"] for x in data["weather"]],
        temp=data["main"]["temp"],
        temp_feel=data["main"]["feels_like"],
        pressure=data["main"]["pressure"],
        humidity=data["main"]["humidity"],
        wind_spd=data["wind"]["speed"],
        wind_deg=data["wind"]["deg"]
    )
    return Current(
        dt=datetime.fromtimestamp(data["dt"]),
        sunrise=datetime.fromtimestamp(data["sys"]["sunrise"]),
        sunset=datetime.fromtimestamp(data["sys"]["sunset"]),
        loc=geolocation,
        weather=weather
    )
