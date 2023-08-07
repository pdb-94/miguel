import sys
import pandas as pd
import threading
from global_land_mask import globe
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from tzfpy import get_tz
from environment import Environment
from operation import Operator
from evaluation import Evaluation
from report.report import Report
from components.pv import PV
from components.windturbine import WindTurbine
from components.dieselgenerator import DieselGenerator
import gui.gui_func as gui_func
from gui.gui_projectsetup import ProjectSetup
from gui.gui_environment import EnergySystem
from gui.gui_weatherdata import WeatherData
from gui.gui_load import LoadProfile
from gui.gui_pv import Photovoltaic
from gui.gui_wt import WT
from gui.gui_dg import DG
from gui.gui_storage import EnergyStorage
from gui.gui_dispatch import Dispatch
from gui.gui_evaluation import EvaluateSystem


class TabWidget(QWidget):
    """
    Class to create the main Window Frame of the LPC GUI
    """

    def __init__(self):
        super().__init__()
        self.root = sys.path[1]

        # Class containers
        self.env = None
        self.operator = None
        self.evaluation = None
        self.report = None
        # Style sheet
        self.setStyleSheet("""QWidget {font: Calibri}""")

        # Set up TabWidget
        self.tabs = QTabWidget()
        self.setFont(QFont('Calibri'))
        self.tab_title = ['Get started',
                          'Energy system',
                          'Weather data',
                          'Load profile',
                          'PV system',
                          'Wind turbine',
                          'Diesel generator',
                          'Energy storage',
                          'Dispatch',
                          'System evaluation']
        self.tab_classes = [ProjectSetup,
                            EnergySystem,
                            WeatherData,
                            LoadProfile,
                            Photovoltaic,
                            WT,
                            DG,
                            EnergyStorage,
                            Dispatch,
                            EvaluateSystem]
        # Add tabs to TabWidget and disable widgets
        enabled = [True, True, False, False, False, False, False, False, False, False]
        for count, tab in enumerate(self.tab_classes, start=0):
            self.tabs.addTab(tab(), self.tab_title[count])
            # self.tabs.widget(count).setEnabled(enabled[count])

        # Set up Pushbutton
        self.delete_btn = QPushButton('Delete')
        self.delete_btn.setFixedSize(QSize(220, 40))
        self.save_btn = QPushButton('Save')
        self.save_btn.setFixedSize(QSize(220, 40))
        self.return_btn = QPushButton('Return')
        self.return_btn.setFixedSize(QSize(220, 40))
        self.next_btn = QPushButton('Start')
        self.next_btn.setFixedSize(QSize(220, 40))
        gui_func.enable_widget(widget=[self.save_btn, self.return_btn, self.delete_btn], enable=False)
        # Functions
        self.tabs.currentChanged.connect(self.tab_changed)
        self.next_btn.clicked.connect(self.next_tab)
        self.return_btn.clicked.connect(self.previous_tab)
        self.save_btn.clicked.connect(self.save)
        self.delete_btn.clicked.connect(self.delete)

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.tabs, 0, 0, 4, 1)
        self.layout.addWidget(self.delete_btn, 1, 1, Qt.AlignBottom)
        self.layout.addWidget(self.save_btn, 2, 1)
        self.layout.addWidget(self.return_btn, 3, 1)
        self.layout.addWidget(self.next_btn, 4, 1)
        self.setLayout(self.layout)

        # Geometry
        self.screen_geometry = QDesktopWidget().screenGeometry(-1)
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        self.scale = 1.5
        self.setGeometry(200, 200, int(self.screen_width / self.scale), int(self.screen_height / self.scale))
        self.setWindowTitle('Micro Grid User Energy Tool Library')
        window_icon = QIcon(f'{self.root}/documentation/MiGUEL_icon.png')
        self.setWindowIcon(window_icon)
        self.show()

    def next_tab(self):
        """
        Show next tab
        :return: None
        """
        index = self.tabs.currentIndex()
        if index == 9:
            self.close()
        else:
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
            gui_func.enable_widget(widget=[self.save_btn, self.return_btn, self.delete_btn], enable=False)
            gui_func.enable_widget(widget=[self.next_btn], enable=True)
            gui_func.change_widget_text(widget=[self.save_btn, self.delete_btn, self.next_btn, self.return_btn],
                                        text=['Save', 'Delete', 'Start', 'Return'])
        elif index == 1:
            # Tab environment
            gui_func.enable_widget(widget=[self.save_btn, self.next_btn, self.return_btn], enable=True)
            gui_func.enable_widget(widget=[self.delete_btn], enable=False)
            gui_func.change_widget_text(widget=[self.save_btn, self.delete_btn, self.next_btn, self.return_btn],
                                        text=['Save', 'Delete', 'Next', 'Return'])
        elif index == 2:
            # Tab weather data
            gui_func.enable_widget(widget=[self.delete_btn, self.save_btn],
                                   enable=False)
            gui_func.change_widget_text(widget=[self.save_btn, self.delete_btn, self.next_btn, self.return_btn],
                                        text=['Save', 'Delete', 'Next', 'Return'])
        elif index == 3:
            # Tab load profile
            gui_func.enable_widget(widget=[self.delete_btn],
                                   enable=False)
            gui_func.enable_widget(widget=[self.save_btn, self.next_btn, self.return_btn],
                                   enable=True)
            gui_func.change_widget_text(widget=[self.save_btn, self.delete_btn, self.next_btn, self.return_btn],
                                        text=['Save', 'Delete', 'Next', 'Return'])
        elif index == 8:
            # Tab dispatch
            gui_func.change_widget_text(widget=[self.save_btn, self.delete_btn, self.next_btn, self.return_btn],
                                        text=['Run dispatch', 'Delete', 'Next', 'Return'])
            gui_func.enable_widget(widget=[self.save_btn, self.return_btn, self.next_btn],
                                   enable=True)
            gui_func.enable_widget(widget=[self.delete_btn],
                                   enable=False)
            gui_func.update_listview(tab=self.tabs.widget(8),
                                     df=self.tabs.widget(8).component_df)
        elif index == 9:
            # Tab evaluation
            gui_func.change_widget_text(widget=[self.save_btn, self.delete_btn, self.next_btn, self.return_btn],
                                        text=['Export', 'Delete', 'Close', 'Return'])
            gui_func.enable_widget(widget=[self.return_btn],
                                   enable=True)
            # Enable tab if dispatch has been finished
            if self.operator is not None:
                gui_func.enable_widget(widget=[self.save_btn, self.next_btn],
                                       enable=True)
                gui_func.enable_widget(widget=[self.delete_btn],
                                       enable=False)
            else:
                gui_func.enable_widget(widget=[self.save_btn, self.next_btn, self.delete_btn],
                                       enable=False)
        else:
            # Change widget text, show and enable/disable widgets
            gui_func.change_widget_text(widget=[self.save_btn, self.delete_btn, self.next_btn, self.return_btn],
                                        text=['Save', 'Delete', 'Next', 'Return'])
            gui_func.show_widget(widget=[self.save_btn, self.return_btn, self.delete_btn, self.next_btn],
                                 show=True)
            gui_func.enable_widget(widget=[self.save_btn, self.return_btn, self.delete_btn],
                                   enable=True)

    def delete(self):
        """
        Delete components from environment
        :return: None
        """
        index = self.tabs.currentIndex()
        tabs = self.tabs.widget
        tab = tabs(index)
        if index == 3:
            if self.env.load is not None:
                # Delete load, remove column from df, clear plot
                self.env.load = None
                self.env.df = self.env.df.drop(columns=['P_Res [W]'])
                tab.clear_plot()
        if index == 4:
            component = self.env.pv
        elif index == 5:
            component = self.env.wind_turbine
        elif index == 6:
            component = self.env.diesel_generator
        elif index == 7:
            component = self.env.storage
        else:
            return
        # Check if component has been created
        if len(component) > 0:
            row = tab.overview.currentIndex().row()
            # Check if component has been selected
            if row != -1:
                name = component[row].name
                comp = component[row]
                # Delete item from environment
                if isinstance(comp, PV):
                    self.env.df['PV total power [W]'] \
                        = self.env.df['PV total power [W]'] - self.env.df[f'{name}: P [W]']
                    self.env.re_supply.remove(comp)
                    self.env.supply_components.remove(comp)
                elif isinstance(comp, WindTurbine):
                    self.env.df['WT total power [W]'] \
                        = self.env.df['WT total power [W]'] - self.env.df[f'{name}: P [W]']
                    self.env.re_supply.remove(comp)
                    self.env.supply_components.remove(comp)
                elif isinstance(comp, DieselGenerator):
                    self.env.supply_components.remove(comp)
                self.env.df = self.env.df.drop(columns=[f'{name}: P [W]'])
                del (component[row])
                # Remove item from QListView
                tab.component_df = tab.component_df.drop(row, axis=0)
                gui_func.update_listview(tab=tab,
                                         df=tab.component_df)
                # Remove item from dispatch listview
                dispatch_row = tabs(8).component_df.index[tabs(8).component_df['Name'] == name].to_list()[0]
                tabs(8).component_df = tabs(8).component_df.drop(dispatch_row,
                                                                 axis=0)
                gui_func.update_listview(tab=tabs(8), df=tabs(8).component_df)
            else:
                # No component selected
                pop_up = self.pop_up_dialog(title='Warning: Select component',
                                            message='Please select component from list.',
                                            box_type='warning')
        else:
            # No component existing
            pop_up = self.pop_up_dialog(title='Warning: No component',
                                        message='No component has been created.',
                                        box_type='warning')

    def save(self):
        """
        Define save function based on tab index
        :return: None
        """
        index = self.tabs.currentIndex()
        tabs = self.tabs.widget
        tab = tabs(index)
        if index == 1:
            # Environment
            self.create_env(tab)
            # Reset widgets
            gui_func.clear_widget(widget=[tab.project_name, tab.latitude, tab.longitude,
                                          tab.electricity_price, tab.co2_price, tab.wt_feed, tab.pv_feed,
                                          tab.co2_grid, tab.diesel_price])
            gui_func.change_combo_index(combo=[tab.terrain, tab.time_step, tab.tz],
                                        index=[0, 0, 12])
            tab.blackout.setChecked(False)
            tab.feed_in.setChecked(False)
            tab.grid.setChecked(True)
            # Enable widgets
            gui_func.enable_widget(widget=[tabs(2), tabs(3), tabs(4), tabs(5), tabs(6), tabs(7), tabs(8)],
                                   enable=True)
        elif index == 3:
            # Load profile
            self.gui_add_load_profile(tab)
            # Clear widgets
            gui_func.clear_widget(widget=[tab.consumption, tab.load_profile])
            gui_func.change_combo_index(combo=[tab.ref_profile],
                                        index=[0])
        elif index == 4:
            # PV system
            self.gui_add_pv(tab)
            data = gui_func.collect_component_data(self.env.pv[-1])
            # Update QListWidget
            gui_func.update_component_df(data=data,
                                         tab=self.tabs.widget(index))
            gui_func.update_listview(tab=self.tabs.widget(index),
                                     df=self.tabs.widget(index).component_df)
            # Update component df in tab dispatch
            gui_func.update_component_df(data=data,
                                         tab=self.tabs.widget(8))
        elif index == 5:
            # Wind turbine
            self.gui_add_wt(tab)
            data = gui_func.collect_component_data(self.env.wind_turbine[-1])
            # Update QListWidget
            gui_func.update_component_df(data=data,
                                         tab=self.tabs.widget(index))
            gui_func.update_listview(tab=self.tabs.widget(index),
                                     df=self.tabs.widget(index).component_df)
            # Update component df in tab dispatch
            gui_func.update_component_df(data=data,
                                         tab=self.tabs.widget(8))
        elif index == 6:
            # Diesel generator
            self.gui_add_dg(tab)
            gui_func.clear_widget(widget=[tab.p, tab.fuel, tab.invest, tab.op_main])
            gui_func.change_widget_text(widget=[tab.c_var],
                                        text=['0.021'])
            data = gui_func.collect_component_data(self.env.diesel_generator[-1])
            # Update QListWidget
            gui_func.update_component_df(data=data,
                                         tab=self.tabs.widget(index))
            gui_func.update_listview(tab=self.tabs.widget(index),
                                     df=self.tabs.widget(index).component_df)
            # Update component df in tab dispatch
            gui_func.update_component_df(data=data,
                                         tab=self.tabs.widget(8))
        elif index == 7:
            # Energy Storage
            self.gui_add_storage(tab=tab)
            gui_func.clear_widget(widget=[tab.p, tab.c])
            gui_func.change_widget_text(
                widget=[tab.soc, tab.soc_min, tab.soc_max, tab.n_charge, tab.n_discharge, tab.lifetime],
                text=['0.25', '0.05', '0.95', '0.8', '0.8', '10'])
            data = gui_func.collect_component_data(self.env.storage[-1])
            # Update QListWidget
            gui_func.update_component_df(data=data,
                                         tab=self.tabs.widget(index))
            gui_func.update_listview(tab=self.tabs.widget(index),
                                     df=self.tabs.widget(index).component_df)
            # Update component df in tab dispatch
            gui_func.update_component_df(data=data,
                                         tab=self.tabs.widget(8))
        elif index == 8:
            # Tab dispatch
            # TODO: Threading with message
            if self.env.load is not None:
                pop_up = self.pop_up_dialog(title='Information: Dispatch in progress',
                                            message='This window will close automatically once dispatch is finished.',
                                            box_type='information',
                                            dialog=False)
                operator_thread = threading.Thread(target=self.create_operator)
                operator_thread.start()
                operator_thread.join()
                pop_up.close()
                gui_func.enable_widget(widget=[self.tabs.widget(9)], enable=True)
                self.evaluate_system(tab=self.tabs.widget(9))
                self.tabs.setCurrentIndex(9)
            else:
                print('Add load to energy system.')
                pop_up = self.pop_up_dialog(title='Warning: Dispatch not possible',
                                            message='No load profile was added to energy system',
                                            box_type='warning')
        elif index == 9:
            # Tab evaluation
            self.create_report()
            # pop_up = self.pop_up_dialog(title='Information: Creating report',
            #                             message='This window will close automatically once report is finished.',
            #                             box_type='information',
            #                             dialog=False)
            # report_thread = threading.Thread(target=self.create_report)
            # report_thread.start()
            # report_thread.join()
            # pop_up.close()

    def create_env(self, tab: QWidget):
        """
        Create Environment from User Input
        :param tab: Widget
            current tab
        :return: None
        """
        # Collect input parameters
        name = tab.project_name.text()
        longitude = gui_func.convert_str_float(string=tab.longitude.text())
        latitude = gui_func.convert_str_float(string=tab.latitude.text())
        terrain = tab.terrain.currentText()
        start_time = tab.start_time.text()
        end_time = tab.end_time.text()
        time_step = tab.time_step.currentText()
        d_rate = gui_func.convert_str_float(string=tab.d_rate.text())
        lifetime = int(gui_func.convert_str_float(string=tab.lifetime.text()))
        co2_price = gui_func.convert_str_float(string=tab.co2_price.text())
        diesel_price = gui_func.convert_str_float(string=tab.diesel_price.text())
        grid_connection = tab.grid.isChecked()
        if grid_connection:
            electricity_price = gui_func.convert_str_float(string=tab.electricity_price.text())
            feed_in = tab.feed_in.isChecked()
            blackout = tab.blackout.isChecked()
            co2_grid = gui_func.convert_str_float(string=tab.co2_grid.text())
            if blackout:
                blackout_data = tab.blackout_data.text()
            else:
                blackout_data = None
            if feed_in:
                pv_feed_in = gui_func.convert_str_float(string=tab.pv_feed.text())
                wt_feed_in = gui_func.convert_str_float(string=tab.wt_feed.text())
            else:
                pv_feed_in = None
                wt_feed_in = None
        else:
            electricity_price = None
            feed_in = False
            blackout = None
            blackout_data = None
            pv_feed_in = None
            wt_feed_in = None
            co2_grid = None
        # Location
        location = {'longitude': longitude,
                    'latitude': latitude,
                    'terrain': terrain}
        # Time
        timezone = tab.tz.currentText()
        time_data = gui_func.convert_datetime(start=start_time, end=end_time, step=time_step)
        time = {'start': time_data[0], 'end': time_data[1], 'step': time_data[2], 'timezone': timezone}
        # Economy
        economy = {'d_rate': d_rate,
                   'lifetime': lifetime,
                   'electricity_price': electricity_price,
                   'diesel_price': diesel_price,
                   'co2_price': co2_price,
                   'pv_feed_in': pv_feed_in,
                   'wt_feed_in': wt_feed_in,
                   'currency': 'US$'}
        # Ecological
        ecology = {'co2_diesel': 0.2665, 'co2_grid': co2_grid}
        # csv-format:
        csv_format = self.tabs.widget(0).csv_format.currentIndex()
        if csv_format == 1:
            sep = ';'
            decimal = ','
        else:
            sep = ','
            decimal = '.'
        land = globe.is_land(lat=latitude,
                             lon=longitude)
        if not land:
            pop_up = self.pop_up_dialog(title='Warning: Location not on land.',
                                        message='Please select location on land.',
                                        box_type='warning')
        else:
            try:
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
                                       csv_decimal=decimal,
                                       csv_sep=sep)
                # Update folium map
                tab.update_map(latitude=location['latitude'],
                               longitude=location['longitude'],
                               name=name)
                self.pvlib_database()
                self.windpowerlib_database()
                # Plot weather data
                self.plot_monthly_weather_data()
                # Change system type widget
                system_type = self.env.system
                gui_func.change_widget_text(widget=[self.tabs.widget(8).system_type], text=[system_type])
            except Exception:
                pop_up = self.pop_up_dialog(title='Warning: Invalid input parameters.',
                                            message='Please enter valid parameters to create energy system.',
                                            box_type='warning',
                                            button=False)

    def gui_add_load_profile(self, tab: QWidget):
        """
        Create load profile
        :param tab: Widget
            current tab
        :return: None
        """
        # Get method
        method = tab.method_combo.currentIndex()
        # Set all parameters to None
        annual_consumption = None
        ref_profile = None
        load_profile_path = None
        # Retrieve parameters depending on method
        if method == 0:
            # Method 1 - Reference load profile
            annual_consumption = gui_func.convert_str_float(string=tab.consumption.text())
            ref_profile_index = tab.ref_profile.currentIndex()
            profiles = ['hospital_ghana', 'H0', 'G0', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'L0', 'L1', 'L2']
            ref_profile = profiles[ref_profile_index]
        else:
            # Method 2 - Individual load profile
            load_profile_path = tab.load_profile.text()
            load_profile_path = load_profile_path.replace('\\', '/')
        # Add load profile to Environment
        try:
            if isinstance(self.env, Environment):
                self.env.add_load(annual_consumption=annual_consumption,
                                  ref_profile=ref_profile,
                                  load_profile=load_profile_path)
                tab.adjust_plot(time_series=self.env.time_series,
                                df=self.env.load.df)
                gui_func.enable_widget(widget=[self.delete_btn], enable=True)
        except Exception:
            pop_up = self.pop_up_dialog(title='Warning: Invalid input parameter',
                                        message='Please enter valid parameters to add load profile to energy system.',
                                        box_type='warning',
                                        button=False)

    def gui_add_pv(self, tab: QWidget):
        """
        Add PV system to environment
        :param tab: Widget
            current tab
        :return: None
        """
        # Get method
        method = tab.method_combo.currentIndex()
        if method == 0:
            # Standard method
            # Collect parameters
            p = gui_func.convert_str_float(string=tab.p.text()) * 1000
            p_min = gui_func.convert_str_float(string=tab.p_min.text())
            p_max = gui_func.convert_str_float(string=tab.p_max.text())
            inverter = gui_func.convert_str_float(string=tab.inverter_range.text()) * 1000
            azimuth = int(gui_func.convert_str_float(string=tab.azimuth.text()))
            tilt = int(gui_func.convert_str_float(string=tab.tilt.text()))
            invest = gui_func.convert_str_float(string=tab.invest.text())
            opm = gui_func.convert_str_float(string=tab.opm.text())
            pv_data = {'surface_tilt': tilt, 'surface_azimuth': azimuth, 'min_module_power': p_min,
                       'max_module_power': p_max, 'inverter_power_range': inverter}
            self.env.add_pv(p_n=p,
                            pv_data=pv_data,
                            c_invest=invest,
                            c_op_main=opm)
            gui_func.clear_widget(widget=[tab.p, tab.p_min, tab.p_max, tab.inverter_range, tab.azimuth, tab.tilt,
                                          tab.invest, tab.opm])
        elif method == 1:
            # Advanced method
            # Collect parameters
            module = tab.module.currentText()
            inverter = tab.inverter.currentText()
            modules_per_string = int(gui_func.convert_str_float(string=tab.modules_per_string.text()))
            strings_per_inverter = int(gui_func.convert_str_float(string=tab.strings_per_inverter.text()))
            azimuth = int(gui_func.convert_str_float(string=tab.azimuth.text()))
            tilt = int(gui_func.convert_str_float(string=tab.tilt.text()))
            invest = gui_func.convert_str_float(string=tab.invest.text())
            opm = gui_func.convert_str_float(string=tab.opm.text())
            pv_data = {'pv_module': module, 'inverter': inverter, 'surface_tilt': tilt, 'surface_azimuth': azimuth,
                       'modules_per_string': modules_per_string, 'strings_per_inverter': strings_per_inverter}
            self.env.add_pv(pv_data=pv_data,
                            c_invest=invest,
                            c_op_main=opm)
            gui_func.clear_widget(widget=[tab.modules_per_string, tab.strings_per_inverter, tab.azimuth,
                                          tab.tilt, tab.invest, tab.opm])
            gui_func.change_combo_index(combo=[tab.module, tab.inverter], index=[0, 0])
        elif method == 2:
            # PV profile
            # TODO: Check functionality
            profile = tab.profile.text()
            invest = gui_func.convert_str_float(string=tab.invest.text())
            opm = gui_func.convert_str_float(string=tab.opm.text())
            self.env.add_pv(pv_profile=profile,
                            c_invest=invest,
                            c_op_main=opm)
            gui_func.clear_widget(widget=[tab.profile, tab.invest, tab.opm])
        else:
            pass

    def gui_add_wt(self, tab: QWidget):
        """
        Add wind turbine to environment
        :param tab: QWidget
            current tab
        :return: None
        """
        method = tab.method_combo.currentIndex()
        if method == 0:
            # Default
            p_min = gui_func.convert_str_float(string=tab.p_min.text()) * 1000
            p_max = gui_func.convert_str_float(string=tab.p_max.text()) * 1000
            invest = gui_func.convert_str_float(string=tab.invest.text())
            opm = gui_func.convert_str_float(string=tab.opm.text())
            selection_parameters = [p_min, p_max]
            self.env.add_wind_turbine(selection_parameters=selection_parameters,
                                      c_invest=invest,
                                      c_op_main=opm)
            gui_func.clear_widget(widget=[tab.p_min, tab.p_max, tab.invest, tab.opm])
        elif method == 1:
            # Advanced
            p = gui_func.convert_str_float(string=tab.p.text()) * 1000
            turbine = tab.turbine.currentText()
            hub_height = gui_func.convert_str_float(string=tab.height.text())
            turbine_data = {'turbine_type': turbine, 'hub_height': hub_height, 'p_n': p}
            invest = gui_func.convert_str_float(string=tab.invest.text())
            opm = gui_func.convert_str_float(string=tab.opm.text())
            self.env.add_wind_turbine(p_n=p,
                                      turbine_data=turbine_data,
                                      c_invest=invest,
                                      c_op_main=opm)
            gui_func.clear_widget(widget=[tab.p, tab.height, tab.invest, tab.opm])
            gui_func.change_combo_index(combo=[tab.turbine], index=[0])
        elif method == 2:
            # TODO: Check functionality
            # Wind turbine energy generation profile
            p = gui_func.convert_str_float(string=tab.p.text()) * 1000
            profile = tab.profile.text()
            invest = gui_func.convert_str_float(string=tab.invest.text())
            opm = gui_func.convert_str_float(string=tab.opm.text())
            self.env.add_wind_turbine(p_n=p,
                                      wt_profile=profile,
                                      c_invest=invest,
                                      c_op_main=opm)
        else:
            pass

    def gui_add_dg(self, tab: QWidget):
        """
        Add diesel generator to energy system
        :param tab: QWidget
            current tab
        :return: None
        """
        p = gui_func.convert_str_float(string=tab.p.text()) * 1000
        fuel_consumption = gui_func.convert_str_float(string=tab.fuel.text())
        invest = gui_func.convert_str_float(string=tab.invest.text())
        opm = gui_func.convert_str_float(string=tab.op_main.text())
        c_var = gui_func.convert_str_float(string=tab.c_var.text())
        self.env.add_diesel_generator(p_n=p,
                                      fuel_consumption=fuel_consumption,
                                      c_invest=invest,
                                      c_op_main=opm,
                                      c_var_n=c_var)

    def gui_add_storage(self, tab: QWidget):
        """
        Create energy storage
        :return: None
        """
        # Collect parameters
        p = gui_func.convert_str_float(tab.p.text()) * 1000
        c = gui_func.convert_str_float(tab.c.text()) * 1000
        soc = gui_func.convert_str_float(tab.soc.text())
        lifetime = int(gui_func.convert_str_float(tab.lifetime.text()))
        invest = gui_func.convert_str_float(string=tab.invest.text())
        opm = gui_func.convert_str_float(string=tab.opm.text())
        # Create storage
        if p is not None and c is not None:
            self.env.add_storage(p_n=p,
                                 c=c,
                                 soc=soc,
                                 lifetime=lifetime,
                                 c_invest=invest,
                                 c_op_main=opm)

    def create_operator(self):
        """
        Create Operator and run Dispatch
        :return: None
        """
        self.operator = Operator(env=self.env)

    def evaluate_system(self, tab: Qt.Widget):
        """
        Evaluate system and update listview in tab System evaluation
        :param tab: QWidget
        :return: None
        """
        self.evaluation = Evaluation(env=self.env,
                                     operator=self.operator)
        tab.evaluation_df = self.evaluation.evaluation_df
        components = self.evaluation.evaluation_df.index.tolist()
        tab.evaluation_df.insert(0, column='Component', value=components)
        gui_func.update_listview(tab=tab,
                                 df=tab.evaluation_df)

    def create_report(self):
        """
        Generate and export report
        :return: None
        """
        print('Creating report. This may take couple minutes.')
        self.report = Report(env=self.env,
                             operator=self.operator,
                             evaluation=self.evaluation)
        print('Report finished.')

    def pvlib_database(self):
        """
        Retrieve pvlib database
        :return: None
        """
        tab = self.tabs.widget(4)
        conn = self.env.database.connect
        # Modules
        module = 'pvlib_cec_module'
        inverter = 'pvlib_cec_inverter'
        module_df = pd.read_sql_query(f'SELECT * From {module}', conn)
        module_df = module_df.transpose()
        module_col = module_df.loc['index']
        module_df = module_df.drop(index='index')
        module_df.columns = module_col
        modules = module_df.columns
        for x in modules:
            x.replace('_', ' ')
        tab.module_lib = modules
        # Add module lib to ComboBox
        tab.module.addItems(tab.module_lib)
        # Inverter
        inverter_df = pd.read_sql_query(f'SELECT * From {inverter}', conn)
        inverter_df = inverter_df.transpose()
        inverter_col = inverter_df.loc['index']
        inverter_df = inverter_df.drop(index='index')
        inverter_df.columns = inverter_col
        inverters = inverter_df.columns
        for x in inverters:
            x.replace('_', ' ')
        tab.inverter_lib = inverters
        tab.inverter.addItems(tab.inverter_lib)

    def windpowerlib_database(self):
        """
        Retrieve wwindpowerlib database
        :return:
        """
        tab = self.tabs.widget(5)
        conn = self.env.database.connect
        df = pd.read_sql_query("SELECT * FROM windpowerlib_turbine WHERE has_power_curve = 1", conn)
        df = df.drop('index', axis=1)
        df = df.set_index('turbine_type')
        windturbines = df.index.tolist()
        tab.turbine_lib = windturbines
        tab.turbine.addItems(tab.turbine_lib)

    def plot_monthly_weather_data(self):
        """
        Plot monthly weather data based on location
        :return: None
        """
        wind_data = self.env.monthly_weather_data[['wind_speed', 'wind_direction']]
        gui_func.create_wind_plot(name='wind_data',
                                  data_1=wind_data['wind_speed'],
                                  data_2=wind_data['wind_direction'])
        gui_func.create_pixmap(path=f'{self.root}/gui/images/wind_data.png',
                               widget=self.tabs.widget(2).wind_plot,
                               w=int(self.screen_width / 3),
                               h=int(self.screen_height / 3))
        solar_data = self.env.monthly_weather_data[['ghi', 'dhi', 'dni']]
        gui_func.create_solar_plot(name='solar_data',
                                   data=solar_data)
        gui_func.create_pixmap(path=f'{self.root}/gui/images/solar_data.png',
                               widget=self.tabs.widget(2).solar_plot,
                               w=int(self.screen_width / 3),
                               h=int(self.screen_height / 3))

    def pop_up_dialog(self,
                      title: str = None,
                      message: str = None,
                      box_type: str = None,
                      button: bool = False,
                      dialog: bool = False):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(title)
        dlg.setText(message)
        if box_type == 'information':
            dlg.setIcon(QMessageBox.Information)
        elif box_type == 'warning':
            dlg.setIcon(QMessageBox.Warning)
        elif box_type == 'question':
            dlg.setIcon(QMessageBox.Question)
        if button:
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if dialog:
            dlg.exec()
        else:
            dlg.show()

        return dlg


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont('Calibri'))
    window = TabWidget()
    sys.exit(app.exec())
