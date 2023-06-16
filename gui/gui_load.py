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
        self.setFont(QFont('Calibri', 12))
        description = 'Add a load profile to the energy system\n' \
                      'Method 1 - Reference load profile: choose reference load profile from list. Enter annual electricity consumption [kWh/a] to scale load profile.\n' \
                      'Method 2 - Individual load profile: provide individual load profile as a csv-file. Enter load profile file path.\n\n'
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setWordWrap(True)
        # Content
        self.consumption_l = QLabel()
        self.consumption_l.setText('Annual electricity demand [kWh]')
        self.ref_profile_l = QLabel()
        self.ref_profile_l.setText('Reference load profile')
        self.load_profile_l = QLabel()
        self.load_profile_l.setText('Load profile path')
        self.consumption = QLineEdit()
        self.ref_profile = QComboBox()
        items = ['Hospital Ghana',
                 'H0 - Household',
                 'G0 - General trade/business/commerce',
                 'G1 - Business on weekdays 8 a.m. - 6 p.m.',
                 'G2 - Businesses with heavy to predominant consumption in the evening hours',
                 'G3 - Continuous business',
                 'G4 - Shop/barber shop',
                 'G5 - Bakery',
                 'G6 - Weekend operation',
                 'L0 - General farms',
                 'L1 - Farms with dairy farming/part-time livestock farming',
                 'L2 - Other farms']
        self.ref_profile.addItems(items)
        self.load_profile = QLineEdit()
        # Set up Plot
        self.plot = Plot()
        self.toolbar = self.toolbar = NavigationToolbar(self.plot, self)

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0, 1, 2, Qt.AlignTop)
        self.layout.addWidget(self.consumption_l, 1, 0, Qt.AlignTop)
        self.layout.addWidget(self.consumption, 1, 1, Qt.AlignTop)
        self.layout.addWidget(self.ref_profile_l, 2, 0, Qt.AlignTop)
        self.layout.addWidget(self.ref_profile, 2, 1, Qt.AlignTop)
        self.layout.addWidget(self.load_profile_l, 3, 0, Qt.AlignTop)
        self.layout.addWidget(self.load_profile, 3, 1, Qt.AlignTop)
        self.layout.addWidget(self.toolbar, 5, 0, 1, 2, Qt.AlignTop)
        self.layout.addWidget(self.plot, 5, 0, 1, 2, Qt.AlignTop)
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
                         width=5, height=12, dpi=150)
        self.toolbar = NavigationToolbar(self.plot, self)
        # Add Widgets to Layout
        self.layout.addWidget(self.toolbar, 4, 0, 1, 2)
        self.layout.addWidget(self.plot, 5, 0, 1, 2)

    def clear_plot(self):
        """
        Reset plot
        :return: None
        """
        self.plot = Plot()
        self.toolbar = NavigationToolbar(self.plot, self)
        # Add Widgets to Layout
        self.layout.addWidget(self.toolbar, 4, 0, 1, 2)
        self.layout.addWidget(self.plot, 5, 0, 1, 2)

