"""
Module to display plot in GUI

@author: Paul Bohn
@contributor: Paul Bohn
"""

import datetime as dt
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar


class Plot(FigureCanvasQTAgg):
    """
    Class containing plot
    """
    def __init__(self,
                 df: pd.Series = None,
                 time_series: pd.Series = None,
                 parent=None,
                 width=5,
                 height=3,
                 dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)

        super().__init__(self.fig)
        self.setParent(parent)
        self.df = df
        self.time_series = time_series
        if self.time_series is not None:
            self.ax.plot(self.df)
            self.ax.set(ylabel='Power [W]')
