from datetime import datetime
from typing import Callable, Optional, Union

import plotext as plt
from rich import print
from rich.ansi import AnsiDecoder
from rich.console import Group
from rich.jupyter import JupyterMixin
from rich.layout import Layout
from rich.panel import Panel

from weatherpy.api.models import Forecast

from .utils import UNIT_MAP, get_wind_direction, round_down_to_closest_multiple


def make_layout() -> Layout:
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=1),
        Layout(name="report", ratio=1),
    )
    layout["report"].split_column(
        Layout(name="1st", ratio=1),
        Layout(name="2nd"),
        Layout(name="3rd"),
        Layout(name="4th"),
    )
    return layout


class WeatherPlot(JupyterMixin):
    def __init__(
        self,
        x,
        y,
        plotting_fn: Callable = plt.plot,
        xlabel: str = "",
        datalabel: Union[str, list[str]] = "",
        datalabel2: str = "",
        y2: Optional[list] = None,
        markers: Optional[Union[str, list[str]]] = "braille",
    ):
        if y2 is None:
            y2 = []
        self.decoder = AnsiDecoder()
        self.x = x
        self.y = y
        self.plotting_fn = plotting_fn
        self.xlabel = xlabel
        self.datalabel = datalabel
        self.datalabel2 = datalabel2
        self.y2 = y2
        self.marker = markers

    def __rich_console__(self, console, options):
        self.width = options.max_width or console.width
        self.height = options.height or console.height
        canvas = self._build()
        self.rich_canvas = Group(*self.decoder.decode(canvas))
        yield self.rich_canvas

    def _build(self):
        plt.clf()
        self.plotting_fn(self.x, self.y, label=self.datalabel, marker=self.marker)
        if self.y2:
            self.plotting_fn(self.x, self.y2, label=self.datalabel2, marker=self.marker)
        plt.plotsize(self.width, self.height)
        plt.xaxes(1, 0)
        plt.yaxes(1, 0)
        plt.xlabel(self.xlabel)
        xticks, labels = self._make_x_axis_labels()
        plt.xticks(ticks=xticks, labels=labels)
        plt.theme("clear")
        return plt.build()

    def _make_x_axis_labels(self) -> tuple[list[int], list[str]]:
        mx = self.x[-1]
        t = int(round_down_to_closest_multiple(datetime.now().timestamp(), 24 * 3600)) - 3600
        xticks = []
        while t <= mx:
            xticks.append(t)
            t += 8 * 3600
        labels = []
        for t in xticks:
            dt = datetime.fromtimestamp(t)
            fmt = "%H:%M" if dt.hour else "%a %H:%M"
            labels.append(dt.strftime(fmt))
        return xticks, labels


def show_forecast(forecast: Forecast, units: str) -> None:
    layout = make_layout()

    header = layout["header"]
    title = f":globe_with_meridians: {forecast.loc}"
    header.update(title)
    dts = [int(round(dt.timestamp())) for dt, _ in forecast.weathers]

    temp_layout = layout["1st"]
    temp_plot = Panel(
        WeatherPlot(
            x=dts,
            y=[weather.temp for _, weather in forecast.weathers],
            y2=[weather.temp_feel for _, weather in forecast.weathers],
            datalabel=f"Actual [{UNIT_MAP[units]['temp']}]",
            datalabel2=f"Feels like [{UNIT_MAP[units]['temp']}]",
        ),
        title="Temperature",
    )
    temp_layout.update(temp_plot)

    mult = 3.6 if units == "metric" else 1
    wind_layout = layout["2nd"]
    wind_plot = Panel(
        WeatherPlot(
            x=dts,
            y=[weather.wind_spd * mult for _, weather in forecast.weathers],
            datalabel=f"Speed [{UNIT_MAP[units]['wind']}]",
            markers=[get_wind_direction(weather.wind_deg).value for _, weather in forecast.weathers],
        ),
        title="Wind",
    )
    wind_layout.update(wind_plot)

    precipitation_layout = layout["3rd"]
    precipitation_plot = Panel(
        WeatherPlot(
            x=dts,
            y=[
                [weather.rain.get("3h", 0) for _, weather in forecast.weathers],
                [weather.snow.get("3h", 0) for _, weather in forecast.weathers],
            ],
            plotting_fn=plt.stacked_bar,
            datalabel=[" Rain [mm]", " Snow [mm]"],
            markers=["braille", "snowflake"],
        ),
        title="Precipitation in the Last 3 Hours",
    )
    precipitation_layout.update(precipitation_plot)

    pressure_layout = layout["4th"]
    pressure_plot = Panel(
        WeatherPlot(
            x=dts,
            y=[weather.pressure for _, weather in forecast.weathers],
            datalabel="Pressure [hPa]",
        ),
        title="Pressure",
    )
    pressure_layout.update(pressure_plot)

    print(Panel(layout, title="Weather Report"))
