import datetime as dt
import pandas as pd
import numpy as np
import pvlib
from geopy.geocoders import Nominatim
# MiGUEL Modules
from pv import PV
from windturbine import WindTurbine
from dieselgenerator import DieselGenerator
from grid import Grid
from storage import Storage
from load import Load


class Environment:
    """
    Environment class containing all system components
    Negative power values are power consumption (load, storage)
    Positive power values are power production (PV, DieselGenerator, WindTurbine, Grid, Storage)
    """

    def __init__(self,
                 name: str = None,
                 time: dict = None,
                 economy: dict = None,
                 ecology: dict = None,
                 location: dict = None):
        """
        :param time: dict:
            Parameter for time series
            {start: dt.datetime,
             end: dt.datetime,
             step: dt.timedelta)
        :param economy: dict
            Parameter for economical calculation
            {d_rate: float,
             i_rate: float,
             lifetime: float,
             co2_price: dict
             feed-in_tariff: list}
        :param ecology: dict
            Parameter for ecological calculations
            {co2_diesel: float,
             co2_grid: float}
        """
        self.name = name
        # Time values
        self.t_start = time.get('start')
        self.t_end = time.get('end')
        self.t_step = time.get('step')
        self.timezone = time.get('timezone')
        self.i_step = self.t_step.seconds / 60
        self.time_series = self.create_df()[0]
        self.time = self.create_df()[1]
        # Location
        self.location = location
        self.longitude = self.location.get('longitude')
        self.latitude = self.location.get('latitude')
        self.altitude = self.location.get('altitude')
        self.terrain = self.location.get('terrain')
        self.address = self.find_location()
        # Economy
        if economy is None:
            self.d_rate = 0.03
            self.i_rate = 0.03
            self.lifetime = 20
            self.feed_in = 0.00
            self.co2_price = {2021: 25, 2022: 30, 2023: 35, 2024: 40, 2025: 55, 2026: 65}
            self.currency = 'US$'
        else:
            self.d_rate = economy.get('d_rate')
            self.i_rate = economy.get('i_rate')
            self.lifetime = economy.get('lifetime')
            self.co2_price = economy.get('co2_price')
            self.feed_in = economy.get('feed-in_tariff')
            self.currency = economy.get('currency')
        if ecology is None:
            self.co2_diesel = 0.2665  # kg CO2/kWh
            self.co2_grid = 0.420  # kg CO2/kWh (Germany)
        else:
            self.co2_diesel = ecology.get('co2_diesel')
            self.co2_grid = ecology.get('co2_grid')

        # Environment DataFrame
        columns = ['P_Res [W]', 'PV total power [W]', 'WT total power [W]']
        self.df = pd.DataFrame(columns=columns, index=self.time)
        self.df['PV total power [W]'] = 0
        self.df['WT total power [W]'] = 0
        self.weather_data = self.get_weather_data()
        self.monthly_df = pd.DataFrame

        # Container
        self.grid = []
        self.load = []
        self.pv = []
        self.diesel_generator = []
        self.wind_turbine = []
        self.storage = []
        self.supply_data = pd.DataFrame(columns=['Component',
                                                 'Name',
                                                 'Nominal Power [kW]',
                                                 'Specific investment cost [' + self.currency + '/kW]',
                                                 'Investment cost [' + self.currency + ']',
                                                 'Specific operation maintenance cost [' + self.currency + '/kW]',
                                                 'Operation maintenance cost [' + self.currency + ']'])
        self.storage_data = pd.DataFrame(columns=['Component',
                                                  'Name',
                                                  'Nominal Power [kW]',
                                                  'Capacity [kWh]',
                                                  'Specific investment cost [' + self.currency + '/kWh]',
                                                  'Investment cost [' + self.currency + ']',
                                                  'Specific operation maintenance cost [' + self.currency + '/kWh]',
                                                  'Operation maintenance cost [' + self.currency + ']'])

    def find_location(self):
        """
        Find address based on coordinates
        :return: list
        """
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse(str(self.latitude) + ',' + str(self.longitude))
        address = location.raw['address']
        city = address.get('city', '')
        state = address.get('state', '')
        country = address.get('country', '')
        code = address.get('country_code')
        zipcode = address.get('postcode')

        return city, zipcode, state, country, code

    def create_df(self):
        """
        Create
        :return:
        """
        time_series = pd.date_range(start=self.t_start, end=self.t_end, freq=self.t_step)
        df = pd.Series(time_series)

        return time_series, df

    def get_weather_data(self):
        """
        Retrieve weather data from PHOTOVOLTAIC GEOGRAPHICAL INFORMATION SYSTEM
        :return:
            data: pd.DataFrame
            months_selected: list
            inputs: dict
            metadata: dict
        """
        data, months_selected, inputs, metadata = pvlib.iotools.get_pvgis_tmy(latitude=self.latitude,
                                                                              longitude=self.longitude,
                                                                              startyear=2005, endyear=2016,
                                                                              outputformat='json', usehorizon=True,
                                                                              userhorizon=None, map_variables=True,
                                                                              timeout=30,
                                                                              url='https://re.jrc.ec.europa.eu/api/')
        # Set data.index to current year
        current_year = dt.datetime.today().year
        data.index = pd.date_range(start=dt.datetime(year=current_year, month=1, day=1, hour=0, minute=0),
                                   end=dt.datetime(year=current_year, month=12, day=31, hour=23, minute=0), freq='1h')

        return data, months_selected, inputs, metadata

    # Add Components to Environment
    def add_grid(self):
        """
        Add Grid to environment
        :return:
        """
        name = 'Grid_' + str(len(self.grid) + 1)
        self.grid.append(Grid(env=self,
                              name=name))
        self.df[name + ': P [W]'] = self.grid[-1].df['P [W]']
        self.df[name + ': Blackout'] = self.grid[-1].df['Blackout']

    def add_load(self,
                 load_profile: str = None,
                 lp: bool = None):
        """
        Add Load to environment
        :return:
        """
        # TODO: Differentiate between LPC and load profile
        name = 'Load_' + str(len(self.load) + 1)
        self.load.append(Load(env=self,
                              name=name,
                              load_profile=load_profile))
        self.df['P_Res [W]'] = self.load[-1].df['P [W]']

    def add_pv(self,
               p_n: float = None,
               pv_profile: pd.Series = None,
               pv_module: str = None,
               inverter: str = None,
               modules_per_string: int = 1,
               strings_per_inverter: int = 1,
               surface_tilt: int = None,
               surface_azimuth: int = None):
        """
        Add PV system to environment
        :return:
        """
        name = 'PV_' + str(len(self.pv) + 1)
        self.pv.append(PV(env=self,
                          name=name,
                          p_n=p_n,
                          pv_profile=pv_profile,
                          location=self.location,
                          pv_module=pv_module,
                          inverter=inverter,
                          modules_per_string=modules_per_string,
                          strings_per_inverter=strings_per_inverter,
                          surface_tilt=surface_tilt,
                          surface_azimuth=surface_azimuth))
        self.df[name + ': P [W]'] = self.pv[-1].df['P [W]']
        self.df['PV total power [W]'] += self.df[name + ': P [W]']
        self.add_component_data(component=self.pv[-1], supply=True)

    def add_wind_turbine(self,
                         p_n: float = None,
                         turbine_data: dict = None,
                         wt_profile: pd.Series = None):
        """
        Add Wind Turbine to environment
        :return:
        """
        name = 'WT_' + str(len(self.wind_turbine) + 1)
        self.wind_turbine.append(WindTurbine(env=self,
                                             name=name,
                                             p_n=p_n,
                                             turbine_data=turbine_data,
                                             location=self.location,
                                             wt_profile=wt_profile))
        self.df[name + ': P [W]'] = self.wind_turbine[-1].df['P [W]']
        self.df['WT total power [W]'] += self.df[name + ': P [W]']
        self.add_component_data(component=self.wind_turbine[-1], supply=True)

    def add_diesel_generator(self,
                             p_n: float = None,
                             fuel_consumption: float = None,
                             low_load_behavior: bool = None,
                             fuel_ticks: dict = None,
                             fuel_price: float = None):
        """
        Add Diesel Generator to environment
        :return:
        """
        name = 'DG_' + str(len(self.diesel_generator) + 1)
        self.diesel_generator.append(DieselGenerator(env=self,
                                                     name=name,
                                                     p_n=p_n,
                                                     fuel_consumption=fuel_consumption,
                                                     low_load_behavior=low_load_behavior,
                                                     fuel_ticks=fuel_ticks,
                                                     fuel_price=fuel_price))
        self.add_component_data(component=self.diesel_generator[-1], supply=True)

    def add_storage(self,
                    p_n: float = None,
                    c: float = None):
        """
        Add Energy Storage to environment
        :return:
        """
        name = 'ES_' + str(len(self.storage) + 1)
        self.storage.append(Storage(env=self,
                                    name=name,
                                    p_n=p_n,
                                    c=c))
        self.df[name + ': P [W]'] = self.storage[-1].df['P [W]']
        self.add_component_data(component=self.storage[-1], supply=False)

    def add_component_data(self, component, supply: bool):
        """
        Add technical data of component to component df
        :param supply: bool
        :param component: object
            Object of create Component
        :return:
        """
        if supply is True:
            self.supply_data = self.supply_data.append(component.technical_data, ignore_index=True)
        else:
            self.storage_data = self.storage_data.append(component.technical_data, ignore_index=True)

    # Calculate simulation values
    def calc_self_supply(self):
        """

        :return: None
        """
        df = self.df
        df['Self supply [W]'] = df['WT total power [W]'] + df['PV total power [W]']
        remaining_load = df['P_Res [W]'] - df['WT total power [W]'] - df['PV total power [W]']
        df['P_Res (after RE) [W]'] = np.where(remaining_load < 0, 0, remaining_load)

    def calc_monthly_data(self):
        for i in range(12):
            days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            monthly_df = self.env.df.iloc[[0, 1440 * days[i]], :].sum(axis=0)
        print(monthly_df)

    def calc_lcoe(self, system_component: str):
        """
        Calculate LCOE
        :param system_component: str
            system component
        :return: list
            lcoe: float
            energy_yield: float
        """
        if system_component == 'PV':
            component = self.pv[0]
        elif system_component == 'wind_turbine':
            component = self.wind_turbine[0]
        elif system_component == 'diesel_generator':
            component = self.diesel_generator[0]
        elif system_component == 'grid':
            component = self.grid[0]
        elif system_component == 'storage':
            component = self.storage[0]

        i_c = component.c_invest
        o_m_c = component.c_op_main
        var_c = component.c_var
        energy_yield = component.df['P [W]'] / 1000

        lcoe = (i_c + o_m_c * self.lifetime + var_c * energy_yield * self.lifetime)

        return lcoe, energy_yield


if __name__ == '__main__':
    start = dt.datetime(year=2022, month=1, day=1, hour=0, minute=0)
    end = dt.datetime(year=2022, month=1, day=31, hour=23, minute=59)
    step = dt.timedelta(minutes=1)
    environment = Environment(time={'start': start, 'end': end, 'step': step})

    # def export_csv(self):
    #     """
    #     :return:
    #     """
    #     self.component_data.to_csv('component_data.csv')
    #     self.convert_csv_to_txt(csv='component_data.csv', txt='component_data.txt')
    #
    # def convert_csv_to_txt(self, csv: str, txt: str):
    #     """
    #     :param csv: str
    #         CSV file name
    #     :param txt: str
    #         txt file name
    #     :return: None
    #     """
    #     with open(csv, 'r') as f_in, open(txt, 'w') as f_out:
    #         # Read CSV file and store in variable
    #         content = f_in.read()
    #         # Write  content into the TXT file
    #         f_out.write(content)
