import sys
import folium
import io
import datetime as dt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import gui_func as gui_func


class PV(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        self.setFont(QFont('Calibri', 11))

        # pvlib parameters
        self.module_lib = []
        self.inverter_lib = []

        # Standard widgets
        description = 'Add PV system to energy system. ' \
                      '\nMethod 1 - Default: data input: min. power & max. power, inverter power range. Random PV module, inverter and configuration is selected within the parameters \n' \
                      'Method 2 - Advanced (only recommended for experienced users): data input: PV module, inverter and configuration \n' \
                      'Method 3 - Profile: data input: path to PV energy production profile (csv-file)'
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
        self.modules_string = QLineEdit()
        self.string = QLineEdit()
        # Method 3
        self.profile_l = QLabel()
        self.profile_l.setText('PV profile path')
        self.profile = QLineEdit()
        # Widget container
        self.method_1 = [self.p_l, self.p_min_l, self.p_max_l, self.inverter_range_l, self.azimuth_l, self.tilt_l,
                         self.p, self.p_min, self.p_max, self.inverter_range, self.azimuth, self.tilt]
        self.method_2 = [self.module_l, self.inverter_l, self.modules_string_l, self.string_l, self.azimuth_l, self.tilt_l,
                         self.module, self.inverter, self.modules_string, self.string, self.azimuth, self.tilt]
        self.method_3 = [self.p_l, self.p, self.profile_l, self.profile]


        self.method_combo.currentIndexChanged.connect(self.simulation_method)

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0, 1, 2)
        self.layout.addWidget(self.method_combo_l, 1, 0)
        self.layout.addWidget(self.method_combo, 1, 1)
        self.layout.addWidget(self.p_l, 2, 0)
        self.layout.addWidget(self.p, 2, 1)
        self.layout.addWidget(self.module_l, 2, 0)
        self.layout.addWidget(self.module, 2, 1)
        self.layout.addWidget(self.profile_l, 3, 0)
        self.layout.addWidget(self.profile, 3, 1)
        self.layout.addWidget(self.p_min_l, 3, 0)
        self.layout.addWidget(self.p_min, 3, 1)
        self.layout.addWidget(self.inverter_l, 3, 0)
        self.layout.addWidget(self.inverter, 3, 1)
        self.layout.addWidget(self.p_max_l, 4, 0)
        self.layout.addWidget(self.p_max, 4, 1)
        self.layout.addWidget(self.modules_string_l, 4, 0)
        self.layout.addWidget(self.modules_string, 4, 1)
        self.layout.addWidget(self.inverter_range_l, 5, 0)
        self.layout.addWidget(self.inverter_range, 5, 1)
        self.layout.addWidget(self.string_l, 5, 0)
        self.layout.addWidget(self.string, 5, 1)
        self.layout.addWidget(self.azimuth_l, 6, 0)
        self.layout.addWidget(self.azimuth, 6, 1)
        self.layout.addWidget(self.tilt_l, 7, 0)
        self.layout.addWidget(self.tilt, 7, 1)
        self.layout.addWidget(self.invest_l, 8, 0)
        self.layout.addWidget(self.invest, 8, 1)
        self.layout.addWidget(self.opm_l, 9, 0)
        self.layout.addWidget(self.opm, 9, 1)
        self.setLayout(self.layout)

        gui_func.show_widget(widget=self.method_2, show=False)
        gui_func.show_widget(widget=self.method_3, show=False)
        gui_func.show_widget(widget=self.method_1, show=True)

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


