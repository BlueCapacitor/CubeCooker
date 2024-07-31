from collections.abc import Iterator, Sequence
from itertools import islice

import matplotlib.pyplot as plt
from csv import reader

from matplotlib.axes import Axes
from matplotlib.colors import hsv_to_rgb
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

RECIPIE_PATH: str = "recipie.csv"
PLOT_SET_PATH: str = "plots.csv"

TITLE: str = "Temperature Profiles"

OPACITY: float = 0.6

recipies: dict[str, list[tuple[float, float]]] = {}

with open(RECIPIE_PATH, 'r') as recipe_file:
    recipie_reader: reader = reader(recipe_file)
    for row in islice(recipie_reader, 1, None):
        row_iter: Iterator[str] = iter(row)
        cube_flavor: str = next(row_iter)
        current_temp: float = float(next(row_iter))
        current_time: float = 0

        recipie: list[tuple[float, float]] = [(current_time, current_temp)]

        while True:
            try:
                hold_time: float = float(next(row_iter))
            except StopIteration:
                break
            current_time += hold_time
            recipie.append((current_time, current_temp))

            try:
                rate: float = float(next(row_iter)) * 60
                new_temp: float = float(next(row_iter))
            except StopIteration:
                break
            current_time += (new_temp - current_temp) / rate
            current_temp = new_temp
            recipie.append((current_time, current_temp))

        recipies[cube_flavor] = recipie

max_x_val: float = max(point[0] for recipie in recipies.values() for point in recipie)

plots: list[list[tuple[str, list[tuple[float, float]]]]] = []

with open(PLOT_SET_PATH, 'r') as plot_set_file:
    plot_set_reader: reader = reader(plot_set_file)
    for recipie_names in plot_set_reader:
        plot: list[tuple[str, list[tuple[float, float]]]] = []
        for recipie_name in recipie_names:
            recipie: list[tuple[float, float]] = recipies[recipie_name]
            plot.append((recipie_name, recipie))
        plots.append(plot)

subplots: tuple[Figure, Sequence[Axes]] = plt.subplots(nrows=len(plots), sharex="col")
fig, axs = subplots

for ax, plot in zip(axs, plots):
    ax: Axes
    num_plots: int = len(plot)
    colors = [hsv_to_rgb((h / num_plots, 1, 1)) for h in range(num_plots)]
    lines: list[list[Line2D]] = []
    for (recipie_name, recipie), color in zip(plot, colors):
        lines.append(ax.plot(
            *zip(*recipie),
            label=recipie_name,
            color=color,
            alpha=OPACITY
        ))

    ax.set_xlim(0, max_x_val)
    ax.set_ylim(0)

    ax.minorticks_on()
    ax.locator_params(axis='y', nbins=4)

    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    ax.grid()

axs[len(axs) // 2].set(ylabel="Temperature (C)")

axs[-1].set(xlabel="Time (hours)")

fig.suptitle(TITLE)

plt.tight_layout()

fig.savefig("out.png", dpi=512)
plt.show()
