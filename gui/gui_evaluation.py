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


class EvaluateSystem(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        self.setFont(QFont('Calibri', 12))
        description = 'Key parameters for system evaluation'
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setWordWrap(True)

        self.evaluation_df = pd.DataFrame(columns=['Annual energy supply [kWh/a]',
                                                   'Lifetime energy supply [kWh]',
                                                   'Lifetime cost [US$]',
                                                   'Investment cost [US$]',
                                                   'Annual cost [US$/a]',
                                                   'LCOE [US$/kWh]',
                                                   'Lifetime CO2 emissions [t]',
                                                   'Initial CO2 emissions [t]',
                                                   'Annual CO2 emissions [t/a]'])

        self.table = Table(data=self.evaluation_df)
        self.overview = QTableView()
        self.update_data()

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0, 1, 2)
        self.layout.addWidget(self.overview, 1, 0, 1, 2)
        self.setLayout(self.layout)

    def update_data(self):
        self.table = Table(data=self.evaluation_df)
        self.overview.setModel(self.table)
        self.overview.resizeColumnsToContents()
