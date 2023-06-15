import sys
import folium
import io
import datetime as dt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import gui_func as gui_func


class WT(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        # windpowerib parameters
        self.turbine_lib = []

        # Standard widgets
        self.setFont(QFont('Calibri', 11))
        description = 'Add wind turbine to energy system. ' \
                      '\nMethod 1 - Default: data input: min. power & max. power. Random wind turbin is selected within the power range \n' \
                      'Method 2 - Advanced (only recommended for experienced users): data input: wind turbine and hub height \n' \
                      'Method 3 - Profile: data input: path to wind turbine energy production profile (csv-file)'
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
        # Widget container
        self.method_1 = [self.p_min_l, self.p_max_l, self.p_min, self.p_max]
        self.method_2 = [self.p_l, self.turbine_l, self.p, self.turbine, self.height_l, self.height]
        self.method_3 = [self.p_l, self.p, self.profile_l, self.profile]

        self.method_combo.currentIndexChanged.connect(self.simulation_method)

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0, 1, 2)
        self.layout.addWidget(self.method_combo_l, 1, 0)
        self.layout.addWidget(self.method_combo, 1, 1)
        self.layout.addWidget(self.p_min_l, 2, 0)
        self.layout.addWidget(self.p_min, 2, 1)
        self.layout.addWidget(self.p_l, 2, 0)
        self.layout.addWidget(self.p, 2, 1)
        self.layout.addWidget(self.profile_l, 3, 0)
        self.layout.addWidget(self.profile, 3, 1)
        self.layout.addWidget(self.p_max_l, 3, 0)
        self.layout.addWidget(self.p_max, 3, 1)
        self.layout.addWidget(self.turbine_l, 3, 0)
        self.layout.addWidget(self.turbine, 3, 1)
        self.layout.addWidget(self.height_l, 4, 0)
        self.layout.addWidget(self.height, 4, 1)
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
