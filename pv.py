import pandas as pd
import numpy as np
import datetime as dt
import pvlib

# TODO: Sascha: Module and inverter database? Temperature and dc_model? Errors


class PV:
    """
    Class to represent PV Systems
    """
    def __init__(self,
                 env,
                 name: str = None,
                 p_n: float = None,
                 location: dict = None,
                 pv_profile: pd.DataFrame = None,
                 pv_module: str = None,
                 inverter: str = None,
                 modules_per_string: int = 1,
                 strings_per_inverter: int = 1,
                 surface_tilt: int = None,
                 surface_azimuth: int = None):
        """
        :param env: env.Environment
        :param name: str
            name of PV system
        :param p_n: int
            nominal power
        :param location: dict
            longitude: float
            latitude: float
            altitude: float
        :param pv_profile: pd.Series
            PV production profile
        :param pv_module: str
            PV module
        :param inverter: str
            Inverter
        :param modules_per_string: int
        :param strings_per_inverter: int
        :param surface_tilt: int
            PV module tilt
        :param surface_azimuth: int
            orientation
        """
        self.env = env
        self.name = name
        self.p_n = p_n
        # Location
        self.longitude = location.get('longitude')
        self.latitude = location.get('latitude')
        self.altitude = location.get('altitude')
        self.surface_tilt = surface_tilt
        self.surface_azimuth = surface_azimuth
        # PV Components
        self.module_lib = list(pvlib.pvsystem.retrieve_sam('CECMod'))
        self.inverter_lib = list(pvlib.pvsystem.retrieve_sam('CECInverter'))
        self.pv_module_parameters = pvlib.pvsystem.retrieve_sam('CECMod')[pv_module]
        self.inverter_parameters = pvlib.pvsystem.retrieve_sam('CECInverter')[inverter]
        self.modules_per_string = modules_per_string
        self.strings_per_inverter = strings_per_inverter
        if self.p_n is None:
            self.p_n = self.pv_module_parameters['I_mp_ref'] * self.pv_module_parameters['V_mp_ref'] \
                       * self.modules_per_string * strings_per_inverter
        # Economic parameters
        self.c_invest_n = 875  # USD/kW IRENA - Renewable Power Generation Costs in 2021, page 79
        self.c_op_main_n = self.c_invest_n * 0.02  # USD/kW Sustainable Energy Handbook Module 6.1 Simplified Financial Models
        self.c_var = 0.0

        # Create Location, PVSystem and ModelChain
        self.location = self.create_location()
        self.pv_system = self.create_pv(temperature_model='open_rack_glass_glass',
                                        surface_tilt=20,
                                        surface_azimuth=180,
                                        strings_per_inverter=self.strings_per_inverter,
                                        modules_per_string=self.modules_per_string)
        self.modelchain = self.create_modelchain(pv_system=self.pv_system)
        # Weather data
        self.weather_data = self.env.weather_data[0]
        # TODO: self.model_chain(): aoi_Model = no_loss --> KEY Error 'precipitable_water'
        self.weather_data['precipitable_water'] = np.nan

        # DataFrame
        self.df = pd.DataFrame(columns=['P [W]'], index=self.env.time)
        if pv_profile is not None:
            # Create DataFrame from existing pv profile
            self.df['P [W]'] = pv_profile
        else:
            # Create Profile and run pvlib
            self.annual_pv_yield = self.run(weather_data=self.weather_data)
            self.annual_pv_yield.index = self.convert_index_time()
            self.pv_yield = self.annual_pv_yield.loc[self.env.time_series[0]:self.env.time_series[-1]]
            self.pv_yield = self.interpolate_values()
            self.df['P [W]'] = self.pv_yield

        # Dict with technical data
        self.technical_data = {'Component': 'PV System',
                               'Name': self.name,
                               'Nominal Power [kW]': round(self.p_n/1000, 3),
                               'Specific investment cost [' + self.env.currency + '/kW]': int(self.c_invest_n),
                               'Investment cost [' + self.env.currency + ']': int(self.c_invest_n*self.p_n/1000),
                               'Specific operation maintenance cost [' + self.env.currency + '/kW]': int(self.c_op_main_n),
                               'Operation maintenance cost [' + self.env.currency + '/a]': int(self.c_op_main_n * self.p_n/1000)}

    def create_pv(self,
                  temperature_model: str = 'open_rack_glass_glass',
                  surface_tilt=20,
                  surface_azimuth=180,
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
        pv_system = pvlib.pvsystem.PVSystem(surface_tilt=surface_tilt,
                                            surface_azimuth=surface_azimuth,
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
        location = pvlib.location.Location(name=self.name + ' Location',
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
                          dc_model='cec'):
        """
        :param pv_system: pv.PVSystem
        :param dc_model:
            default: Sandia PV Array Performance Model (no_loss)
        :return: pvlib.modelchain.ModelChain
            ModelChain object
        """
        # TODO: dc_model sapm: raise ValueError(model + ' selected for the DC model but )'
        modelchain = pvlib.modelchain.ModelChain(system=pv_system,
                                                 location=self.location,
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
        # TODO: aoi_coeff = [module['B5'], module['B4'], module['B3'], module['B2'], - KeyError: 'B5'
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
        start = dt.datetime(year=start_y, month=1, day=1, hour=0, minute=0)
        end = dt.datetime(year=end_y, month=12, day=31, hour=23, minute=0)
        pv_yield_time_series = pd.date_range(start=start, end=end, freq='1h')

        return pv_yield_time_series

    def interpolate_values(self):
        """
        Interpolate values to environment time resolution
        :return: pd.Series
            PV Yield with interpolated values
        """
        if self.env.t_step == dt.timedelta(minutes=60):
            pass
        else:
            # Create index with environment time resolution
            pv_yield = pd.Series(index=self.env.time_series)
            # Fill simulated values
            for i in range(len(self.pv_yield.index)):
                index = self.pv_yield.index[i]
                pv_yield[index] = self.pv_yield[index]
            # Interpolate values
            pv_yield = pv_yield.interpolate(method='time')

            return pv_yield


