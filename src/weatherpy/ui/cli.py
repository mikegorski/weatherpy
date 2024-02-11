from typing import Literal, Optional, Union

import cyclopts

from weatherpy.api.comm import get_current_weather
from weatherpy.api.exceptions import BadRequest
from weatherpy.ui.config import create_cfg_file, handle_config

app = cyclopts.App(help="Weather forecast in your command line.")


@app.default
def wthr(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    units: Optional[Union[str, Literal["metric", "imperial", "standard"]]] = None,
):
    """Shows the current weather parameters based on default settings from the
    configuration file (if no arguments are provided).
    Settings can be optionally overridden using arguments provided to this command.
    If configuration file is not found, user is first led by the program through configuration step."""
    config = handle_config()
    if not lat:
        lat = float(config["HOME"]["lat"])
    if not lon:
        lon = float(config["HOME"]["lon"])
    if not units:
        units = config["SETTINGS"]["units"]
    api_token = config["SETTINGS"]["token"]
    print("Current weather:")
    try:
        curr = get_current_weather(lat=lat, lon=lon, units=units, token=api_token)
    except BadRequest as exc:
        print(exc)
        return
    print(curr)


@app.command
def config():
    """Lets user modify the configuration file."""
    _ = create_cfg_file()


@app.command
def latest():
    """Shows weather forecast at location and in units based on the latest request."""
    ...
