import sys
import folium
import io
import datetime as dt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import gui_func as gui_func


class EnergyStorage(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        self.setFont(QFont('Calibri', 10))
        # Labels
        self.p_l = QLabel()
        self.p_l.setText('Power [kW]')
        self.c_l = QLabel()
        self.c_l.setText('Capacity [kWh]')
        self.soc_l = QLabel()
        self.soc_l.setText('Initial state of charge [%]')
        self.soc_min_l = QLabel()
        self.soc_min_l.setText('Min. state of charge [%]')
        self.soc_max_l = QLabel()
        self.soc_max_l.setText('Max. state of charge [%]')
        self.n_charge_l = QLabel()
        self.n_charge_l.setText('Charging efficiency [%]')
        self.n_discharge_l = QLabel()
        self.n_discharge_l.setText('Discharging efficiency [%]')
        self.lifetime_l = QLabel()
        self.lifetime_l.setText('Calendaric lifetime [a]')
        self.invest_l = QLabel()
        self.invest_l.setText('Investment cost (optional) [US$]')
        self.op_main_l = QLabel()
        self.op_main_l.setText('Operation and maintenance cost (optional) [US$/a]')
        # Edits
        self.p = QLineEdit()
        self.c = QLineEdit()
        self.soc = QLineEdit('0.25')
        self.soc_min = QLineEdit('0.05')
        self.soc_max = QLineEdit('0.95')
        self.n_charge = QLineEdit('0.8')
        self.n_discharge = QLineEdit('0.8')
        self.lifetime = QLineEdit('10')
        self.invest = QLineEdit()
        self.op_main = QLineEdit()
        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.p_l, 1, 0)
        self.layout.addWidget(self.p, 1, 1)
        self.layout.addWidget(self.c_l, 2, 0)
        self.layout.addWidget(self.c, 2, 1)
        self.layout.addWidget(self.soc_l, 3, 0)
        self.layout.addWidget(self.soc, 3, 1)
        self.layout.addWidget(self.soc_min_l, 4, 0)
        self.layout.addWidget(self.soc_min, 4, 1)
        self.layout.addWidget(self.soc_max_l, 5, 0)
        self.layout.addWidget(self.soc_max, 5, 1)
        self.layout.addWidget(self.n_charge_l, 6, 0)
        self.layout.addWidget(self.n_charge, 6, 1)
        self.layout.addWidget(self.n_discharge_l, 7, 0)
        self.layout.addWidget(self.n_discharge, 7, 1)
        self.layout.addWidget(self.lifetime_l, 8, 0)
        self.layout.addWidget(self.lifetime, 8, 1)
        self.layout.addWidget(self.invest_l, 9, 0)
        self.layout.addWidget(self.invest, 9, 1)
        self.layout.addWidget(self.op_main_l, 10, 0)
        self.layout.addWidget(self.op_main, 10, 1)
        self.setLayout(self.layout)
