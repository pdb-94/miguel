import sys
import folium
import io
import datetime as dt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import gui.gui_func as gui_func
from gui.gui_table import Table


class WeatherData(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        self.root = sys.path[1]
        self.setFont(QFont('Calibri', 12))

        description = "The weather data presented is retrieved from the PHOTOVOLTAIC GEOGRAPHICAL INFORMATION SYSTEM (PVGIS) hosted by the European Commission."
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setWordWrap(True)
        # PV
        self.solar_l = QLabel()
        self.solar_l.setText('Solar irradiation \nThe plot display the global horizontal, direct normal and direct horizontal irradiation in W/m².')
        self.solar_plot = QLabel()
        self.solar_plot.setAlignment(Qt.AlignHCenter)
        self.solar_plot.adjustSize()
        # Wind
        self.wind_l = QLabel()
        self.wind_l.setText('Wind \nThe plot displays the monthly average wind speed in m/s and wind direction in degree (180° south).')
        self.wind_plot = QLabel()
        self.wind_plot.setAlignment(Qt.AlignHCenter)
        self.wind_plot.adjustSize()
        # EU
        self.eu = QLabel()
        gui_func.create_pixmap(self.root + '/gui/images/European_Commission.png', widget=self.eu, w=200, h=200)

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0, 1, 2)
        self.layout.addWidget(self.solar_l, 1, 0)
        self.layout.addWidget(self.solar_plot, 2, 0)
        self.layout.addWidget(self.wind_l, 1, 1)
        self.layout.addWidget(self.wind_plot, 2, 1)
        self.layout.addWidget(self.eu, 3, 0)
        self.setLayout(self.layout)
