import math
import sys
import sqlite3
import numpy as np
import pandas as pd
import datetime as dt
from matplotlib import pyplot as plt

"""
Sources: 
Minimum runtime 15min: https://powercontinuity.co.uk/knowledge-base/ups-and-generators-how-long-can-they-run-for
Power curve values: https://www.generatorsource.com/Diesel_Fuel_Consumption.aspx
"""


class DieselGenerator:
    def __init__(self,
                 env=None,
                 name: str = None,
                 p_n: float = None,
                 model: bool = False,
                 c_invest_n: float = 468,
                 c_op_main_n: float = None,
                 c_var_n: float = 0.021,
                 co2_init: float = 265,
                 c_invest: float = None,
                 c_op_main: float = None):
        self.env = env
        self.name = name
        self.p_n = p_n
        self.p_min = self.p_n * 0.3
        if model:
            self.model = 'low_load'
        else:
            self.model = 'conventional'
        self.power_curve_data = self.get_power_curve_data()
        self.power_curve = self.select_power_curve()

        self.df = pd.DataFrame(columns=['P [W]',
                                        'P [%]',
                                        'Fuel consumption [l/h]',
                                        f'Fuel cost [US$]'],
                               index=self.env.time)
        # Economic parameters
        self.c_invest_n = c_invest_n  # USD/kW
        if c_invest is None:
            self.c_invest = self.c_invest_n * self.p_n / 1000
        else:
            self.c_invest = c_invest
        if c_op_main_n is not None:
            self.c_op_main_n = c_op_main_n
        else:
            self.c_op_main_n = self.c_invest_n * 0.03  # USD/kW
        if c_op_main is None:
            self.c_op_main = self.c_op_main_n * self.p_n / 1000
        else:
            self.c_op_main = c_op_main
        # Ecologic parameters
        self.c_var_n = c_var_n  # USD/kWh
        self.co2_init = co2_init * self.p_n / 1000  # kg
        # Technical data
        self.technical_data = {'Component': 'Diesel Generator',
                               'Name': self.name,
                               'Nominal Power [kW]': round(self.p_n / 1000, 3),
                               f'Specific investment cost [US$/kW]': int(self.c_invest_n),
                               f'Investment cost [US$]': int(self.c_invest_n * self.p_n / 1000),
                               f'Specific operation maintenance cost [US$/kW]': int(self.c_op_main_n),
                               f'Operation maintenance cost [US$/a]': int(self.c_op_main_n * self.p_n / 1000)}

    def run(self,
            clock: dt.datetime,
            power: float):
        """
        Run generator model
        :param clock: dt.datetime
            time stamp
        :param power: float
            power [W]
        :return: clock, power
        """
        if self.model == 'conventional':
            if 0 < power <= self.p_n * 0.3:
                power = self.p_n * 0.3
            else:
                power = power
        p_relative = power/self.p_n
        fuel_consumption = self.calc_fuel_consumption(power=power)
        fuel_cost = self.calc_fuel_cost(fuel_consumption=fuel_consumption)
        # Set values
        self.df.at[clock, 'P [W]'] = power
        self.df.at[clock, 'P [%]'] = p_relative
        self.df.at[clock, 'Fuel consumption [l/h]'] = fuel_consumption
        self.df.at[clock, 'Fuel cost [US$]'] = fuel_cost

        return power
    @staticmethod
    def get_power_curve_data():
        """
        Get power curves from database
        :return: pd.DataFrame
            df with power curves
        """
        conn = sqlite3.connect(f"{sys.path[1]}/data/miguel.db")
        df = pd.read_sql('SELECT * FROM dg_fuel_consumption_data', conn)

        return df

    def select_power_curve(self):
        """
        Select power curve based on nominal power from database
        :return: np.poly1d
            polynom to calculate fuel consumption
        """
        index = self.power_curve_data[self.power_curve_data['Power'] >= self.p_n]['Power'].min()
        if math.isnan(index):
            index = 2250
        self.power_curve_data = self.power_curve_data.set_index('Power')
        x = self.power_curve_data.loc[index, 'x2':'x0'].to_list()
        power_curve = np.poly1d(x)

        return power_curve

    def calc_fuel_consumption(self,
                              power: float):
        """
        Calculate fuel consumption in l/h based on power demand
        :param power: float
            power
        :return: float
            fuel_consumption [l/h]
        """
        fuel_consumption = self.power_curve(power / self.p_n)

        return fuel_consumption

    def calc_fuel_cost(self, fuel_consumption: float):
        """
        Calculate fuel cost for each time step
        :param fuel_consumption: float
            fuel consumption [l/h]
        :return: float
            fuel cost [US$/time step]
        """
        fuel_cost = fuel_consumption * self.env.diesel_price * self.env.i_step / 60  # Fuel cost in US$ per time step

        return fuel_cost

