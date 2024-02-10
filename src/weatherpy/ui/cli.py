import cyclopts
from typing import Optional, Literal

from weatherpy.ui.config import handle_config
from weatherpy.api.comm import get_current_weather
from weatherpy.api.exceptions import BadRequest

app = cyclopts.App(help="Weather forecast in your command line.")


@app.default
def wthr(
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        units: Literal['metric', 'imperial', 'standard'] = None
):
    """Shows the latest weather forecast based on default settings from the
    configuration file (if no arguments are provided).
    Settings can be optionally overridden using arguments provided to this command.
    """
    config = handle_config()
    if not lat:
        lat = config["HOME"]["lat"]
    if not lon:
        lon = config["HOME"]["lon"]
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
def latest():
    """Show weather forecast at location and in units based on your latest request."""
    ...
