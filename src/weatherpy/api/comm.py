import requests
from .models import Geolocation
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
    ...
