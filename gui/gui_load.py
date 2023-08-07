import sys
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
import gui.gui_func as gui_func
from gui.gui_plot import Plot


class LoadProfile(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        # Header
        self.setFont(QFont('Calibri', 12))
        description = 'Add a load profile to the energy system\n' \
                      'Method 1 - Reference load profile: choose reference load profile from list. Enter annual electricity consumption [kWh/a] to scale load profile.\n' \
                      'Method 2 - Individual load profile: provide individual load profile as a csv-file. Enter load profile file path.\n\n'
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setWordWrap(True)
        # Content
        self.method_l = QLabel()
        self.method_l.setText('Method')
        self.method_combo = QComboBox()
        method = ['Reference load profile', 'Load profile from csv']
        self.method_combo.addItems(method)
        self.consumption_l = QLabel()
        self.consumption_l.setText('Annual electricity demand [kWh]')
        self.ref_profile_l = QLabel()
        self.ref_profile_l.setText('Reference load profile')
        self.load_profile_l = QLabel()
        self.load_profile_l.setText('Load profile path')
        self.consumption = QLineEdit()
        self.ref_profile = QComboBox()
        items = ['Hospital Ghana',
                 'H0 - Household',
                 'G0 - General trade/business/commerce',
                 'G1 - Business on weekdays 8 a.m. - 6 p.m.',
                 'G2 - Businesses with heavy to predominant consumption in the evening hours',
                 'G3 - Continuous business',
                 'G4 - Shop/barber shop',
                 'G5 - Bakery',
                 'G6 - Weekend operation',
                 'L0 - General farms',
                 'L1 - Farms with dairy farming/part-time livestock farming',
                 'L2 - Other farms']
        self.ref_profile.addItems(items)
        self.load_profile = QLineEdit()
        self.browse = QPushButton('Browse')
        # Methods
        self.method_1 = [self.consumption, self.consumption_l, self.ref_profile_l, self.ref_profile]
        self.method_2 = [self.load_profile_l, self.load_profile, self.browse]
        # Set up Plot
        self.plot = Plot()
        self.toolbar = self.toolbar = NavigationToolbar(self.plot, self)

        # Connect functions
        self.load_profile_path = self.browse.clicked.connect(self.get_load_profile)
        self.method_combo.currentIndexChanged.connect(self.simulation_method)

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0, 1, 3, Qt.AlignVCenter)
        self.layout.addWidget(self.method_l, 1, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.layout.addWidget(self.method_combo, 1, 1, 1, 2, Qt.AlignVCenter)
        self.layout.addWidget(self.consumption_l, 2, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.layout.addWidget(self.consumption, 2, 1, Qt.AlignVCenter)
        self.layout.addWidget(self.ref_profile_l, 3, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.layout.addWidget(self.ref_profile, 3, 1, Qt.AlignVCenter)
        self.layout.addWidget(self.load_profile_l, 2, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.layout.addWidget(self.load_profile, 2, 1, Qt.AlignVCenter)
        self.layout.addWidget(self.browse, 2, 2, Qt.AlignVCenter | Qt.AlignLeft)
        self.layout.addWidget(self.toolbar, 4, 0, 1, 3, Qt.AlignVCenter)
        self.layout.addWidget(self.plot, 5, 0, 1, 3, Qt.AlignVCenter)
        self.setLayout(self.layout)

        gui_func.show_widget(widget=self.method_2, show=False)

    def simulation_method(self):
        index = self.method_combo.currentIndex()
        if index == 0:
            gui_func.show_widget(widget=self.method_2, show=False)
            gui_func.show_widget(widget=self.method_1, show=True)
        else:
            gui_func.show_widget(widget=self.method_2, show=True)
            gui_func.show_widget(widget=self.method_1, show=False)

    def get_load_profile(self):
        """

        :return:
        """
        response = QFileDialog.getOpenFileName(parent=self,
                                               caption='Select load profile',
                                               filter='Data file (*.csv)',
                                               directory=sys.path[1])
        load_profile_path = response[0]
        self.load_profile.setText(load_profile_path)

        return load_profile_path

    def adjust_plot(self, df: pd.Series, time_series: pd.Series):
        """
        Plot DataFrame based on parameter load_profile
        :param time_series: pd.Series
            environment time_series
        :param df: pd.Series
            load_df
        :return: None
        """
        # Create Widgets
        self.plot = Plot(df=df,
                         time_series=time_series,
                         width=5, height=12, dpi=150)
        self.toolbar = NavigationToolbar(self.plot, self)
        # Add Widgets to Layout
        self.layout.addWidget(self.toolbar, 4, 0, 1, 3)
        self.layout.addWidget(self.plot, 5, 0, 1, 3)

    def clear_plot(self):
        """
        Reset plot
        :return: None
        """
        self.plot = Plot()
        self.toolbar = NavigationToolbar(self.plot, self)
        # Add Widgets to Layout
        self.layout.addWidget(self.toolbar, 4, 0, 1, 3)
        self.layout.addWidget(self.plot, 5, 0, 1, 3)
