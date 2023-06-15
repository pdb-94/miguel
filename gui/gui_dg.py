import sys
import folium
import io
import datetime as dt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import gui_func as gui_func


class DG(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        self.setFont(QFont('Calibri', 10))

        # Labels
        self.p_l = QLabel()
        self.p_l.setText('Power [kW]')
        self.fuel_l = QLabel()
        self.fuel_l.setText('Fuel consumption at nominal power [l]')
        self.invest_l = QLabel()
        self.invest_l.setText('Investment cost (optional) [US$]')
        self.op_main_l = QLabel()
        self.op_main_l.setText('Operation and maintenance cost (optional) [US$/a]')
        self.c_var_l = QLabel()
        self.c_var_l.setText('Variable cost (optional) [US$/kWh]')
        # Edits
        self.p = QLineEdit()
        self.fuel = QLineEdit()
        self.invest = QLineEdit()
        self.op_main = QLineEdit()
        self.c_var = QLineEdit('0.021')
        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.p_l, 1, 0)
        self.layout.addWidget(self.p, 1, 1)
        self.layout.addWidget(self.fuel_l, 2, 0)
        self.layout.addWidget(self.fuel, 2, 1)
        self.layout.addWidget(self.invest_l, 3, 0)
        self.layout.addWidget(self.invest, 3, 1)
        self.layout.addWidget(self.op_main_l, 4, 0)
        self.layout.addWidget(self.op_main, 4, 1)
        self.layout.addWidget(self.c_var_l, 5, 0)
        self.layout.addWidget(self.c_var, 5, 1)
        self.setLayout(self.layout)
