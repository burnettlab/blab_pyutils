"""Decorators for plotting functions"""

import os
import re
import logging
from functools import wraps
from pathlib import Path
from typing import Callable

import matplotlib as mpl
import matplotlib.pyplot as plt
from auto_all import public


LOGGER = logging.getLogger(__name__)


@public
def save_plots(func: Callable) -> Callable:
    """Decorator to save plots to the output directory.
    The decorated function should return a dictionary of {plot_name: figure} pairs.
    """

    @wraps(func)
    def save_plots_wrapper(*args, obscure_plot: bool = True, **kwargs):
        if not (plots := func(*args, obscure_plot=obscure_plot, **kwargs)):
            return

        try:
            if obscure_plot:
                images_dir = Path.cwd() / "Images"
            elif env_path := os.getenv("IMAGES_DIR"):
                images_dir = Path(env_path) / "data" / "plots"
            else:
                raise FileNotFoundError("No images directory specified.")
            images_dir.mkdir(parents=True, exist_ok=True)
        except FileNotFoundError as e:
            LOGGER.warning(f"{e}\nPlots will not be saved to disk.")
            images_dir = None

        for plot_name, fig in plots.items():
            if images_dir is not None:
                for ext in map(
                    lambda e: re.sub(r"^\.", "", e),
                    os.getenv("IMAGE_FORMATS", ["png", "svg"]),
                ):
                    fig.savefig(
                        images_dir / f"{plot_name}.{ext}",
                        format=ext,
                        bbox_inches="tight",
                    )
            else:
                plt.show(block=False)
            plt.close(fig)

    return save_plots_wrapper
