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


class WT(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        # windpowerib parameters
        self.turbine_lib = []

        # Standard widgets
        self.setFont(QFont('Calibri', 12))
        description = 'Add wind turbine to energy system\n' \
                      'Method 1 - Default: data input: min. power & max. power. Random wind turbin is selected within the power range. \n' \
                      'Method 2 - Advanced (only recommended for experienced users): data input: wind turbine and hub height. \n' \
                      'Method 3 - Profile: data input: path to wind turbine energy production profile (csv-file).\n\n'
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setWordWrap(True)
        self.method_combo_l = QLabel()
        self.method_combo_l.setText('Method')
        self.method_combo = QComboBox()
        method = ['Default', 'Advanced', 'Wind turbine profile']
        self.method_combo.addItems(method)
        self.invest_l = QLabel()
        self.invest_l.setText('Investment cost (optional) [US$]')
        self.opm_l = QLabel()
        self.opm_l.setText('Operation and maintenance cost (optional) [US$/a]')
        self.invest = QLineEdit()
        self.opm = QLineEdit()
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

        # Method 1
        self.p_min_l = QLabel()
        self.p_min_l.setText('Min. power [kW]')
        self.p_max_l = QLabel()
        self.p_max_l.setText('Max. power [kW]')
        self.p_min = QLineEdit()
        self.p_max = QLineEdit()
        # Method 2
        self.p_l = QLabel()
        self.p_l.setText('Power [kW]')
        self.turbine_l = QLabel()
        self.turbine_l.setText('Wind turbine')
        self.height_l = QLabel()
        self.height_l.setText('Hub height [m]')
        self.p = QLineEdit()
        self.turbine = QComboBox()
        self.turbine.addItems(self.turbine_lib)
        self.height = QLineEdit()

        # Method 3
        self.profile_l = QLabel()
        self.profile_l.setText('Wind turbine profile path')
        self.profile = QLineEdit()
        self.browse = QPushButton('Browse')
        # Widget container
        self.method_1 = [self.p_min_l, self.p_max_l, self.p_min, self.p_max]
        self.method_2 = [self.p_l, self.turbine_l, self.p, self.turbine, self.height_l, self.height]
        self.method_3 = [self.p_l, self.p, self.profile_l, self.profile, self.browse]

        self.method_combo.currentIndexChanged.connect(self.simulation_method)
        self.browse.clicked.connect(self.get_profile)

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0, 1, 2)
        self.layout.addWidget(self.method_combo_l, 1, 0, Qt.AlignRight)
        self.layout.addWidget(self.method_combo, 1, 1, Qt.AlignTop)
        self.layout.addWidget(self.p_min_l, 2, 0, Qt.AlignRight)
        self.layout.addWidget(self.p_min, 2, 1, Qt.AlignTop)
        self.layout.addWidget(self.p_l, 2, 0, Qt.AlignRight)
        self.layout.addWidget(self.p, 2, 1, Qt.AlignTop)
        self.layout.addWidget(self.profile_l, 3, 0, Qt.AlignRight)
        self.layout.addWidget(self.profile, 3, 1, Qt.AlignTop)
        self.layout.addWidget(self.browse, 3, 2, Qt.AlignLeft)
        self.layout.addWidget(self.p_max_l, 3, 0, Qt.AlignRight)
        self.layout.addWidget(self.p_max, 3, 1, Qt.AlignTop)
        self.layout.addWidget(self.turbine_l, 3, 0, Qt.AlignRight)
        self.layout.addWidget(self.turbine, 3, 1, Qt.AlignTop)
        self.layout.addWidget(self.height_l, 4, 0, Qt.AlignRight)
        self.layout.addWidget(self.height, 4, 1, Qt.AlignTop)
        self.layout.addWidget(self.invest_l, 5, 0, Qt.AlignRight)
        self.layout.addWidget(self.invest, 5, 1, Qt.AlignTop)
        self.layout.addWidget(self.opm_l, 6, 0, Qt.AlignRight)
        self.layout.addWidget(self.opm, 6, 1, Qt.AlignTop)
        self.layout.addWidget(self.overview, 7, 0, 1, 3)
        self.setLayout(self.layout)

        gui_func.show_widget(widget=self.method_2, show=False)
        gui_func.show_widget(widget=self.method_3, show=False)
        gui_func.show_widget(widget=self.method_1, show=True)

    def get_profile(self):
        """
        Open QFileDialog to select Wt profile
        :return:
        """
        response = QFileDialog.getOpenFileName(parent=self,
                                               caption='Select wind turbine profile',
                                               filter='Data file (*.csv)',
                                               directory=sys.path[1])
        wt_profile = response[0]
        self.profile.setText(wt_profile)

        return wt_profile

    def simulation_method(self):
        index = self.method_combo.currentIndex()
        if index == 0:
            gui_func.show_widget(widget=self.method_2, show=False)
            gui_func.show_widget(widget=self.method_3, show=False)
            gui_func.show_widget(widget=self.method_1, show=True)
        elif index == 1:
            gui_func.show_widget(widget=self.method_1, show=False)
            gui_func.show_widget(widget=self.method_3, show=False)
            gui_func.show_widget(widget=self.method_2, show=True)
        elif index == 2:
            gui_func.show_widget(widget=self.method_1, show=False)
            gui_func.show_widget(widget=self.method_2, show=False)
            gui_func.show_widget(widget=self.method_3, show=True)

    def update_data(self):
        self.table = Table(data=self.component_df)
        self.overview.setModel(self.table)
        self.overview.resizeColumnsToContents()
