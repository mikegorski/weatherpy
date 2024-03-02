from datetime import datetime

import requests
from requests import Response
from requests.exceptions import ConnectionError, RequestException
from rich import print

from .exceptions import BadRequest
from .models import Current, Forecast, Geolocation, Weather
from .urls import (
    build_current_weather_url,
    build_direct_geocoding_url,
    build_forecast_weather_url,
    build_ip_url,
    build_reverse_geocoding_url,
)


def handle_request(url: str) -> Response:
    """Handles GET requests with possible errors."""
    try:
        resp = requests.get(url=url)
    except (RequestException, ConnectionError):
        print("[bold red]An error occurred. Please check your network connection and try again.[/]")
        exit(1)
    return resp


def get_ip_address() -> str:
    resp = handle_request(url=build_ip_url())
    return resp.text


def api_token_valid(token: str) -> bool:
    resp = handle_request(url=build_direct_geocoding_url(q="London", appid=token))
    return resp.status_code == 200


def get_locations_by_name(name: str, token: str) -> list[Geolocation]:
    resp = handle_request(url=build_direct_geocoding_url(q=name, limit=5, appid=token))
    if resp.status_code != 200:
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
    resp = handle_request(url=build_reverse_geocoding_url(lat=lat, lon=lon, limit=5, appid=token))
    if resp.status_code != 200:
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
    resp = handle_request(url=build_current_weather_url(lat=lat, lon=lon, units=units, limit=5, appid=token))
    data = resp.json()
    if resp.status_code != 200:
        raise BadRequest(code=data["cod"], message=data["message"])
    geolocation = Geolocation(
        name=data["name"], country=data["sys"]["country"], state="", lat=data["coord"]["lat"], lon=data["coord"]["lon"]
    )
    weather: Weather = Weather(
        description=[(x["description"], x["icon"]) for x in data["weather"]],
        temp=data["main"]["temp"],
        temp_feel=data["main"]["feels_like"],
        pressure=data["main"]["pressure"],
        humidity=data["main"]["humidity"],
        wind_spd=data["wind"]["speed"],
        wind_deg=data["wind"]["deg"],
    )
    return Current(
        dt=datetime.fromtimestamp(data["dt"]),
        sunrise=datetime.fromtimestamp(data["sys"]["sunrise"]),
        sunset=datetime.fromtimestamp(data["sys"]["sunset"]),
        loc=geolocation,
        weather=weather,
    )


def get_weather_forecast(lat: float, lon: float, units: str, token: str) -> Forecast:
    resp = handle_request(url=build_forecast_weather_url(lat=lat, lon=lon, units=units, limit=5, appid=token))
    data = resp.json()
    if resp.status_code != 200:
        raise BadRequest(code=data["cod"], message=data["message"])
    geolocation = Geolocation(
        name=data["city"]["name"],
        country=data["city"]["country"],
        state="",
        lat=data["city"]["coord"]["lat"],
        lon=data["city"]["coord"]["lon"],
    )
    forecasted: list[tuple[datetime, Weather]] = []
    for forecast in data["list"]:
        dt = datetime.fromtimestamp(forecast["dt"])
        params = forecast["main"]
        weather: Weather = Weather(
            description=[(x["description"], x["icon"]) for x in forecast["weather"]],
            temp=params["temp"],
            temp_feel=params["feels_like"],
            pressure=params["pressure"],
            humidity=params["humidity"],
            wind_spd=forecast["wind"]["speed"],
            wind_deg=forecast["wind"]["deg"],
        )
        forecasted.append((dt, weather))
    return Forecast(loc=geolocation, weathers=forecasted)
