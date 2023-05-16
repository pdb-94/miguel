import sys
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import pandas as pd
import windpowerlib


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
                 c_invest_n: float = 1160,
                 c_op_main_n: float = 43,
                 c_var: float = 0.0035,
                 co2_init: float = 200):
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
        :param c_var: float
            variable cost [US$/kWh]
        :param co2_init: float
            initial CO2-emissions during production [US$/kW]
        """
        self.env = env
        self.p_n = p_n
        self.name = name
        self.c_invest_n = c_invest_n  # USD/kW
        self.c_op_main_n = c_op_main_n  # USD/kW
        self.c_var = c_var  # USD/kWh
        self.co2_init = co2_init  # kg/kW
        # Location
        self.longitude = self.env.location.get('longitude')
        self.latitude = self.env.location.get('latitude')
        self.altitude = self.env.location.get('altitude')
        self.roughness_length = self.env.location.get('terrain')
        # DataFrame
        self.df = pd.DataFrame(columns=['P [W]'], index=self.env.time)
        if wind_speed is not None:
            self.df['Wind speed [km/h]'] = wind_speed
        if wt_profile is not None:
            self.df['P [W]'] = wt_profile
        if turbine_data is not None:
            self.turbine_data = turbine_data
            self.hub_height = self.turbine_data.get('hub_height')

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
                               'Specific investment cost [' + self.env.currency + '/kW]': int(self.c_invest_n),
                               'Investment cost [' + self.env.currency + ']': int(self.c_invest_n * self.p_n / 1000),
                               'Specific operation maintenance cost [' + self.env.currency + '/kW]': int(
                                   self.c_op_main_n),
                               'Operation maintenance cost [' + self.env.currency + '/a]': int(
                                   self.c_op_main_n * self.p_n / 1000)}

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
        index = pd.MultiIndex.from_tuples(tuples, names=['variable_name', 'height'])
        weather_data = pd.DataFrame(np.nan, index=self.env.time_series, columns=index)
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
        start = dt.datetime(year=start_y, month=1, day=1, hour=0, minute=0)
        end = dt.datetime(year=end_y, month=12, day=31, hour=23, minute=0)
        wt_yield_time_series = pd.date_range(start=start, end=end, freq='1h')

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
            wt_yield = pd.DataFrame(index=self.env.time_series, columns=df.columns)
            # Fill simulated values
            for i in range(len(df.index)):
                index = df.index[i]
                wt_yield.loc[index, 'temp_air'] = df.loc[index, 'temp_air']
                wt_yield.loc[index, 'relative_humidity'] = df.loc[index, 'relative_humidity']
                wt_yield.loc[index, 'wind_speed'] = df.loc[index, 'wind_speed']
                wt_yield.loc[index, 'wind_direction'] = df.loc[index, 'wind_direction']
                wt_yield.loc[index, 'pressure'] = df.loc[index, 'pressure']
            # Interpolate values
            for col in wt_yield.columns:
                wt_yield[col] = wt_yield[col].astype(float)
                wt_yield[col] = wt_yield[col].interpolate(method='time')

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

    def pick_windturbine(self, min_height: float, max_height: float):
        """

        :param min_height:
        :param max_height:
        :return:
        """
        min_power = 0.8 * self.p_n
        max_power = 1.2 * self.p_n

