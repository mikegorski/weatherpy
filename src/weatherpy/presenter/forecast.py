from datetime import datetime
from typing import Optional, Union

import plotext as plt
from rich import print
from rich.ansi import AnsiDecoder
from rich.console import Group
from rich.jupyter import JupyterMixin
from rich.layout import Layout
from rich.panel import Panel

from weatherpy.api.models import Forecast

from .utils import UNIT_MAP, get_wind_direction


def make_layout() -> Layout:
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=1),
        Layout(name="report", ratio=1),
    )
    layout["report"].split_column(
        Layout(name="temperature", ratio=1),
        Layout(name="wind"),
    )
    return layout


class WeatherPlot(JupyterMixin):
    def __init__(
        self,
        x,
        y,
        xlabel="Hours from now",
        datalabel="",
        datalabel2="",
        y2: Optional[list] = None,
        markers: Union[str, list[str]] = "braille",
    ):
        if y2 is None:
            y2 = []
        self.decoder = AnsiDecoder()
        self.x = x
        self.y = y
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
        plt.plot(self.x, self.y, label=self.datalabel, marker=self.marker)
        if self.y2:
            plt.plot(self.x, self.y2, label=self.datalabel2, marker=self.marker)
        plt.plotsize(self.width, self.height)
        plt.xaxes(1, 0)
        plt.yaxes(1, 0)
        plt.xlabel(self.xlabel)
        plt.xticks(ticks=[x for x in range(0, 121, 6)])
        plt.theme("clear")
        return plt.build()


def show_forecast(forecast: Forecast, units: str) -> None:
    layout = make_layout()

    header = layout["header"]
    title = f"Showing weather forecast for :globe_with_meridians: {forecast.loc}"
    header.update(title)

    dts = [(dt - datetime.now()).total_seconds() // 3600 for dt, _ in forecast.weathers]

    temp_layout = layout["temperature"]
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

    mult = 1
    if units == "metric":
        mult = 3.6
    wind_layout = layout["wind"]
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

    print(Panel(layout, title="Weather Report"))
