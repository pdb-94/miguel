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


class DG(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        self.setFont(QFont('Calibri', 12))

        # Labels
        description = 'Add diesel generator to the energy system. \n'
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setWordWrap(True)
        self.p_l = QLabel()
        self.p_l.setText('Power [kW]')
        self.fuel_l = QLabel()
        self.fuel_l.setText('Fuel consumption at nominal power [l/h]')
        self.invest_l = QLabel()
        self.invest_l.setText('Investment cost (optional) [US$]')
        self.op_main_l = QLabel()
        self.op_main_l.setText('Operation and maintenance cost (optional) [US$/a]')
        self.c_var_l = QLabel()
        self.c_var_l.setText('Variable cost (optional) [US$/kWh]')
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
        self.fuel = QLineEdit()
        self.invest = QLineEdit()
        self.op_main = QLineEdit()
        self.c_var = QLineEdit('0.021')
        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0, 1, 2)
        self.layout.addWidget(self.p_l, 1, 0, Qt.AlignRight)
        self.layout.addWidget(self.p, 1, 1, Qt.AlignTop)
        self.layout.addWidget(self.fuel_l, 2, 0, Qt.AlignRight)
        self.layout.addWidget(self.fuel, 2, 1, Qt.AlignTop)
        self.layout.addWidget(self.invest_l, 3, 0, Qt.AlignRight)
        self.layout.addWidget(self.invest, 3, 1, Qt.AlignTop)
        self.layout.addWidget(self.op_main_l, 4, 0, Qt.AlignRight)
        self.layout.addWidget(self.op_main, 4, 1, Qt.AlignTop)
        self.layout.addWidget(self.c_var_l, 5, 0, Qt.AlignRight)
        self.layout.addWidget(self.c_var, 5, 1, Qt.AlignTop)
        self.layout.addWidget(self.overview, 6, 0, 1, 2)
        self.setLayout(self.layout)

    def update_data(self):
        self.table = Table(data=self.component_df)
        self.overview.setModel(self.table)
        self.overview.resizeColumnsToContents()
