import sys
import os
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from tzfpy import get_tz
from environment import Environment
import gui_func as gui_func
from gui.projectsetup import ProjectSetup
from gui.energysystem import EnergySystem
from gui.weatherdata import WeatherData
from gui.systemconfiguration import SystemConfig
from gui.loadprofile import LoadProfile


class TabWidget(QWidget):
    """
    Class to create the main Window Frame of the LPC GUI
    """

    def __init__(self):
        super().__init__()
        self.root = sys.path[1]

        # Environment Container
        self.env = None
        self.setStyleSheet("""QWidget {font: Calibri}""")

        # Set up TabWidget
        self.tabs = QTabWidget()
        self.setFont(QFont('Calibri'))
        self.tab_title = ['Get started',
                          'Energy system',
                          'Weather data',
                          'Load profile',
                          'System configuration']
        self.tab_classes = [ProjectSetup,
                            EnergySystem,
                            WeatherData,
                            LoadProfile,
                            SystemConfig]
        enabled = [True, True, False, False, False]

        for i in range(len(self.tab_classes)):
            self.tabs.addTab(self.tab_classes[i](), self.tab_title[i])
            self.tabs.widget(i).setEnabled(enabled[i])

        # Set up Pushbutton
        self.delete_btn = QPushButton('Delete')
        self.save_btn = QPushButton('Save')
        self.return_btn = QPushButton('Return')
        self.next_btn = QPushButton('Start')
        self.next_btn.setFixedSize(QSize(150, 40))
        gui_func.enable_widget(widget=[self.save_btn, self.return_btn], enable=False)
        gui_func.show_widget(widget=[self.save_btn, self.return_btn, self.delete_btn], show=False)
        # Functions
        self.tabs.currentChanged.connect(self.tab_changed)
        self.next_btn.clicked.connect(self.next_tab)
        self.return_btn.clicked.connect(self.previous_tab)
        self.save_btn.clicked.connect(self.save)

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.tabs, 0, 0, 4, 1)
        self.layout.addWidget(self.delete_btn, 0, 1, Qt.AlignBottom)
        self.layout.addWidget(self.save_btn, 1, 1)
        self.layout.addWidget(self.return_btn, 2, 1)
        self.layout.addWidget(self.next_btn, 3, 1)
        self.setLayout(self.layout)

        self.setGeometry(200, 200, 1300, 800)
        self.setWindowTitle('Micro Grid User Energy Tool Library')
        window_icon = QIcon(self.root + '/documentation/MiGUEL_icon.png')
        self.setWindowIcon(window_icon)
        self.show()

    def next_tab(self):
        """
        :return: None
        """
        index = self.tabs.currentIndex()
        self.tabs.setCurrentIndex(index + 1)

    def previous_tab(self):
        """
        Show previous tab
        :return: None
        """
        # Get current Index from TabWidget and set current Index -=1
        index = self.tabs.currentIndex()
        self.tabs.setCurrentIndex(index - 1)

    def tab_changed(self):
        """
        Prepare tabs to default look (change texts, show/hide/enable/disable/clear widgets, reset ComboBox)
        :return: None
        """
        index = self.tabs.currentIndex()
        if index == 0:
            # Tab Start
            # Change widget text, show and enable widgets
            gui_func.change_widget_text(widget=[self.next_btn], text=['Start'])
            gui_func.show_widget(widget=[self.save_btn, self.return_btn, self.delete_btn], show=False)
            gui_func.enable_widget(widget=[self.next_btn], enable=True)
        elif index == 1:
            # Tab Hospital
            # Change widget text, show and enable/disable widgets
            gui_func.change_widget_text(widget=[self.next_btn], text=['Next'])
            gui_func.show_widget(widget=[self.save_btn, self.return_btn, self.delete_btn], show=True)
            gui_func.enable_widget(widget=[self.save_btn, self.return_btn], enable=True)

    def save(self):
        """
        Define save function based on tab index
        :return:
        """
        index = self.tabs.currentIndex()
        tabs = self.tabs.widget
        tab = tabs(index)
        if index == 1:
            # Environment
            self.create_env()
            # Plot weather data
            self.plot_monthly_weather_data()
            # Reset widgets
            gui_func.clear_widget(widget=[tab.project_name, tab.latitude, tab.longitude, tab.altitude,
                                          tab.electricity_price, tab.co2_price, tab.wt_feed, tab.pv_feed,
                                          tab.co2_grid])
            tab.blackout.setChecked(False)
            tab.feed_in.setChecked(False)
            tab.grid.setChecked(True)
            # Enable widgets
            gui_func.enable_widget(widget=[tabs(2), tabs(3)], enable=True)
        elif index == 3:
            # Load profile
            self.gui_add_load_profile()
            # Clear widgets
            gui_func.clear_widget(widget=[tab.consumption, tab.load_profile])

    def create_env(self):
        """
        Create Environment from User Input
        :return:
        """
        tab = self.tabs.widget(1)
        # Collect input parameters
        name = tab.project_name.text()
        longitude = float(tab.longitude.text())
        latitude = float(tab.latitude.text())
        altitude = float(tab.altitude.text())
        terrain = tab.terrain.currentText()
        start_time = tab.start_time.text()
        end_time = tab.end_time.text()
        time_step = tab.time_step.currentText()
        d_rate = float(tab.d_rate.text())
        lifetime = int(tab.lifetime.text())
        electricity_price = float(tab.electricity_price.text())
        co2_price = float(tab.co2_price.text())
        grid_connection = tab.grid.isChecked()
        blackout = tab.blackout.isChecked()
        if blackout:
            blackout_data = tab.blackout_data.text()
        else:
            blackout_data = None
        feed_in = tab.feed_in.isChecked()
        if feed_in:
            pv_feed_in = float(tab.pv_feed.text())
            wt_feed_in = float(tab.wt_feed.text())
        else:
            pv_feed_in = None
            wt_feed_in = None
        # Location
        location = {'longitude': longitude,
                    'latitude': latitude,
                    'altitude': altitude,
                    'terrain': terrain}
        # Time
        timezone = get_tz(location['latitude'], location['longitude'])
        time_data = gui_func.convert_datetime(start=start_time, end=end_time, step=time_step)
        time = {'start': time_data[0], 'end': time_data[1], 'step': time_data[2], 'timzone': timezone}
        # Economy
        economy = {'d_rate': d_rate,
                   'lifetime': lifetime,
                   'electricity_price': electricity_price,
                   'co2_price': co2_price,
                   'pv_feed_in': pv_feed_in,
                   'wt_feed_in': wt_feed_in,
                   'currency': 'US$'}
        # Ecological
        co2_grid = tab.co2_grid.text()
        if co2_grid is not None:
            co2_grid = float(co2_grid)
        ecology = {'co2_diesel': 0.2665, 'co2_grid': co2_grid}
        # Create Environment
        self.env = Environment(name=name,
                               time=time,
                               location=location,
                               economy=economy,
                               ecology=ecology,
                               grid_connection=grid_connection,
                               blackout=blackout,
                               blackout_data=blackout_data,
                               feed_in=feed_in,
                               csv_decimal=',',
                               csv_sep=';')
        # Update folium map
        tab.update_map(latitude=location['latitude'], longitude=location['longitude'], name=name)

    def gui_add_load_profile(self):
        """
        Create load profile
        :return:
        """
        tab = self.tabs.widget(3)
        annual_consumption = tab.consumption.text()
        load_profile_path = tab.load_profile.text()
        load_profile_path = load_profile_path.replace('\\', '/')
        if annual_consumption != "":
            annual_consumption = float(annual_consumption)
        if load_profile_path != "":
            annual_consumption = None
        else:
            load_profile_path = None
        if isinstance(self.env, Environment):
            self.env.add_load(annual_consumption=annual_consumption,
                              load_profile=load_profile_path)
            tab.adjust_plot(time_series=self.env.time_series,
                            df=self.env.df['P_Res [W]'])

    def plot_monthly_weather_data(self):
        """

        :return:
        """
        wind_data = self.env.monthly_weather_data[['wind_speed', 'wind_direction']]
        self.create_wind_plot(name='wind_data',
                              data_1=wind_data['wind_speed'],
                              data_2=wind_data['wind_direction'])
        gui_func.create_pixmap(path=f'{self.root}/gui/images/wind_data.png',
                               widget=self.tabs.widget(2).wind_plot,
                               w=540,
                               h=400)
        solar_data = self.env.monthly_weather_data[['ghi', 'dhi', 'dni']]
        self.create_solar_plot(name='solar_data',
                               data=solar_data)
        gui_func.create_pixmap(path=f'{self.root}/gui/images/solar_data.png',
                               widget=self.tabs.widget(2).solar_plot,
                               w=540,
                               h=400)

    def create_wind_plot(self, name, data_1, data_2):
        """
        Create monthly wind data plot
        :param name:
        :param data_1:
        :param data_2:
        :return:
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('Month')
        fig.legend(['wind speed', 'wind direction'])
        ax2 = ax.twinx()
        data_1.plot(kind='bar', color='lightgreen', ax=ax, width=0.2, position=1, label='Wind speed')
        data_2.plot(kind='bar', color='steelblue', ax=ax2, width=0.2, position=0, label='Wind direction')
        ax.set_ylabel(ylabel='wind speed [m/s]')
        ax2.set_ylabel(ylabel='wind direction [°]')
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        fig.tight_layout()
        plt.savefig(f'{self.root}/gui/images/{name}.png')

    def create_solar_plot(self, name, data):
        """

        :param name:
        :param data:
        :return:
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('Month')
        data['ghi'].plot(kind='bar', color='yellow', ax=ax, width=0.2, position=1, label='Global horizontal irradiation')
        data['dhi'].plot(kind='bar', color='gold', ax=ax, width=0.2, position=0, label='Direct horizontal irradiation')
        data['dni'].plot(kind='bar', color='darkorange', ax=ax, width=0.2, position=2, label='Direct normal irradiation')
        ax.set_ylabel(ylabel='Solar irradiation [W/m²]')
        plt.legend(loc='upper left')
        fig.tight_layout()
        plt.savefig(f'{self.root}/gui/images/{name}.png')

    def plot_load_profile(self):
        """

        :return:
        """
        data = self.env.load[0].load_profile
        self.create_load_profile_plot(name='load_profile',
                                      data=data)
        gui_func.create_pixmap(path=f'{self.root}/gui/images/load_profile.png',
                               widget=self.tabs.widget(3).load_profile_plot,
                               w=1260,
                               h=540)

    def create_load_profile_plot(self, name, data):
        """

        :param name:
        :param data:
        :return:
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('Time hh:mm')
        data['P [W]'].plot(kind='line', color='blue', ax=ax, label='Load [W]')
        ax.set_ylabel(ylabel='P [W]')
        plt.legend(loc='upper left')
        fig.tight_layout()
        plt.savefig(f'{self.root}/gui/images/{name}.png')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont('Calibri'))
    window = TabWidget()
    sys.exit(app.exec())
