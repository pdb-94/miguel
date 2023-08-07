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


class Photovoltaic(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        self.setFont(QFont('Calibri', 12))

        # pvlib parameters
        self.module_lib = []
        self.inverter_lib = []

        # Standard widgets
        description = 'Add PV system to energy system\n'\
                      'Method 1 - Default: data input: min. power & max. power, inverter power range. Random PV module, inverter and configuration is selected within the parameters. \n' \
                      'Method 2 - Advanced (only recommended for experienced users): data input: PV module, inverter and configuration. \n' \
                      'Method 3 - Profile: data input: path to PV energy production profile (csv-file).\n\n'
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setWordWrap(True)
        self.method_combo_l = QLabel()
        self.method_combo_l.setText('Method')
        self.method_combo = QComboBox()
        method = ['Default', 'Advanced', 'PV profile']
        self.method_combo.addItems(method)
        self.invest_l = QLabel()
        self.invest_l.setText('Investment cost (optional) [US$]')
        self.opm_l = QLabel()
        self.opm_l.setText('Operation and maintenance cost (optional) [US$/a]')
        self.invest = QLineEdit()
        self.opm = QLineEdit()

        # Method 1
        self.p_l = QLabel()
        self.p_l.setText('Power [kW]')
        self.p_min_l = QLabel()
        self.p_min_l.setText('Min. module power [W]')
        self.p_max_l = QLabel()
        self.p_max_l.setText('Max. module power [W]')
        self.inverter_range_l = QLabel()
        self.inverter_range_l.setText('Inverter power range [kW]')
        self.azimuth_l = QLabel()
        self.azimuth_l.setText('Surface azimuth [°]')
        self.tilt_l = QLabel()
        self.tilt_l.setText('Surface tilt [°]')
        self.p = QLineEdit()
        self.p_min = QLineEdit()
        self.p_max = QLineEdit()
        self.inverter_range = QLineEdit()
        self.azimuth = QLineEdit()
        self.tilt = QLineEdit()
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
        # Method 2
        self.module_l = QLabel()
        self.module_l.setText('PV module')
        self.inverter_l = QLabel()
        self.inverter_l.setText('Inverter')
        self.modules_string_l = QLabel()
        self.modules_string_l.setText('Modules per string')
        self.string_l = QLabel()
        self.string_l.setText('Strings per inverter')
        self.module = QComboBox()
        self.module.addItems(self.module_lib)
        self.inverter = QComboBox()
        self.inverter.addItems(self.inverter_lib)
        self.modules_per_string = QLineEdit()
        self.strings_per_inverter = QLineEdit()
        # Method 3
        self.profile_l = QLabel()
        self.profile_l.setText('PV profile path')
        self.profile = QLineEdit()
        self.browse = QPushButton('Browse')
        # Widget container
        self.method_1 = [self.p_l, self.p_min_l, self.p_max_l, self.inverter_range_l, self.azimuth_l, self.tilt_l,
                         self.p, self.p_min, self.p_max, self.inverter_range, self.azimuth, self.tilt]
        self.method_2 = [self.module_l, self.inverter_l, self.modules_string_l, self.string_l, self.azimuth_l, self.tilt_l,
                         self.module, self.inverter, self.modules_per_string, self.strings_per_inverter, self.azimuth, self.tilt]
        self.method_3 = [self.p_l, self.p, self.profile_l, self.profile, self.browse]

        # Connect function to ComboBox
        self.method_combo.currentIndexChanged.connect(self.simulation_method)
        self.browse.clicked.connect(self.get_profile)

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0, 1, 2)
        self.layout.addWidget(self.method_combo_l, 1, 0, Qt.AlignRight)
        self.layout.addWidget(self.method_combo, 1, 1, Qt.AlignTop)
        self.layout.addWidget(self.p_l, 2, 0, Qt.AlignRight)
        self.layout.addWidget(self.p, 2, 1, Qt.AlignTop)
        self.layout.addWidget(self.module_l, 2, 0, Qt.AlignRight)
        self.layout.addWidget(self.module, 2, 1, Qt.AlignTop)
        self.layout.addWidget(self.profile_l, 3, 0, Qt.AlignRight)
        self.layout.addWidget(self.profile, 3, 1, Qt.AlignTop)
        self.layout.addWidget(self.browse, 3, 2, Qt.AlignLeft)
        self.layout.addWidget(self.p_min_l, 3, 0, Qt.AlignRight)
        self.layout.addWidget(self.p_min, 3, 1, Qt.AlignTop)
        self.layout.addWidget(self.inverter_l, 3, 0, Qt.AlignRight)
        self.layout.addWidget(self.inverter, 3, 1, Qt.AlignTop)
        self.layout.addWidget(self.p_max_l, 4, 0, Qt.AlignRight)
        self.layout.addWidget(self.p_max, 4, 1, Qt.AlignTop)
        self.layout.addWidget(self.modules_string_l, 4, 0, Qt.AlignRight)
        self.layout.addWidget(self.modules_per_string, 4, 1, Qt.AlignTop)
        self.layout.addWidget(self.inverter_range_l, 5, 0, Qt.AlignRight)
        self.layout.addWidget(self.inverter_range, 5, 1, Qt.AlignTop)
        self.layout.addWidget(self.string_l, 5, 0, Qt.AlignRight)
        self.layout.addWidget(self.strings_per_inverter, 5, 1, Qt.AlignTop)
        self.layout.addWidget(self.azimuth_l, 6, 0, Qt.AlignRight)
        self.layout.addWidget(self.azimuth, 6, 1, Qt.AlignTop)
        self.layout.addWidget(self.tilt_l, 7, 0, Qt.AlignRight)
        self.layout.addWidget(self.tilt, 7, 1, Qt.AlignTop)
        self.layout.addWidget(self.invest_l, 8, 0, Qt.AlignRight)
        self.layout.addWidget(self.invest, 8, 1, Qt.AlignTop)
        self.layout.addWidget(self.opm_l, 9, 0, Qt.AlignRight)
        self.layout.addWidget(self.opm, 9, 1, Qt.AlignTop)
        self.layout.addWidget(self.overview, 10, 0, 1, 3)
        self.setLayout(self.layout)

        gui_func.show_widget(widget=self.method_2, show=False)
        gui_func.show_widget(widget=self.method_3, show=False)
        gui_func.show_widget(widget=self.method_1, show=True)

    def get_profile(self):
        """
        Open QFileDialog to select PV profile
        :return:
        """
        response = QFileDialog.getOpenFileName(parent=self,
                                               caption='Select PV profile',
                                               filter='Data file (*.csv)',
                                               directory=sys.path[1])
        pv_profile = response[0]
        self.profile.setText(pv_profile)

        return pv_profile

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


