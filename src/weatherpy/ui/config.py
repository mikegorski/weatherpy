import re
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

from ip2geotools.databases.noncommercial import DbIpCity
from rich import print
from rich.pretty import pprint
from rich.prompt import Confirm, IntPrompt, Prompt

from weatherpy.api.comm import api_token_valid, get_ip_address, get_locations_by_coords, get_locations_by_name
from weatherpy.api.models import Geolocation

CFG_FILENAME: str = "weatherpy.cfg"
HOME_DIR: Path = Path.home() / "weatherpy"
TOKEN_PATTERN: str = "^[a-z0-9]{32}$"

OPEN_WEATHER_LOGIN_URL: str = "https://home.openweathermap.org/users/sign_up"
OPEN_WEATHER_API_KEY_ERROR_URL: str = "https://openweathermap.org/faq#error401"


def read_cfg_file() -> ConfigParser:
    config = ConfigParser()
    try:
        config.read_file(open(HOME_DIR / CFG_FILENAME))
    except FileNotFoundError as exc:
        raise exc
    return config


def is_api_token_format_valid(api_token: str) -> bool:
    return re.match(TOKEN_PATTERN, api_token) is not None


def set_api_key() -> str:
    while True:
        token = Prompt.ask(
            "[cyan]Please provide an API key (a free API key can be obtained at "
            f"[underline]{OPEN_WEATHER_LOGIN_URL}[/underline]) [/cyan]"
        )
        if not is_api_token_format_valid(token):
            print("[bold red blink]Incorrect API key format.[/] [cyan]Please check if it was pasted correctly.[/]")
            continue
        if not api_token_valid(token):
            print(
                "[bold red blink]Invalid API key.[/] [cyan]Please see "
                f"[underline]{OPEN_WEATHER_API_KEY_ERROR_URL}[/underline] for more info.[/]"
            )
            continue
        return token


def set_units() -> str:
    mapping = {"m": "metric", "i": "imperial", "s": "standard"}
    setting = Prompt.ask(
        "[cyan]Please choose [b]m[/b]etric, [b]i[/b]mperial or [b]s[/b]tandard units[/cyan]",
        choices=list(mapping.keys()),
        default="m",
    )
    return mapping[setting]


def handle_many_location_choices(locs: list[Geolocation]) -> Optional[Geolocation]:
    print("[cyan]Several locations matching your query have been found.[/]")
    for i, loc in enumerate(locs):
        print(f"{i + 1}. {loc}")

    if not Confirm.ask(r"[cyan]\Type [y] to continue or [N] to reject choices and try again[/cyan]", default=True):
        return None

    while True:
        n = IntPrompt.ask("[cyan]Please choose the number corresponding to your choice:[/cyan]")
        if n not in range(1, len(locs) + 1):
            print(f"[light_red]Incorrect value chosen. Please choose number from range 1-{len(locs)}[/]")
            continue
        return locs[n - 1]


def set_location_by_city(api_token: str) -> Geolocation:
    while True:
        inp = Prompt.ask(
            "\n[cyan]Please provide a name of a location. Valid example formats are:[/cyan]\n"
            "[green]- London\n"
            "- London, GB\n"
            "- London, Kentucky, US[/green]\n"
            "\n[cyan]Your choice[/cyan]"
        )
        if not len(inp):
            print("[light_red]\nNo location name provided. Please try again.[/light_red]")
            continue
        locs = get_locations_by_name(name=inp, token=api_token)
        if not locs:
            print("[light_red]\nProvided name couldn't be geocoded. Please try again.[/light_red]")
            continue

        if len(locs) == 1:
            loc = locs[0]
            print(f"[green] Location found: [light_green]\n{loc}[/]")
            if Confirm.ask(
                r"[cyan]\[y] accept location \[n] reject location and provide a different name[/cyan]", default=True
            ):
                return loc
            continue

        if choice := handle_many_location_choices(locs):
            return choice


