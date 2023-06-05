import sys
import folium
import io
import datetime as dt
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
import gui_func as gui_func
from gui_plot import Plot


class LoadProfile(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        # Header
        self.setFont(QFont('Calibri', 11))
        description = """Add a load profile to the energy system. Enter the file path with the csv file for this. If no load profile is available, a reference load profile for African hospitals will be used. To scale the energy consumption, the annual demand of electrical energy in kWh is needed."""
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setWordWrap(True)
        # Content
        self.consumption_l = QLabel()
        self.consumption_l.setText('Annual electricity demand [kWh]')
        self.load_profile_l = QLabel()
        self.load_profile_l.setText('Load profile path')
        self.consumption = QLineEdit()
        self.load_profile = QLineEdit()
        # Set up Plot
        self.plot = Plot()
        self.toolbar = self.toolbar = NavigationToolbar(self.plot, self)

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0, 1, 2)
        self.layout.addWidget(self.consumption_l, 1, 0)
        self.layout.addWidget(self.consumption, 1, 1)
        self.layout.addWidget(self.load_profile_l, 2, 0)
        self.layout.addWidget(self.load_profile, 2, 1)
        self.layout.addWidget(self.toolbar, 3, 0, 1, 2)
        self.layout.addWidget(self.plot, 4, 0, 1, 2)
        self.setLayout(self.layout)

    def adjust_plot(self, df: pd.Series, time_series: pd.Series):
        """
        Plot DataFrame based on parameter load_profile
        :param time_series: pd.Series
            environment time_series
        :param df: pd.Series
            load_df
        :return: None
        """
        # Create Widgets
        self.plot = Plot(df=df,
                         time_series=time_series,
                         width=5, height=4, dpi=100)
        self.toolbar = NavigationToolbar(self.plot, self)
        # Add Widgets to Layout
        self.layout.addWidget(self.toolbar, 3, 0, 1, 2)
        self.layout.addWidget(self.plot, 4, 0, 1, 2)

    def clear_plot(self):
        """
        Reset plot
        :return: None
        """
        self.plot = Plot()
        self.toolbar = NavigationToolbar(self.plot, self)
        # Add Widgets to Layout
        self.layout.addWidget(self.toolbar, 3, 0, 1, 2)
        self.layout.addWidget(self.plot, 4, 0, 1, 2)

