from typing import TypeAlias

from weatherpy.presenter.symbols import DEGREE, Wind

Number: TypeAlias = int | float


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
    elif 337.5 <= deg <= 360:
        return Wind.N
    else:
        raise ValueError(f"Incorrect wind direction value: {deg}. Should be a number between 0 and 360.")


UNIT_MAP: dict[str, dict] = {
    "standard": {"temp": "K", "wind": "m/s"},
    "metric": {"temp": f"{DEGREE}C", "wind": "km/h"},
    "imperial": {"temp": f"{DEGREE}F", "wind": "mph"},
}


def round_down_to_closest_multiple(num: Number, mult: Number) -> Number:
    return num // mult * mult
