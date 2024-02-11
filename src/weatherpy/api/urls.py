from functools import partial
from typing import TypeAlias, Union

ApiURL: TypeAlias = str

DIRECT_GEOCODING: ApiURL = "https://api.openweathermap.org/geo/1.0/direct?"
REVERSE_GEOCODING: ApiURL = "https://api.openweathermap.org/geo/1.0/reverse?"
CURRENT_WEATHER: ApiURL = "https://api.openweathermap.org/data/2.5/weather?"
FORECAST_WEATHER: ApiURL = "https://api.openweathermap.org/data/2.5/forecast?"
IP: ApiURL = "https://api.ipify.org"


def build_url(base: ApiURL, **query_params: Union[str, float]) -> str:
    return base + "&".join([f"{k}={v}" for k, v in query_params.items()])


build_direct_geocoding_url = partial(build_url, base=DIRECT_GEOCODING)
build_reverse_geocoding_url = partial(build_url, base=REVERSE_GEOCODING)
build_current_weather_url = partial(build_url, base=CURRENT_WEATHER)
build_forecast_weather_url = partial(build_url, base=FORECAST_WEATHER)
build_ip_url = partial(build_url, base=IP)
