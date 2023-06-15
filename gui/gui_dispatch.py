import sys
import folium
import io
import datetime as dt

import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import gui_func as gui_func
from gui_table import Table


class Dispatch(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        self.setFont(QFont('Calibri', 11))
        self.component_df = pd.DataFrame(columns=['Component',
                                                  'Name',
                                                  'Power [kW]',
                                                  'Capacity [kWh]',
                                                  'Investment cost [US$]',
                                                  'Operation maintenance cost [US$/a]',
                                                  'Initial CO2 emissions [kg]'])

        self.table = Table(data=self.component_df)
        self.overview = QTableView()
        # self.table_header()

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.overview, 1, 0)
        self.setLayout(self.layout)

    def table_header(self):
        header = self.overview.horizontalHeader()
        header.ResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

    def update_data(self):
        self.table = Table(data=self.component_df)
        self.overview.setModel(self.table)
