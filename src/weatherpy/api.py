from dataclasses import dataclass

import requests

GEOCODING_API_URL: str = "https://api.openweathermap.org/geo/1.0/direct?"
CURR_API_URL: str = "https://api.openweathermap.org/data/2.5/weather?"
FORECAST_API_URL: str = "https://api.openweathermap.org/data/2.5/forecast?"
IP_API_URL: str = "https://api.ipify.org"


@dataclass
class GeoApiLoc:
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


def get_ip_address() -> str:
    resp = requests.get(url=IP_API_URL)
    return resp.text


def api_token_valid(token: str) -> bool:
    resp = requests.get(url=f"{GEOCODING_API_URL}q=London&appid={token}")
    return resp.status_code == 200


def get_locations_by_name(name: str, token: str) -> list[GeoApiLoc]:
    resp = requests.get(url=f"{GEOCODING_API_URL}q={name}&limit=5&appid={token}")
    if not resp.status_code == 200:
        return []
    locs: list[GeoApiLoc] = []
    for loc in resp.json():
        if "state" not in loc:
            loc["state"] = ""
        locs.append(
            GeoApiLoc(name=loc["name"], country=loc["country"], state=loc["state"], lat=loc["lat"], lon=loc["lon"])
        )
    return locs
