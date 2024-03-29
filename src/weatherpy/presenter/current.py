from rich import print
from rich.panel import Panel

from weatherpy.api.models import Current

from .symbols import API_ICON_TO_EMOJI
from .utils import UNIT_MAP, get_wind_direction


def create_location_and_time_panel(weather_data: Current) -> Panel:
    loc_txt: str = f":globe_with_meridians: {weather_data.loc} "
    date = weather_data.dt.strftime("%b %d, %Y")
    time = weather_data.dt.strftime("%H:%M")
    dt_txt: str = f":calendar: {date} :clock10: {time}\n\n"
    sun_txt: str = (
        f":sunrise: {weather_data.sunrise.strftime('%H:%M')} " f":sunset: {weather_data.sunset.strftime('%H:%M')}"
    )
    txt = loc_txt + dt_txt + sun_txt
    return Panel(
        renderable=txt,
        title="[b]Location & Time[/b]",
        expand=False,
        padding=(1, 3),
    )


def create_current_weather_panel(weather_data: Current, units: str) -> Panel:
    weather_txt: str = (
        " ".join(f"{API_ICON_TO_EMOJI[icon]} {desc.title()}" for desc, icon in weather_data.weather.description) + "\n"
    )
    weather_txt += f":thermometer: {weather_data.weather.temp:+.1f}{UNIT_MAP[units]['temp']}"
    weather_txt += f", feels like {weather_data.weather.temp_feel:+.1f}{UNIT_MAP[units]['temp']}\n"

    wind_speed = weather_data.weather.wind_spd
    wind_dir = get_wind_direction(weather_data.weather.wind_deg).value
    if units == "metric":
        wind_speed *= 3.6
    wind_speed = int(wind_speed)
    weather_txt += f":dash: {wind_speed} {UNIT_MAP[units]['wind']} {wind_dir}"
    weather_txt += "\n"
    weather_txt += f"{weather_data.weather.pressure} hPa, :sweat_drops: {weather_data.weather.humidity}%"

    if rain := weather_data.weather.rain:
        weather_txt += "\n"
        weather_txt += f":droplet: [b]{rain.get('1h', 0)} mm[/b] last hour"
    if snow := weather_data.weather.snow:
        weather_txt += "\n"
        weather_txt += f":snowflake: [b]{snow.get('1h', 0)} mm[/b] last hour"

    return Panel(
        renderable=weather_txt,
        title="[b]Current Weather Conditions[/b]",
        expand=False,
        padding=(1, 3),
    )


def show_current_weather(weather_data: Current, units: str) -> None:
    loc_panel = create_location_and_time_panel(weather_data)
    weather_panel = create_current_weather_panel(weather_data, units)
    print("\n")
    print(loc_panel)
    print(weather_panel)
