import sys
import folium
import io
import datetime as dt
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import gui.gui_func as gui_func
from gui.gui_table import Table


class EnergyStorage(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        self.setFont(QFont('Calibri', 12))
        # Labels
        description = 'Add battery storage to the energy system \n'
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setWordWrap(True)
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
        self.opm_l = QLabel()
        self.opm_l.setText('Operation and maintenance cost (optional) [US$/a]')
        # Overview
        self.component_df = pd.DataFrame(columns=['Component',
                                                  'Name',
                                                  'Power [kW]',
                                                  'Capacity [kWh]',
                                                  'Investment cost [US$]',
                                                  'Operation maintenance cost [US$/a]',
                                                  'Initial CO2 emissions [kg]'])

        self.table = Table(data=self.component_df)
        self.overview = QTableView()
        self.update_data()
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
        self.opm = QLineEdit()
        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0, 1, 2)
        self.layout.addWidget(self.p_l, 1, 0, Qt.AlignRight)
        self.layout.addWidget(self.p, 1, 1, Qt.AlignTop)
        self.layout.addWidget(self.c_l, 2, 0, Qt.AlignRight)
        self.layout.addWidget(self.c, 2, 1, Qt.AlignTop)
        self.layout.addWidget(self.soc_l, 3, 0, Qt.AlignRight)
        self.layout.addWidget(self.soc, 3, 1, Qt.AlignTop)
        self.layout.addWidget(self.soc_min_l, 4, 0, Qt.AlignRight)
        self.layout.addWidget(self.soc_min, 4, 1, Qt.AlignTop)
        self.layout.addWidget(self.soc_max_l, 5, 0, Qt.AlignRight)
        self.layout.addWidget(self.soc_max, 5, 1, Qt.AlignTop)
        self.layout.addWidget(self.n_charge_l, 6, 0, Qt.AlignRight)
        self.layout.addWidget(self.n_charge, 6, 1, Qt.AlignTop)
        self.layout.addWidget(self.n_discharge_l, 7, 0, Qt.AlignRight)
        self.layout.addWidget(self.n_discharge, 7, 1, Qt.AlignTop)
        self.layout.addWidget(self.lifetime_l, 8, 0, Qt.AlignRight)
        self.layout.addWidget(self.lifetime, 8, 1, Qt.AlignTop)
        self.layout.addWidget(self.invest_l, 9, 0, Qt.AlignRight)
        self.layout.addWidget(self.invest, 9, 1, Qt.AlignTop)
        self.layout.addWidget(self.opm_l, 10, 0, Qt.AlignRight)
        self.layout.addWidget(self.opm, 10, 1, Qt.AlignTop)
        self.layout.addWidget(self.overview, 11, 0, 1, 2)
        self.setLayout(self.layout)

    def update_data(self):
        self.table = Table(data=self.component_df)
        self.overview.setModel(self.table)
        self.overview.resizeColumnsToContents()
