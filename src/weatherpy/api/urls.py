from enum import Enum
from functools import partial
from typing import Any


class ApiURL(Enum):
    DIRECT_GEOCODING: str = "https://api.openweathermap.org/geo/1.0/direct?"
    REVERSE_GEOCODING: str = "https://api.openweathermap.org/geo/1.0/reverse?"
    CURRENT_WEATHER: str = "https://api.openweathermap.org/data/2.5/weather?"
    FORECAST_WEATHER: str = "https://api.openweathermap.org/data/2.5/forecast?"
    IP: str = "https://api.ipify.org"


def build_url(base: ApiURL, **query_params: dict[str, Any]) -> str:
    return base.value + '&'.join([f"{k}={v}" for k, v in query_params.items()])


build_direct_geocoding_url = partial(build_url, base=ApiURL.DIRECT_GEOCODING)
build_reverse_geocoding_url = partial(build_url, base=ApiURL.REVERSE_GEOCODING)
build_current_weather_url = partial(build_url, base=ApiURL.CURRENT_WEATHER)
build_forecast_weather_url = partial(build_url, base=ApiURL.FORECAST_WEATHER)
build_ip_url = partial(build_url, base=ApiURL.IP)
