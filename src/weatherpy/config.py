import re
from configparser import ConfigParser
from pathlib import Path

from colorama import Fore
from colorama import init as colorama_init
from ip2geotools.databases.noncommercial import DbIpCity

from .api.comm import api_token_valid, get_ip_address, get_locations_by_name

colorama_init()

CFG_FILENAME: str = "weatherpy.cfg"
HOME_DIR: Path = Path.home() / "weatherpy"
TOKEN_PATTERN: str = "^[a-z0-9]{32}$"


def read_cfg_file() -> ConfigParser:
    config = ConfigParser()
    try:
        config.read_file(open(HOME_DIR / CFG_FILENAME))
    except FileNotFoundError as exc:
        raise exc
    return config


def set_api_key() -> str:
    while True:
        token = input(
            f"{Fore.CYAN}Please provide an API key (a free API key can be obtained at "
            f"{Fore.GREEN}https://home.openweathermap.org/users/sign_up{Fore.RESET}):"
        )
        api_key_valid_format = re.match(TOKEN_PATTERN, token) is not None
        if not api_key_valid_format:
            print(
                f"{Fore.LIGHTRED_EX}Incorrect API key format. " f"Please check if it was pasted correctly.{Fore.RESET}"
            )
            continue
        if not api_token_valid(token):
            print(
                f"{Fore.LIGHTRED_EX}Invalid API key. "
                f"Please see https://openweathermap.org/faq#error401 for more info.{Fore.RESET}"
            )
            continue
        return token


def set_units() -> str:
    mapping = {"m": "metric", "i": "imperial"}
    setting: str = "m"
    choice_valid: bool = False
    while not choice_valid:
        setting = input(
            f"{Fore.CYAN}Please choose metric [m] or imperial [i] units {Fore.GREEN}[default: m]{Fore.RESET} "
        )
        if not setting:
            return "metric"
        choice_valid = setting in ["m", "i"]
        if not choice_valid:
            print(
                f"{Fore.LIGHTRED_EX}Incorrect value chosen. Please type 'm' for metric or 'i' for imperial.{Fore.RESET}"
            )
    return mapping[setting]


def location_by_city(api_token: str) -> tuple[float, float]:
    while True:
        inp = input(
            f"{Fore.CYAN}\nPlease provide a name of a location. Valid example formats are:\n"
            f"{Fore.GREEN}- London\n"
            f"- London, GB\n"
            f"- London, Kentucky, US\n"
            f"{Fore.CYAN}\nYour choice: {Fore.RESET}"
        )
        if not len(inp):
            print(f"{Fore.LIGHTRED_EX}No location name provided. Please try again.{Fore.RESET}")
            continue
        locs = get_locations_by_name(name=inp, token=api_token)
        if not locs:
            print(f"{Fore.LIGHTRED_EX}Provided name couldn't be geocoded. Please try again.{Fore.RESET}")
            continue

        accepted: bool = True
        if len(locs) == 1:
            loc = locs[0]
            print(f"{Fore.GREEN} Location found: {Fore.LIGHTGREEN_EX}{loc}{Fore.RESET}")
            while True:
                inp = input(
                    f"{Fore.CYAN}[y] accept location [N] reject location and provide a different name: {Fore.RESET}"
                )
                if not inp or inp == "y":
                    return loc.lat, loc.lon
                if inp != "N":
                    print(
                        f"{Fore.LIGHTRED_EX}Incorrect value chosen. "
                        f"Please type 'y' to accept or 'N' to reject.{Fore.RESET}"
                    )
                    continue
                assert inp == "N"
                accepted = False
                break
            if not accepted:
                continue

        print(f"{Fore.CYAN}Several locations matching your query have been found.{Fore.RESET}")
        for i, loc in enumerate(locs):
            print(f"{i+1}. {loc}")
        while True:
            n = int(input(f"{Fore.CYAN}Please choose the number corresponding to your choice: {Fore.RESET}"))
            if n not in range(1, len(locs) + 1):
                print(
                    f"{Fore.LIGHTRED_EX}Incorrect value chosen. "
                    f"Please choose number from range 1-{len(locs)}{Fore.RESET}"
                )
                continue
            choice = locs[n - 1]
            return choice.lat, choice.lon


