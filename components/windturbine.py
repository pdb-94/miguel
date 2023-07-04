import random
import sys
import os
import numpy as np
import datetime as dt
import pandas as pd
import windpowerlib
from configparser import ConfigParser


class WindTurbine:
    """
    Class to represent Wind Turbines
    """

    def __init__(self,
                 env,
                 name: str = None,
                 p_n: float = None,
                 wt_profile: pd.DataFrame = None,
                 turbine_data: dict = None,
                 wind_speed: pd.Series = None,
                 selection_parameters: list = None,
                 c_invest_n: float = 1160,
                 c_op_main_n: float = 43,
                 c_var_n: float = 0.0035,
                 co2_init: float = 200,
                 c_invest: float = None,
                 c_op_main: float = None):
        """
        :param env: environment
        :param name: str
            name
        :param p_n: float
            nominal power
        :param wt_profile: pd.DataFrame
            Wind energy production profile
        :param turbine_data: dict
            {'turbine_type': str,
             'hub_height': float}
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
        self.p_n = p_n
        self.name = name
        self.selection_parameters = selection_parameters
        self.c_invest_n = c_invest_n  # USD/kW
        self.c_op_main_n = c_op_main_n  # USD/kW
        self.c_var_n = c_var_n  # USD/kWh
        # Location
        self.longitude = self.env.longitude
        self.latitude = self.env.latitude
        self.altitude = self.env.altitude
        self.roughness_length = self.env.terrain
        # DataFrame
        self.df = pd.DataFrame(columns=['P [W]'],
                               index=self.env.time)
        if self.selection_parameters is not None:
            self.turbine_data = self.pick_windturbine(selection_parameters=selection_parameters)
            self.hub_height = self.turbine_data.get('hub_height')
            self.p_n = self.turbine_data.get('p_n')
        if wind_speed is not None:
            self.df['Wind speed [km/h]'] = wind_speed
        if wt_profile is not None:
            self.df['P [W]'] = wt_profile
            self.p_n = p_n
        if turbine_data is not None:
            self.turbine_data = turbine_data
            self.hub_height = self.turbine_data.get('hub_height')
            self.p_n = self.turbine_data.get('p_n')
        if c_invest is None:
            self.c_invest = self.c_invest_n * self.p_n / 1000
        else:
            self.c_invest = c_invest
        if c_op_main is None:
            self.c_op_main = self.c_op_main_n * self.p_n / 1000
        else:
            self.c_op_main = c_op_main
        self.co2_init = co2_init * self.p_n / 1000  # kg

        self.turbine_df = self.get_turbine_data()
        self.windturbine = self.create_wind_turbine()
        self.modelchain = self.create_modelchain()
        # Prepare weather data
        self.annual_weather_data = self.env.wt_weather_data
        self.annual_weather_data = self.modify_weather_data()
        # Run windpowerlib
        self.annual_wt_yield = self.run(weather_data=self.annual_weather_data)
        self.wt_yield = self.annual_wt_yield.loc[self.env.time_series[0]:self.env.time_series[-1]]
        self.df['P [W]'] = self.wt_yield

        # Dict with technical data
        self.technical_data = {'Component': 'Wind Turbine',
                               'Name': self.name,
                               'Nominal Power [kW]': round(self.p_n / 1000, 3),
                               f'Specific investment cost [{self.env.currency}/kW]': int(self.c_invest_n),
                               f'Investment cost [{self.env.currency}]': int(self.c_invest_n * self.p_n / 1000),
                               f'Specific operation maintenance cost [{self.env.currency}/kW]': int(self.c_op_main_n),
                               f'Operation maintenance cost [{self.env.currency}/a]': int(
                                   self.c_op_main_n * self.p_n / 1000)}

        if wt_profile is not None:
            pass
        else:
            self.config = ConfigParser()
            self.create_config()

    def get_turbine_data(self):
        """
        Get turbine data from windpowerlib
        :return: data
        """
        connect = self.env.database.connect
        data = pd.read_sql_query("SELECT * FROM windpowerlib_turbine", connect)

        return data

    def modify_weather_data(self):
        """
        Modify weather data for windpowerlib use
        :return: pd.DataFrame
            Modified weather_data
        """
        # Create MultiIndex
        arrays = [['wind_speed', 'wind_speed', 'temperature', 'temperature', 'pressure'],
                  [10, self.hub_height, 2, self.hub_height, 0]]
        tuples = list(zip(*arrays))
        index = pd.MultiIndex.from_tuples(tuples,
                                          names=['variable_name', 'height'])
        weather_data = pd.DataFrame(np.nan,
                                    index=self.env.time_series,
                                    columns=index)
        # Assign values to columns
        weather_data['wind_speed', 10] = self.annual_weather_data['wind_speed']
        weather_data['temperature', 2] = self.annual_weather_data['temp_air'] + 273.15
        weather_data['pressure', 0] = self.annual_weather_data['pressure']
        # Calculate wind speed and temperature at hub height
        weather_data['wind_speed', self.hub_height] = self.calc_wind_speed(wind_df=weather_data['wind_speed', 10],
                                                                           hub_height=self.hub_height)
        weather_data['temperature', self.hub_height] = self.calc_temperature(
                                                                        temperature_df=weather_data['temperature', 2],
                                                                        hub_height=self.hub_height)
        return weather_data

    def create_wind_turbine(self):
        """
        Create windpowerlib.WindTurbine object in self.WindTurbine
        :return: None
        """
        wind_turbine = windpowerlib.WindTurbine(**self.turbine_data)

        return wind_turbine

    def create_modelchain(self):
        """
        Create windpowerlib.ModelChain object in self.ModelChain
        :return: None
        """
        modelchain = windpowerlib.modelchain.ModelChain(power_plant=self.windturbine)

        return modelchain

    def run(self, weather_data: pd.DataFrame):
        """
        Run simulation
        :param weather_data: pd.DataFrame
            weather input data
        :return: pd.Series
            simulation results
        """
        density_hub = self.modelchain.density_hub(weather_df=weather_data)
        wind_speed_hub = self.modelchain.wind_speed_hub(weather_df=weather_data)
        simulation_results = self.modelchain.calculate_power_output(wind_speed_hub=wind_speed_hub,
                                                                    density_hub=density_hub)
        return simulation_results

    def convert_index_time(self):
        """
        Convert results to current year and time resolution
        :return:
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
        wt_yield_time_series = pd.date_range(start=start,
                                             end=end,
                                             freq='1h')

        return wt_yield_time_series

    def interpolate_values(self, df: pd.DataFrame):
        """
        Interpolate values to environment time resolution
        :return: pd.Series
            WT Yield with interpolated values
        """
        if self.env.t_step == dt.timedelta(minutes=60):
            pass
        else:
            # Create index with environment time resolution
            wt_yield = pd.DataFrame(index=self.env.time_series,
                                    columns=df.columns)
            # Fill simulated values
            wt_yield = pd.DataFrame(index=self.env.time_series, columns=df.columns)

            # Fill simulated values
            wt_yield['temp_air'] = df['temp_air'].values
            wt_yield['relative_humidity'] = df['relative_humidity'].values
            wt_yield['wind_speed'] = df['wind_speed'].values
            wt_yield['wind_direction'] = df['wind_direction'].values
            wt_yield['pressure'] = df['pressure'].values

            # Interpolate values
            wt_yield = wt_yield.astype(float).interpolate(method='time')

            return wt_yield

    def calc_wind_speed(self, wind_df: pd.Series, hub_height: float):
        """
        Calculate wind speed using hellman equation at hub height
        Hau, E.: “Windkraftanlagen - Grundlagen, Technik, Einsatz, Wirtschaftlichkeit”. 4. Auflage, Springer-Verlag, 2008, p. 517
        Sharp, E.: “Spatiotemporal disaggregation of GB scenarios depicting increased wind capacity and electrified heat demand in dwellings”. UCL, Energy Institute, 2015, p. 83

        :param wind_df: pd.Series
            wind speed at 10m
        :param hub_height: float
        :return: pd.Series
            Wind speed at hub height
        Roughness length: EnArgus: https://www.enargus.de/pub/bscw.cgi/d9182-2/*/*/Rauigkeitsl%C3%A4nge.html?op=Wiki.getwiki
        """
        roughness_length = {'Water surfaces': 0.0002,
                            'Open terrain with smooth surface, e.g., concrete, airport runways, mowed grass': 0.0024,
                            'Open agricultural terrain without fences or hedges, possibly with widely scattered houses, very rolling hills': 0.03,
                            'Agricultural terrain with some houses and 8 meter high hedges at a distance of approx. 1250 meters': 0.055,
                            'Agricultural terrain with many houses, bushes, plants or 8 meter high hedges at a distance of approx. 250 meters': 0.2,
                            'Villages, small towns, agricultural buildings with many or high hedges, woods and very rough and uneven terrain': 0.4,
                            'Larger cities with tall buildings': 0.8,
                            'Large cities, tall buildings, skyscrapers': 1.6}
        z0 = roughness_length.get(self.roughness_length)
        a = 1 / np.log(self.hub_height / z0)
        # Calculate hub height
        wind_speed_hub_height = wind_df * (hub_height / 10) ** a

        return wind_speed_hub_height

    def calc_temperature(self, temperature_df: pd.Series, hub_height: float, initial_height: float = 2):
        """
        Calculate temperature at hub height with linear temperature gradient
        ICAO-Standardatmosphäre (ISA). http://www.dwd.de/DE/service/lexikon/begriffe/S/Standardatmosphaere_pdf.pdf?__blob=publicationFile&v=3

        :param temperature_df: pd.Series
            temperatures at inital height
        :param hub_height: float
            hub height
        :param initial_height: float
            height of initial data (default: 2m)
        :return: pd.Series
            temperature at hub height
        """
        temperature_hub_height = temperature_df - 0.0065 * (hub_height - initial_height)

        return temperature_hub_height

    def pick_windturbine(self, selection_parameters):
        """
        Pick wind turbine based on power range
        :param selection_parameters: list
            min and max power
        :return: dict
            turbine_data (turbine_type & hub_height)
        """
        # Unpack parameters
        power_min = selection_parameters[0]
        power_max = selection_parameters[1]
        # Retrieve turbine parameters from database
        conn = self.env.database.connect
        df = pd.read_sql_query("SELECT * FROM windpowerlib_turbine WHERE has_power_curve = 1", conn)
        df = df.drop('index', axis=1)
        df = df.set_index('turbine_type')
        # Collect wind turbines if nominal power in power range
        turbine = []
        for wt in df.index:
            if power_max > df.loc[wt, 'nominal_power'] > power_min:
                turbine.append(wt)
        # Select random wind turbine
        turbine_parameters = self.select_turbine(turbine=turbine, df=df)
        windturbine = turbine_parameters[0]
        height = turbine_parameters[1]
        while height is None:
            turbine_parameters = self.select_turbine(turbine=turbine, df=df)
            windturbine = turbine_parameters[0]
            height = turbine_parameters[1]
        # Select hub height
        if isinstance(df.loc[windturbine, 'hub_height'], str):
            height_string = df.loc[windturbine, 'hub_height'].replace(' ', '')
            height_string = height_string.replace('None', '')
            height_string = height_string.replace(',', '.')
            variations = height_string.split(';')
            for height in variations:
                if height == '':
                    variations.remove(height)
            hub_height = float(variations[random.randint(0, (len(variations)-1))])
        else:
            hub_height = df.loc[windturbine, 'hub_height']
        p_n = df.loc[windturbine, 'nominal_power']

        turbine_data = {'turbine_type': windturbine, 'hub_height': hub_height, 'p_n': p_n}

        return turbine_data

    def select_turbine(self, turbine, df):
        """
        Select random wind turbine
        :param turbine: list
            turbine types
        :param df: pd.DataFrame
            turbine parameters
        :return: list
            windturbine: str, height: str or None
        """
        windturbine = turbine[random.randint(0, (len(turbine) - 1))]
        height = df.loc[windturbine, 'hub_height']

        return windturbine, height

    def create_config(self):
        """
        Create and write config file for system configuration
        :return: None
        """
        self.config[self.name] = {'turbine_data': self.turbine_data,
                                  'hub_height': self.hub_height}

        path = f'{sys.path[1]}/export/config/'
        if not os.path.exists(path):
            os.makedirs(path)

        with open(f'{sys.path[1]}/export/config/{self.name}_config.ini', 'w') as file:
            self.config.write(file)
