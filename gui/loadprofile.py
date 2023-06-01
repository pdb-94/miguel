import sys
import folium
import io
import datetime as dt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import gui_func as gui_func


class LoadProfile(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        self.setFont(QFont('Calibri', 11))
        description = """Add a load profile to the energy system. Enter the file path with the csv file for this. If no load profile is available, a reference load profile for afcrian hospitals will be used. To scale the energy consumption, the annual bard of electrical energy in kWh is needed."""
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setWordWrap(True)

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0)
        self.setLayout(self.layout)

