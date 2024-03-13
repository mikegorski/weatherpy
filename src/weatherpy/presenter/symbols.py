from enum import Enum


class Wind(Enum):
    E = "\u2190"
    S = "\u2191"
    W = "\u2192"
    N = "\u2193"
    SE = "\u2196"
    SW = "\u2197"
    NW = "\u2198"
    NE = "\u2199"


DEGREE = "\u00b0"


API_ICON_TO_EMOJI: dict[str, str] = {
    "01d": ":yellow_circle:",
    "02d": ":sun_behind_cloud:",
    "03d": ":cloud:",
    "04d": ":cloud:",
    "09d": ":cloud_with_rain:",
    "10d": ":cloud_with_rain:",
    "11d": ":cloud_with_lightning_and_rain:",
    "13d": ":snowflake:",
    "50d": ":fog:",
    "01n": ":moon:",
    "02n": ":white_sun_behind_cloud:",
    "03n": ":cloud:",
    "04n": ":cloud:",
    "09n": ":cloud_with_rain:",
    "10n": ":cloud_with_rain:",
    "11n": ":cloud_with_lightning_and_rain:",
    "13n": ":snowflake:",
    "50n": ":fog:",
}
