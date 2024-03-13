from typing import Literal, Optional, Union

import cyclopts

from weatherpy.api.comm import get_current_weather, get_locations_by_name, get_weather_forecast
from weatherpy.api.exceptions import BadRequest
from weatherpy.presenter.current import show_current_weather
from weatherpy.presenter.forecast import show_forecast
from weatherpy.ui.config import create_cfg_file, display_config, handle_config

app = cyclopts.App(help="Weather forecast in your command line.")


@app.default
def wthr(
    city: Optional[list[str]] = None,
    coords: Optional[tuple[float, float]] = None,
    units: Optional[Union[str, Literal["metric", "imperial", "standard"]]] = None,
):
    """Shows the current weather parameters based on default settings from the
    configuration file (if no arguments are provided).
    Settings can be optionally overridden using arguments provided to this command.
    If configuration file is not found, user is first led by the program through configuration step."""
    config = handle_config()
    api_token = config["SETTINGS"]["token"]

    if city:
        locs = get_locations_by_name(name=" ".join(city).title(), token=api_token)
        if not locs:
            print(f"Location '{' '.join(city).title()}' couldn't be found.")
            return
        loc = locs[0]
        lat, lon = loc.lat, loc.lon

    elif not coords:
        lat = float(config["HOME"]["lat"])
        lon = float(config["HOME"]["lon"])
    else:
        lat, lon = coords

    if not units:
        units = config["SETTINGS"]["units"]

    try:
        curr = get_current_weather(lat=lat, lon=lon, units=units, token=api_token)
    except BadRequest as exc:
        print(exc)
        return
    show_current_weather(weather_data=curr, units=units)


@app.command
def config(display: Optional[bool] = False):
    """Lets user overwrite the configuration file or display it."""
    if display:
        display_config()
    else:
        _ = create_cfg_file()


@app.command
def forecast(
    city: Optional[list[str]] = None,
    coords: Optional[tuple[float, float]] = None,
    units: Optional[Union[str, Literal["metric", "imperial", "standard"]]] = None,
):
    """Shows weather forecast for the next 5 days in 3-hour intervals."""
    config = handle_config()
    api_token = config["SETTINGS"]["token"]

    if city:
        locs = get_locations_by_name(name=" ".join(city).title(), token=api_token)
        if not locs:
            print(f"Location '{' '.join(city).title()}' couldn't be found.")
            return
        loc = locs[0]
        lat, lon = loc.lat, loc.lon

    elif not coords:
        lat = float(config["HOME"]["lat"])
        lon = float(config["HOME"]["lon"])
    else:
        lat, lon = coords

    if not units:
        units = config["SETTINGS"]["units"]

    try:
        forecast = get_weather_forecast(lat=lat, lon=lon, units=units, token=api_token)
    except BadRequest as exc:
        print(exc)
        return
    show_forecast(forecast, units)