def location_by_coords() -> tuple[float, float]:
    while True:
        inp = input(
            f"{Fore.CYAN}Please input geographic coordinates (lat, lon) separated by a comma "
            f"{Fore.GREEN}[example: 27.51434,83.099336]: {Fore.RESET}"
        )
        if len(inp) < 3 or "," not in inp:
            print(f"{Fore.LIGHTRED_EX}Incorrect value typed. The correct format is latitude,longitude.{Fore.RESET}")
            continue
        sep = ", " if " " in inp else ","
        lat, lon = inp.split(sep)
        if geo_coords_valid(loc=(lat, lon)):
            return float(lat), float(lon)
        print(
            f"{Fore.LIGHTRED_EX}Incorrect value typed. The correct format is latitude,longitude "
            f"using '.' as decimal separator.{Fore.RESET}"
        )


def geo_coords_valid(loc) -> bool:
    try:
        loc = (float(loc[0]), float(loc[1]))
    except ValueError:
        return False
    return isinstance(loc, tuple) and len(loc) == 2


def set_location(api_token: str) -> tuple[float, float]:
    ip = get_ip_address()
    response = DbIpCity.get(ip_address=ip, api_key="free")
    city, region, country, lat, lon = (
        response.city,
        response.region,
        response.country,
        response.latitude,
        response.longitude,
    )
    while True:
        inp = input(
            f"{Fore.CYAN}Based on your IP address ({ip}), your default location has been set to "
            f"{Fore.LIGHTGREEN_EX}{city}, {region}, {country} ({lat}, {lon}). "
            f"{Fore.CYAN}Do you want to keep this setting [y] "
            f"or provide a different location [N]? {Fore.GREEN}[default: y]{Fore.RESET} "
        )
        if not inp or inp == "y":
            assert lat and lon
            return lat, lon
        if inp != "N":
            print(
                f"{Fore.LIGHTRED_EX}Incorrect response. Please type 'y' to accept or 'N' to reject current default "
                f"setting {Fore.LIGHTMAGENTA_EX}[{city}, {region}, {country} ({lat}, {lon})].{Fore.RESET}"
            )
            continue
        break

    while True:
        loc = None
        inp = input(
            f"{Fore.CYAN}Please choose preferred way of setting your location: "
            f"{Fore.GREEN}[c]ity or [l]atitude, longitude {Fore.RESET}"
        )
        if inp not in ["c", "l"]:
            print(
                f"{Fore.LIGHTRED_EX}Incorrect value chosen. Available values are {Fore.GREEN}[c]ity or [l]atitude, "
                f"longitude {Fore.RESET}"
            )
            continue
        if inp == "c":
            loc = location_by_city(api_token)
        elif inp == "l":
            loc = location_by_coords()
        if loc:
            return loc
        print(f"{Fore.LIGHTRED_EX}Invalid coordinates. Please try again.{Fore.RESET}")


def create_cfg_file() -> ConfigParser:
    token = set_api_key()
    units = set_units()
    lat, lon = set_location(api_token=token)
    config = ConfigParser()
    config["SETTINGS"] = {}
    settings = config["SETTINGS"]
    settings["token"] = token
    settings["units"] = units
    settings["lat"] = str(lat)
    settings["lon"] = str(lon)
    if not HOME_DIR.exists():
        Path(HOME_DIR).mkdir(exist_ok=False)
    with Path.open(HOME_DIR / CFG_FILENAME, mode="w") as file:
        config.write(file)
    return config


def handle_config() -> ConfigParser:
    try:
        config = read_cfg_file()
    except FileNotFoundError:
        print(f"{Fore.BLUE}Settings file not found. Creating configuration...{Fore.RESET}")
        config = create_cfg_file()
    return config
