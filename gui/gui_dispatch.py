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


class Dispatch(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        self.setFont(QFont('Calibri', 12))
        description = 'Overview of system components'
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setWordWrap(True)
        self.system_type_l = QLabel()
        self.system_type_l.setText('System type')
        self.system_type = QLabel()

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

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0, 1, 2)
        self.layout.addWidget(self.system_type_l, 1, 0)
        self.layout.addWidget(self.system_type, 1, 1)
        self.layout.addWidget(self.overview, 2, 0, 1, 2)
        self.setLayout(self.layout)

    def update_data(self):
        self.table = Table(data=self.component_df)
        self.overview.setModel(self.table)
        self.overview.resizeColumnsToContents()