def set_location_by_coords(api_token: str) -> Geolocation:
    while True:
        inp = Prompt.ask(
            "[cyan]\nPlease input geographic coordinates (lat, lon) separated by a comma "
            r"[green]\[example: 27.51434,83.099336][/]"
        )
        if len(inp) < 3 or "," not in inp:
            print("[light_red]\nIncorrect value typed. The correct format is latitude,longitude.[/light_red]")
            continue
        cleaned_input = "".join(inp.split())
        lat, lon = cleaned_input.split(sep=",")
        if not geo_coords_valid(loc=(lat, lon)):
            print(
                "[bold red blink]\nIncorrect value typed.[/] [cyan]The correct format is latitude,longitude "
                "using '.' as decimal separator. "
                "Remember that latitude is a number in range [-90;90] and longitude [-180;180].[/]"
            )
            continue

        locs = get_locations_by_coords(float(lat), float(lon), token=api_token)

        if not locs:
            print("[light_red]\nNo location available for given coordinates. Please try again.[/light_red]")
            continue

        if len(locs) == 1:
            loc = locs[0]
            print(f"[green]\nLocation found: [light_green]{loc}[/]")
            if Confirm.ask(
                r"[cyan]\[y] accept location \[n] reject location and provide different coordinates[/cyan]",
                default=True,
            ):
                return loc
            continue

        if choice := handle_many_location_choices(locs):
            return choice


def geo_coords_valid(loc: tuple[str, str]) -> bool:
    try:
        loc2 = (float(loc[0]), float(loc[1]))
    except (ValueError, TypeError):
        return False
    return -90 <= loc2[0] <= 90 and -180 <= loc2[1] <= 180


def determine_location_based_on_ip(api_token: str) -> tuple[str, Optional[Geolocation]]:
    ip = get_ip_address()
    response = DbIpCity.get(ip_address=ip, api_key="free")
    lat, lon = float(str(response.latitude)), float(str(response.longitude))
    locs = get_locations_by_coords(lat, lon, token=api_token)
    return (ip, locs[0]) if locs else (ip, None)


def set_location(api_token: str) -> Geolocation:
    ip, loc = determine_location_based_on_ip(api_token)
    if loc:
        if Confirm.ask(
            f"[cyan]\nBased on your IP address ({ip}), your default location has been set to "
            f"[light_green]{loc.name}, {loc.state}, {loc.country} ({loc.lat}, {loc.lon})[/light_green]. "
            f"Do you want to keep this setting or provide a different location?[/cyan]",
            default=True,
        ):
            return loc
    else:
        print("[light_red]\nYour location couldn't be determined automatically.[/]")

    while True:
        loc = None
        inp = Prompt.ask(
            "[cyan]\nPlease choose preferred way of setting your location: \\[c]ity or \\[l]atitude, longitude[/cyan]",
            choices=["c", "l"],
        )
        if inp == "c":
            loc = set_location_by_city(api_token)
        elif inp == "l":
            loc = set_location_by_coords(api_token)
        if loc:
            return loc
        print("\n[bold red blink]Invalid coordinates.[/] [light_red]Please try again.[/]")


def create_cfg_file() -> ConfigParser:
    token = set_api_key()
    units = set_units()
    geolocation: Geolocation = set_location(api_token=token)
    config = ConfigParser()
    config["SETTINGS"] = {}
    settings = config["SETTINGS"]
    settings["token"] = token
    settings["units"] = units
    config["HOME"] = {}
    home = config["HOME"]
    home["name"] = geolocation.name
    home["state/region"] = geolocation.state
    home["country"] = geolocation.country
    home["lat"] = str(geolocation.lat)
    home["lon"] = str(geolocation.lon)
    if not HOME_DIR.exists():
        Path(HOME_DIR).mkdir(exist_ok=False)
    with Path.open(HOME_DIR / CFG_FILENAME, mode="w", encoding="utf8") as file:
        config.write(file)
    return config


def handle_config() -> ConfigParser:
    try:
        config = read_cfg_file()
    except FileNotFoundError:
        print("[bold blue]Settings file not found. Creating configuration...[/]")
        config = create_cfg_file()
    return config


def display_config() -> None:
    try:
        config = read_cfg_file()
    except FileNotFoundError:
        print("[bold red blink]Settings file not found.[/]")
        if not Confirm.ask("[bold blue]Do you want to create it?[/]", default=True):
            exit(0)
        config = create_cfg_file()
    pprint({section: dict(config[section]) for section in config.sections()}, expand_all=True)
