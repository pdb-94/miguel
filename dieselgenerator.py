import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
# MiGUEL modules
from component import Component


class DieselGenerator(Component):
    """
    Class to represent Diesel Generators
    """
    c_invest_n = 1000.0
    c_op_main = 20.0

    def __init__(self,
                 env,
                 name: str = None,
                 p_n: float = None,
                 low_load_behavior: bool = None,
                 fuel_consumption: float = None,
                 fuel_price: float = None,
                 fuel_ticks: dict = None):
        """
        :param env: environment
        :param name: str
            generator name
        :param p_n: float
            nominal power [W]
        :param fuel_consumption: float
            fuel consumption at nominal power
        :param fuel_price: float
            fuel price per liter
        :param fuel_ticks: dict
            fuel consumption depending on load in percentage
        """
        self.p_n = p_n
        self.c_invest = 0
        self.c_op_main = 0
        self.fuel_consumption = fuel_consumption
        self.fuel_price = fuel_price
        self.low_load_behavior = low_load_behavior
        super().__init__(env=env,
                         name=name,
                         p_n=p_n,
                         c_invest=self.c_invest_n * self.p_n,
                         c_op_main=self.c_op_main * self.p_n)
        self.df = pd.DataFrame(columns=['Status',
                                        'P [W]',
                                        'P [%]',
                                        'Energy [kWh]',
                                        'Fuel consumption [%/h]',
                                        'Fuel consumption [l/h]',
                                        'Fuel consumption [l]',
                                        'CO2-Emission [kg]',
                                        'Fuel Cost ' + self.env.currency],
                               index=self.env.time)

        if fuel_ticks is None:
            self.fuel_ticks = {0: 0, 0.25: 0.286, 0.5: 0.524, 0.75: 0.762, 1: 1.0}
            self.fuel_tick_percentage = list(self.fuel_ticks.keys())
            self.fuel_consumption_percentage = list(self.fuel_ticks.values())

        # Operating parameters
        self.status = ['ON', 'OFF', 'FORCED_ON', 'FORCED_OFF']
        # Time limit [min per 240 min] for engine load in percentage
        self.load_duration = {0.3: [30, 240], 0.5: [120, 240], 1: [240, 240]}

        # Dict with technical data
        self.technical_data = {'Component': 'Diesel Generator',
                               'Name': self.name,
                               'Nominal Power [kW]': round(self.p_n/1000, 3),
                               'Specific investment cost [' + self.env.currency + '/kW]': self.c_invest_n,
                               'Investment cost [' + self.env.currency + ']': int(self.c_invest_n*self.p_n/1000),
                               'Specific operation maintenance cost [' + self.env.currency + '/kW]': self.c_op_main,
                               'Operation maintenance cost [' + self.env.currency + ']': int(self.c_op_main * self.p_n/1000)}

    def run(self):
        """

        :return:
        """
        if self.low_load_behavior is True:
            self.low_load_model()
        elif self.low_load_behavior is False:
            self.conventional_model()
        else:
            pass
        self.calc_energy_consumption()
        # print(self.df[['P [W]', 'Energy [kWh]']])

    def low_load_model(self):
        """
        Run low load model (load < 30% nominal power possible)
        :return:
        """
        env = self.env
        df = self.df
        df['P (after RE) [W]'] = np.where(env.df['P_Res (after RE) [W]'] > self.p_n, self.p_n,
                                          env.df['P_Res (after RE) [W]'])
        df['P [W]'] = df['P (after RE) [W]']

    def conventional_model(self):
        """
        Run conventional load model with restrictions from self.load_duration
        :return: None
        """
        env = self.env
        df = self.df
        df['P (after RE) [W]'] = np.where(env.df['P_Res (after RE) [W]'] > self.p_n, self.p_n,
                                          env.df['P_Res (after RE) [W]'])
        df['P [W]'] = df['P (after RE) [W]']
        for i in range(0, len(df.index) - 239, 240):
            # Set clock
            clock = self.df.index[i]
            end = clock + dt.timedelta(minutes=239)
            self.calc_load_percentage(clock=clock, end=end)
            gen_status = self.check_status(clock=clock, end=end)
            keys = list(gen_status.keys())
            # Calculate possible power ups to 51%
            if 1 in keys:
                power_50 = int(120 - gen_status[1])
            else:
                power_50 = int(120)
            # Calculate power ups tp 71%
            if 0 in keys:
                if gen_status[0] - power_50 - 30 < 0:
                    power_30 = int(0)
                else:
                    power_30 = int(gen_status[0] - power_50 - 30)
            else:
                power_30 = int(0)
            self.change_generator_load(end=end, power_30=power_30, power_50=power_50)

    def calc_load_percentage(self, clock: dt.datetime, end: dt.datetime):
        """
        :param clock: dt.datetime
            time frame start
        :param end: dt.datetime
            time frame end
        :return: None
        """
        df = self.df
        df.loc[clock:end, 'Load Percentage'] = df.loc[clock:end, 'P (after RE) [W]'] / self.p_n

    def check_status(self, clock: dt.datetime, end: dt.datetime):
        """
        :param clock: dt.datetime
            time frame start
        :param end: dt.datetime
            time frame end
        :return: dict
            generator status during timeframe
        """
        df = self.df
        df.loc[clock:end, 'Generator Status'] = np.where(df.loc[clock:end, 'Load Percentage'] <= 0.3, 0,
                                                         np.where(df.loc[clock:end, 'Load Percentage'] <= 0.5, 1, 2))
        gen_status = dict(df.loc[clock:end, 'Generator Status'].value_counts())

        return gen_status

    def change_generator_load(self, end: dt.datetime, power_30: int, power_50: int):
        """
        :param end: dt.datetime
            time frame end
        :param power_30: int
            number of time steps to power up to 71%
        :param power_50: int
            number of time steps to power up to 51%
        :return: None
        """
        df = self.df
        df.loc[end - dt.timedelta(minutes=power_50 + power_30):end - dt.timedelta(minutes=power_30), 'P [W]'] = self.p_n * 0.51
        df.loc[end - dt.timedelta(minutes=power_30):end, 'P [W]'] = self.p_n * 0.71
        df['P [W]'] = np.where(df['P [W]'] > df['P (after RE) [W]'], df['P [W]'], df['P (after RE) [W]'])

    # Economical and ecological parameters
    def calc_energy_consumption(self):
        """
        Calculate energy consumption per time step
        :return:
        """
        # Calculate energy consumption per time step
        self.df['Energy [kWh]'] = self.df['P [W]'] / 60 * self.env.i_step / 1000

    def calc_fuel_consumption(self):
        """
        Calculate fuel consumption per time step with fuel ticks
        :return: None
        """
        # Interpolate fuel ticks
        self.df['Fuel consumption [%/h]'] = np.interp(x=self.df['P [%]'],
                                                      xp=self.fuel_tick_percentage,
                                                      fp=self.fuel_consumption_percentage)
        # Calculate fuel consumption
        self.df['Fuel consumption [l/h]'] = round(self.df['Fuel consumption [%/h]'] * self.fuel_consumption, 3)
        self.df['Fuel consumption [l]'] = round(
            self.df['Fuel consumption [%/h]'] * self.fuel_consumption / 60 * self.env.i_step, 3)

    def calc_fuel_cost(self):
        """
        Calculate fuel cost per time step with fuel price
        :return: None
        """
        self.df['Fuel Cost ' + self.env.currency] = self.df['Fuel consumption [l]'] * self.fuel_price

    def calc_co2_emissions(self):
        """
        Calculate CO2-Emissions per time step with CO2 factor
        :return: None
        """
        self.df['CO2-Emission [kg]'] = self.df['Energy [kWh]'] * self.env.co2_diesel

