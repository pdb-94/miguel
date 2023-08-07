import sys
import folium
import io
import datetime as dt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import gui.gui_func as gui_func
from gui.gui_table import Table


class EnergySystem(QWidget):
    """
    Tab Welcome Screen
    """

    def __init__(self):
        super().__init__()

        self.setFont(QFont('Calibri', 12))

        # Labels
        description = 'Base values for modeling the energy system'
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setWordWrap(True)
        self.project_name_l = QLabel()
        self.project_name_l.setText('Project name')
        self.start_time_l = QLabel()
        self.start_time_l.setText('Start time')
        self.end_time_l = QLabel()
        self.end_time_l.setText('End time')
        self.time_step_l = QLabel()
        self.time_step_l.setText('Time resolution [hh:mm]')
        self.tz_l = QLabel()
        self.tz_l.setText('Time zone')
        self.longitude_l = QLabel()
        self.longitude_l.setText('Longitude')
        self.latitude_l = QLabel()
        self.latitude_l.setText('Latitude')
        self.terrain_l = QLabel()
        self.terrain_l.setText('Terrain')
        self.d_rate_l = QLabel()
        self.d_rate_l.setText('Discount rate')
        self.lifetime_l = QLabel()
        self.lifetime_l.setText('System lifetime [a]')
        self.grid_l = QLabel()
        self.grid_l.setText('Grid connection')
        self.blackout_l = QLabel()
        self.blackout_l.setText('Blackout')
        self.blackout_data_l = QLabel()
        self.blackout_data_l.setText('Blackout data')
        self.electricity_price_l = QLabel()
        self.electricity_price_l.setText('Electricity price [US$/kWh]')
        self.diesel_price_l = QLabel()
        self.diesel_price_l.setText('Diesel price [US$/l]')
        self.co2_price_l = QLabel()
        self.co2_price_l.setText('Average CO2 price [US$/t]')
        self.feed_in_l = QLabel()
        self.feed_in_l.setText('Feed-in possible')
        self.pv_feed_l = QLabel()
        self.pv_feed_l.setText('PV feed-in tariff [US$/kWh]')
        self.wt_feed_l = QLabel()
        self.wt_feed_l.setText('Wind turbine feed-in tariff [US$/kWh]')
        self.co2_grid_l = QLabel()
        self.co2_grid_l.setText('Grid CO2 emissions [kg/kWh]')
        gui_func.set_alignment(widget=[self.project_name_l, self.time_step_l, self.end_time_l, self.start_time_l,
                                       self.d_rate_l, self.wt_feed_l, self.longitude_l, self.feed_in_l,
                                       self.blackout_l, self.blackout_data_l, self.grid_l, self.electricity_price_l,
                                       self.co2_grid_l, self.co2_price_l, self.pv_feed_l,  self.latitude_l,
                                       self.terrain_l, self.lifetime_l, self.diesel_price_l, self.tz_l],
                               alignment=Qt.AlignRight | Qt.AlignVCenter)
        # Edits
        self.project_name = QLineEdit()
        self.start_time = QDateTimeEdit()
        start_date = dt.datetime(year=2023, month=1, day=1)
        end_date = dt.datetime(year=2023, month=12, day=31)
        start_time = dt.time(hour=0, minute=0)
        end_time = dt.time(hour=23, minute=45)
        start_datetime = dt.datetime.combine(start_date, start_time)
        end_time = dt.datetime.combine(end_date, end_time)
        self.start_time.setDateTime(start_datetime)
        self.start_time.setCalendarPopup(True)
        self.end_time = QDateTimeEdit(end_time)
        self.end_time.setCalendarPopup(True)
        self.time_step = QComboBox()
        self.tz = QComboBox()
        tz = ['Etc/GMT+12', 'Etc/GMT+11', 'Etc/GMT+10', 'Etc/GMT+9', 'Etc/GMT+8', 'Etc/GMT+7', 'Etc/GMT+6', 'Etc/GMT+5',
              'Etc/GMT+4', 'Etc/GMT+3', 'Etc/GMT+2', 'Etc/GMT+1', 'Etc/GMT+0', 'Etc/GMT-1', 'Etc/GMT-2', 'Etc/GMT-3',
              'Etc/GMT-4', 'Etc/GMT-5', 'Etc/GMT-6', 'Etc/GMT-7', 'Etc/GMT-8', 'Etc/GMT-9', 'Etc/GMT-10', 'Etc/GMT-11',
              'Etc/GMT-12']
        self.tz.addItems(tz)
        self.tz.setCurrentIndex(12)
        gui_func.add_combo(widget=self.time_step, name=['00:15', '01:00'])
        gui_func.change_combo_index(combo=[self.time_step], index=[0])
        self.longitude = QLineEdit()
        self.latitude = QLineEdit()
        self.terrain = QComboBox()
        terrain = ['Water surfaces',
                   'Open terrain with smooth surface, e.g., concrete, airport runways, mowed grass',
                   'Open agricultural terrain without fences or hedges, possibly with widely scattered houses, '
                   'very rolling hills',
                   'Agricultural terrain with some houses and 8 meter high hedges at a distance of approx. 1250 meters',
                   'Agricultural terrain with many houses, bushes, plants or 8 meter high hedges at a distance of '
                   'approx. 250 meters',
                   'Villages, small towns, agricultural buildings with many or high hedges, woods and very rough and '
                   'uneven terrain',
                   'Larger cities with tall buildings', 'Large cities, tall buildings, skyscrapers']
        gui_func.add_combo(widget=self.terrain, name=terrain)
        self.d_rate = QLineEdit('0.03')
        self.lifetime = QLineEdit('20')
        self.grid = QCheckBox()
        self.grid.setChecked(True)
        self.blackout = QCheckBox()
        self.blackout.setChecked(False)
        self.blackout_data = QLineEdit()
        self.blackout_data.setDisabled(True)
        self.electricity_price = QLineEdit()
        self.diesel_price = QLineEdit()
        self.co2_price = QLineEdit()
        self.feed_in = QCheckBox()
        self.feed_in.setChecked(False)
        self.pv_feed = QLineEdit()
        self.pv_feed.setDisabled(True)
        self.wt_feed = QLineEdit()
        self.wt_feed.setDisabled(True)
        self.co2_grid = QLineEdit()
        # Map
        self.map = folium.Map(location=[50.9375, 6.9603], zoom_start=12)
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.map_viewer = QWebEngineView()
        self.map_viewer.setHtml(data.getvalue().decode())
        self.map_viewer.resize(640, 480)

        # Functions
        self.feed_in.stateChanged.connect(self.feed_in_status)
        self.grid.stateChanged.connect(self.grid_connection_status)
        self.blackout.stateChanged.connect(self.blackout_status)
        self.time_step.activated.connect(self.change_end_time)

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.description, 0, 0, 1, 6)
        self.layout.addWidget(self.project_name_l, 1, 0)
        self.layout.addWidget(self.project_name, 1, 1, 1, 5)
        self.layout.addWidget(self.start_time_l, 2, 0)
        self.layout.addWidget(self.start_time, 2, 1, 1, 5)
        self.layout.addWidget(self.end_time_l, 3, 0)
        self.layout.addWidget(self.end_time, 3, 1, 1, 5)
        self.layout.addWidget(self.time_step_l, 4, 0)
        self.layout.addWidget(self.time_step, 4, 1)
        self.layout.addWidget(self.tz_l, 4, 2)
        self.layout.addWidget(self.tz, 4, 3, 1, 3)
        self.layout.addWidget(self.latitude_l, 5, 0)
        self.layout.addWidget(self.latitude, 5, 1)
        self.layout.addWidget(self.longitude_l, 5, 2)
        self.layout.addWidget(self.longitude, 5, 3)
        self.layout.addWidget(self.terrain_l, 6, 0)
        self.layout.addWidget(self.terrain, 6, 1, 1, 5)
        self.layout.addWidget(self.d_rate_l, 7, 0)
        self.layout.addWidget(self.d_rate, 7, 1, 1, 5)
        self.layout.addWidget(self.lifetime_l, 8, 0)
        self.layout.addWidget(self.lifetime, 8, 1, 1, 5)
        self.layout.addWidget(self.grid_l, 9, 0)
        self.layout.addWidget(self.grid, 9, 1, 1, 5)
        self.layout.addWidget(self.blackout_l, 10, 0)
        self.layout.addWidget(self.blackout, 10, 1)
        self.layout.addWidget(self.blackout_data_l, 10, 2)
        self.layout.addWidget(self.blackout_data, 10, 3, 1, 3)
        self.layout.addWidget(self.electricity_price_l, 11, 0)
        self.layout.addWidget(self.electricity_price, 11, 1)
        self.layout.addWidget(self.diesel_price_l, 11, 2)
        self.layout.addWidget(self.diesel_price, 11, 3, 1, 3)
        self.layout.addWidget(self.co2_price_l, 12, 0)
        self.layout.addWidget(self.co2_price, 12, 1, 1, 5)
        self.layout.addWidget(self.feed_in_l, 13, 0)
        self.layout.addWidget(self.feed_in, 13, 1, 1, 5)
        self.layout.addWidget(self.pv_feed_l, 14, 0)
        self.layout.addWidget(self.pv_feed, 14, 1)
        self.layout.addWidget(self.wt_feed_l, 14, 2)
        self.layout.addWidget(self.wt_feed, 14, 3, 1, 3)
        self.layout.addWidget(self.co2_grid_l, 15, 0)
        self.layout.addWidget(self.co2_grid, 15, 1, 1, 5)
        self.layout.addWidget(self.map_viewer, 16, 0, 1, 6)
        self.setLayout(self.layout)

    def grid_connection_status(self):
        """
        Check status of grid connection (self.grid) and en-, disable widgets
        :return: None
        """
        if self.grid.isChecked():
            gui_func.enable_widget(widget=[self.feed_in, self.blackout, self.co2_grid], enable=True)
            if self.feed_in.isChecked():
                gui_func.enable_widget(widget=[self.electricity_price, self.pv_feed, self.wt_feed],
                                       enable=True)
            else:
                gui_func.enable_widget(widget=[self.electricity_price, self.feed_in],
                                       enable=True)
            if self.blackout.isChecked():
                gui_func.enable_widget(widget=[self.blackout_data],
                                       enable=True)
            else:
                gui_func.enable_widget(widget=[self.blackout_data],
                                       enable=False)
        else:
            self.blackout.setChecked(False)
            self.feed_in.setChecked(False)
            gui_func.enable_widget(widget=[self.electricity_price, self.feed_in, self.pv_feed, self.wt_feed,
                                           self.blackout, self.blackout_data, self.co2_grid],
                                   enable=False)

    def feed_in_status(self):
        """
        Check status of feed-in (self.feed_in) and en-, disable widgets
        :return: None
        """
        if self.feed_in.isChecked():
            gui_func.enable_widget(widget=[self.pv_feed, self.wt_feed], enable=True)
        else:
            gui_func.enable_widget(widget=[self.pv_feed, self.wt_feed], enable=False)

    def blackout_status(self):
        """
        Check if grid has blackouts
        :return: None
        """
        if self.blackout.isChecked():
            self.blackout_data.setEnabled(True)
        else:
            self.blackout_data.setEnabled(False)

    def update_map(self, latitude, longitude, name):
        """
        :param latitude: float
        :param longitude: float
        :param name: str
            project name
        :return: None
        """
        self.map = folium.Map(location=[latitude, longitude], zoom_start=12)
        data = io.BytesIO()
        tooltip = name
        folium.Marker(location=[latitude, longitude],
                      popup=f'<i> {name} <i>',
                      tooltip=tooltip,
                      icon=folium.Icon(color='blue', icon='info-sign')).add_to(self.map)
        self.map.save(data, close_file=False)
        self.map_viewer = QWebEngineView()
        self.map_viewer.setHtml(data.getvalue().decode())
        self.map_viewer.resize(640, 480)
        self.layout.addWidget(self.map_viewer, 16, 0, 1, 6)

    def change_end_time(self):
        """
        Change end time depending on time resolution
        :return: None
        """
        start_time = dt.datetime.strptime(self.start_time.text(), '%d.%m.%Y %H:%M')
        start_year = start_time.date().year
        if self.time_step.currentIndex() == 0:
            end_time = dt.datetime.combine(dt.date(year=start_year, month=12, day=31), dt.time(hour=23, minute=45))
            self.end_time.setDateTime(end_time)
        else:
            end_time = dt.datetime.combine(dt.date(year=start_year, month=12, day=31), dt.time(hour=23, minute=0))
            self.end_time.setDateTime(end_time)

