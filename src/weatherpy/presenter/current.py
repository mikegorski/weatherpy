from rich import print
from rich.panel import Panel

from weatherpy.api.models import Current

from .symbols import API_ICON_TO_EMOJI, DEGREE, Wind


def get_wind_direction(deg: int) -> Wind:
    if 0 <= deg < 22.5:
        return Wind.N
    elif 22.5 <= deg < 67.5:
        return Wind.NE
    elif 67.5 <= deg < 112.5:
        return Wind.E
    elif 112.5 <= deg < 157.5:
        return Wind.SE
    elif 157.5 <= deg < 202.5:
        return Wind.S
    elif 202.5 <= deg < 247.5:
        return Wind.SW
    elif 247.5 <= deg < 292.5:
        return Wind.W
    elif 292.5 <= deg < 337.5:
        return Wind.NW
    elif 337.5 <= deg <= 359:
        return Wind.N
    else:
        raise ValueError(f"Incorrect wind direction value: {deg}. Should be a number between 0 and 359.")


UNIT_MAP: dict[str, dict] = {
    "standard": {"temp": "K", "wind": "m/s"},
    "metric": {"temp": f"{DEGREE}C", "wind": "km/h"},
    "imperial": {"temp": f"{DEGREE}F", "wind": "mph"},
}


def create_location_and_time_panel(weather_data: Current) -> Panel:
    loc_txt: str = f":globe_with_meridians: {weather_data.loc} "
    date = weather_data.dt.strftime("%b %d, %Y")
    time = weather_data.dt.strftime("%H:%M")
    dt_txt: str = f":calendar: {date} :clock10: {time}\n\n"
    sun_txt: str = (
        f":sunrise: {weather_data.sunrise.strftime('%H:%M')} " f":sunset: {weather_data.sunset.strftime('%H:%M')}"
    )
    txt = loc_txt + dt_txt + sun_txt
    loc_panel = Panel(renderable=txt, title="[b]Location & Time[/b]", expand=False, padding=(1, 3))
    return loc_panel


def create_current_weather_panel(weather_data: Current, units: str) -> Panel:
    weather_txt: str = ""
    for desc, icon in weather_data.weather.description:
        weather_txt += f"{API_ICON_TO_EMOJI[icon]} {desc.title()}"
    weather_txt += "\n"

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
    weather_panel = Panel(
        renderable=weather_txt, title="[b]Current Weather Conditions[/b]", expand=False, padding=(1, 3)
    )
    return weather_panel


def show_current_weather(weather_data: Current, units: str) -> None:
    loc_panel = create_location_and_time_panel(weather_data)
    weather_panel = create_current_weather_panel(weather_data, units)
    # layout = Layout(size=1)
    # layout.split_row(
    #     loc_panel,
    #     weather_panel,
    # )
    print("\n")
    print(loc_panel)
    print(weather_panel)
