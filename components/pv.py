import random
import sys
import os
import pandas as pd
import numpy as np
import datetime as dt
import pvlib
from configparser import ConfigParser


class PV:
    """
    Class to represent PV Systems
    """

    def __init__(self,
                 env,
                 name: str = None,
                 p_n: float = None,
                 pv_profile: pd.Series = None,
                 pv_data: dict = None,
                 c_invest_n: float = 667.68,
                 c_op_main_n: float = 6.06,
                 c_var_n: float = 0,
                 co2_init: float = 460,
                 c_invest: float = None,
                 c_op_main: float = None):
        """
        :param env: env.Environment
            System Environment
        :param name: str
            name of PV system
        :param p_n: float
            nominal power
        :param pv_profile: pd.Series
            PV production profile
        :param pv_data: dict
            pv_module: str
            inverter: str
            modules_per_string: int
            strings_per_inverter: int
            surface_tilt: int
            surface_azimuth: int
        :param c_invest_n: float
            specific investment cost [US$/kW]
        :param c_op_main_n: float
            operation and maintenance cost [US$/kW/a]
        :param c_var_n: float
            variable cost [US$/kWh]
        :param co2_init: float
            initial CO2-emissions during production [US$/kW]
        """
        self.env = env
        self.name = name
        self.df = pd.DataFrame(columns=['P [W]'],
                               index=self.env.time)
        # Location
        self.longitude = self.env.longitude
        self.latitude = self.env.latitude
        self.altitude = self.env.altitude
        # Weather data
        self.weather_data = self.env.weather_data[0]
        self.weather_data['precipitable_water'] = 0.1
        # Libraries (use project-relative data files so this works on other machines)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        module_csv = os.path.join(base_dir, 'data', 'CEC Modules.csv')
        inverter_csv = os.path.join(base_dir, 'data', 'sam-library-cec-inverters-2019-03-05.csv')

        self.module_lib = pd.read_csv(module_csv, sep=',', skiprows=[1, 2])
        self.inverter_lib = pd.read_csv(inverter_csv, sep=',', skiprows=[1, 2])



        if pv_profile is not None:
            # Create DataFrame from existing pv profile
            print("DEBUG: pv_profile received in PV class")
            print("  → Length:", len(pv_profile))
            print("  → Missing values:", pv_profile.isna().sum())
            print("  → Max:", pv_profile.max())

            self.df = pd.DataFrame({'P [W]': pv_profile})

            #self.df['P [W]'] = pv_profile
            self.p_n = p_n
            ####
            print("DEBUG AFTER SETTING P [W] in self.df")
            print("  → Sum:", self.df['P [W]'].sum())
            print("  → Max:", self.df['P [W]'].max())
            print("DEBUG: PV p_n =", self.p_n)
        elif p_n is not None:
            self.p_n = p_n
            self.longitude = self.env.longitude
            self.latitude = self.env.latitude
            self.altitude = self.env.altitude
            if pv_data.get('surface_tilt') is None:
                self.surface_tilt = 20
            else:
                self.surface_tilt = pv_data.get('surface_tilt')
            self.surface_azimuth = pv_data.get('surface_azimuth')
            system_parameters = self.pick_pv_system(min_module_power=pv_data.get('min_module_power'),
                                                    max_module_power=pv_data.get('max_module_power'),
                                                    inverter_power_range=pv_data.get('inverter_power_range'))
            self.pv_module_parameters = system_parameters[0]
            self.pv_module = system_parameters[1]
            self.inverter_parameters = system_parameters[2]
            self.inverter = system_parameters[3]
            self.modules_per_string = system_parameters[4]
            self.strings_per_inverter = system_parameters[5]
            # Create Location, PVSystem and ModelChain
            pvlib_parameters = self.create_pvlib_parameters()
            self.location = pvlib_parameters[0]
            self.pv_system = pvlib_parameters[1]
            self.modelchain = pvlib_parameters[2]
            # Run pvlib
            self.annual_pv_yield = self.run(weather_data=self.weather_data)
            self.annual_pv_yield.index = self.convert_index_time()
            self.pv_yield = self.annual_pv_yield.loc[self.env.time_series[0]:self.env.time_series[-1]]
            if self.env.i_step != 60:
                self.pv_yield = self.interpolate_values()
            self.df['P [W]'] = np.where(self.pv_yield < 0, 0, self.pv_yield)
        elif pv_data is not None:
            if pv_data.get('surface_tilt') is None:
                self.surface_tilt = 20
            else:
                self.surface_tilt = pv_data.get('surface_tilt')
            self.surface_azimuth = pv_data.get('surface_azimuth')
            # PV Components
            self.pv_module = pv_data.get('pv_module')
            self.inverter = pv_data.get('inverter')
            self.modules_per_string = pv_data.get('modules_per_string')
            self.strings_per_inverter = pv_data.get('strings_per_inverter')
            self.pv_module_parameters = self.module_lib[self.pv_module]
            self.inverter_parameters = self.inverter_lib[self.inverter]
            self.p_n = self.pv_module_parameters['I_mp_ref'] * self.pv_module_parameters[
                'V_mp_ref'] * self.modules_per_string * self.strings_per_inverter
            # Create Location, PVSystem and ModelChain
            pvlib_parameters = self.create_pvlib_parameters()
            self.location = pvlib_parameters[0]
            self.pv_system = pvlib_parameters[1]
            self.modelchain = pvlib_parameters[2]
            # Create Profile and dispatch pvlib
            self.annual_pv_yield = self.run(weather_data=self.weather_data)
            self.annual_pv_yield.index = self.convert_index_time()
            self.pv_yield = self.annual_pv_yield.loc[self.env.time_series[0]:self.env.time_series[-1]]
            self.pv_yield = self.interpolate_values()
            self.df['P [W]'] = np.where(self.pv_yield < 0, 0, self.pv_yield)

        # Economic parameters
        self.c_invest_n = c_invest_n
        self.c_op_main_n = c_op_main_n
        self.c_var_n = c_var_n
        self.co2_init = co2_init * self.p_n / 1000  # kg/kW
        if c_invest is None:
            self.c_invest = self.c_invest_n * self.p_n / 1000
        else:
            self.c_invest = c_invest
        if c_op_main is None:
            self.c_op_main = self.c_op_main_n * self.p_n / 1000
        else:
            self.c_op_main = c_op_main
        # Dict with technical data
        self.technical_data = {'Component': 'PV System',
                               'Name': self.name,
                               'Nominal Power [kW]': round(self.p_n / 1000, 3),
                               f'Specific investment cost [{self.env.currency}/kW]': int(self.c_invest_n),
                               f'Investment cost [{self.env.currency}]': int(self.c_invest_n * self.p_n / 1000),
                               f'Specific operation maintenance cost [{self.env.currency}/kW]': int(
                                   self.c_op_main_n),
                               f'Operation maintenance cost [{self.env.currency}/a]': int(
                                   self.c_op_main_n * self.p_n / 1000)}

        if pv_profile is not None:
            pass
        else:
            self.config = ConfigParser()
            self.create_config()

    def create_pvlib_parameters(self):
        """
        Create pvlib parameters
        :return: list
            location, pv_system, modelchain
        """
        location = self.create_location()
        pv_system = self.create_pv(temperature_model='open_rack_glass_glass',
                                   strings_per_inverter=self.strings_per_inverter,
                                   modules_per_string=self.modules_per_string)
        modelchain = self.create_modelchain(pv_system=pv_system, location=location)

        return location, pv_system, modelchain

    def create_pv(self,
                  temperature_model: str = 'open_rack_glass_glass',
                  modules_per_string=1,
                  strings_per_inverter=1):
        """
        :param temperature_model: str
        :param surface_tilt: int
            surface tilt angle
        :param surface_azimuth: int
            surface azimuth angle
        :param modules_per_string: int
            number of modules per string
        :param strings_per_inverter: int
            number of strings per inverter
        :return: pvlib.pvsystem.PVSystem
            PV system
        """
        # Get temperature_model
        temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm'][temperature_model]
        # Create PV system
        pv_system = pvlib.pvsystem.PVSystem(surface_tilt=self.surface_tilt,
                                            surface_azimuth=self.surface_azimuth,
                                            modules_per_string=modules_per_string,
                                            strings_per_inverter=strings_per_inverter,
                                            module_parameters=self.pv_module_parameters,
                                            inverter_parameters=self.inverter_parameters,
                                            temperature_model_parameters=temperature_model_parameters)
        return pv_system

    def create_location(self):
        """
        Create pvlib Location object for modelchain
        :return: pvlib.Location
            Location object
        """
        location = pvlib.location.Location(name=f'{self.name} Location',
                                           longitude=self.longitude,
                                           latitude=self.latitude,
                                           altitude=self.altitude,
                                           tz=self.env.timezone)
        return location

    def run_clearsky_model(self):
        """
        Run clearsky model
        :return: pd.Series
            clearsky model data
        """
        clearsky = self.location.get_clearsky(times=self.env.time_series)

        return clearsky

    def create_modelchain(self,
                          pv_system,
                          location,
                          dc_model='cec'):
        """
        :param pv_system: pv.PVSystem
        :param dc_model:
            default: Sandia PV Array Performance Model (no_loss)
        :return: pvlib.modelchain.ModelChain
            ModelChain object
        """
        modelchain = pvlib.modelchain.ModelChain(system=pv_system,
                                                 location=location,
                                                 name=self.name + ' ModelChain',
                                                 dc_model=dc_model,
                                                 aoi_model='no_loss')
        return modelchain

    def run(self, weather_data):
        """
        Run pvlib simulation
        :param weather_data: pd.DataFrame
        :return: pd.Series
            AC power output
        """
        self.modelchain.run_model(weather=weather_data)
        simulation_results = self.modelchain.results.ac

        return simulation_results

    def convert_index_time(self):
        """
        Convert results to current year and time resolution
        :return: pd.DatetimeIndex
            time index in self.env time resolution
        """
        start_date = self.env.time_series[0]
        start_y = start_date.year
        end_date = self.env.time_series[-1]
        end_y = end_date.year
        # Create time series for simulated year in environment
        start = dt.datetime(year=start_y,
                            month=1,
                            day=1,
                            hour=0,
                            minute=0)
        end = dt.datetime(year=end_y,
                          month=12,
                          day=31,
                          hour=23,
                          minute=0)
        pv_yield_time_series = pd.date_range(start=start,
                                             end=end,
                                             freq='1h')

        return pv_yield_time_series

    def interpolate_values(self):
        """
        Interpolate values to environment time resolution
        :return: pd.Series
            PV Yield with interpolated values
        """
        if self.env.i_step == 60:
            pass
        else:
            # Create index with environment time resolution
            pv_yield = pd.Series(index=self.env.time_series)
            # Fill simulated values
            for index in self.pv_yield.index:
                pv_yield[index] = self.pv_yield[index]
            # Interpolate values
            pv_yield = pv_yield.interpolate(method='time')

            return pv_yield

    def pick_pv_system(self, min_module_power: float, max_module_power: float, inverter_power_range: float):
        """
        Pick PV system based on nominal power
        :param min_module_power: float
            Minimum module power in Watts
        :param max_module_power: float
            Maximum module power in Watts
        :param inverter_power_range: float
            Inverter power range tolerance in Watts
        :return: list
            Selected module, module name, inverter, inverter name, modules per string, strings per inverter
        """
        # Filter modules based on power range
        modules = self.module_lib.loc[
            (self.module_lib['I_mp_ref'] * self.module_lib['V_mp_ref'] >= min_module_power) &
            (self.module_lib['I_mp_ref'] * self.module_lib['V_mp_ref'] <= max_module_power)
            ]

        if modules.empty:
            raise ValueError("No PV modules found within the specified power range.")

        # Pick a random module
        selected_module = modules.sample()
        module_name = selected_module.index[0]
        module = selected_module.iloc[0]

        # Calculate required number of modules
        module_power = module['I_mp_ref'] * module['V_mp_ref']
        n_modules = self.p_n / module_power

        # Determine modules per string and strings per inverter
        if round(n_modules) % 3 == 0:
            modules_per_string = round(n_modules / 3)
            strings_per_inverter = 3
        elif round(n_modules) % 4 == 0:
            modules_per_string = round(n_modules / 4)
            strings_per_inverter = 4
        else:
            modules_per_string = round(n_modules / 2)
            strings_per_inverter = 2

        # Filter inverters based on total module power
        total_power = module_power * modules_per_string * strings_per_inverter
        inverters = self.inverter_lib.loc[
            (self.inverter_lib['Paco'] >= total_power) &
            (self.inverter_lib['Paco'] <= total_power + inverter_power_range)
            ]

        if inverters.empty:
            raise ValueError("No suitable inverter found for the selected modules. Consider adjusting the power range.")

        # Pick a random inverter
        selected_inverter = inverters.sample()
        inverter_name = selected_inverter.index[0]
        inverter = selected_inverter.iloc[0]

        return module, module_name, inverter, inverter_name, modules_per_string, strings_per_inverter

    def create_config(self):
        """
        Create and write config file for system configuration
        :return: None
        """
        self.config[self.name] = {'module': self.pv_module,
                                  'inverter': self.inverter,
                                  'modules_per_string': self.modules_per_string,
                                  'strings_per_inverter': self.strings_per_inverter,
                                  'surface_azimuth': self.surface_azimuth,
                                  'surface_tilt': self.surface_tilt}

        path = f'{sys.path[1]}/export/config/'
        if not os.path.exists(path):
            os.makedirs(path)

        with open(f'{path}{self.name}_config.ini', 'w') as file:
            self.config.write(file)

