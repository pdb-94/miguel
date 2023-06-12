import pandas as pd
import numpy as np
import datetime as dt


class DieselGenerator:
    """
    Class to represent Diesel Generators
    """

    def __init__(self,
                 env,
                 name: str = None,
                 p_n: float = None,
                 fuel_consumption: float = None,
                 fuel_price: float = None,
                 fuel_ticks: dict = None,
                 c_invest_n: float = 468,
                 c_op_main_n: float = None,
                 c_var_n: float = 0.021,
                 co2_init: float = 265,
                 c_invest: float = None,
                 c_op_main: float = None):
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
        self.name = name
        self.p_n = p_n
        self.c_invest_n = c_invest_n  # USD/kW
        if c_op_main_n is not None:
            self.c_op_main_n = c_op_main_n
        else:
            self.c_op_main_n = self.c_invest_n * 0.03  # USD/kW
        self.c_var_n = c_var_n  # USD/kWh
        self.fuel_consumption = fuel_consumption  # [l/p_n]
        self.fuel_price = fuel_price  # [US$/l]
        self.co2_init = co2_init  # kg/kW
        if c_invest is None:
            self.c_invest = self.c_invest_n * self.p_n / 1000
        else:
            self.c_invest = c_invest
        if c_op_main is None:
            self.c_op_main = self.c_op_main_n * self.p_n / 1000
        else:
            self.c_op_main = c_op_main
        self.df = pd.DataFrame(columns=['P [W]',
                                        'P [%]',
                                        'Fuel Consumption [l/h]',
                                        f'Fuel cost [{self.env.currency}]'],
                               index=self.env.time)

        if fuel_ticks is None:
            self.fuel_ticks = {0: 0, 0.25: 0.33, 0.5: 0.542, 0.75: 0.771, 1: 1.0}
            self.fuel_tick_percentage = list(self.fuel_ticks.keys())
            self.fuel_consumption_percentage = list(self.fuel_ticks.values())
        self.fuel_df = self.calc_fuel_ticks()

        # Dict with technical data
        self.technical_data = {'Component': 'Diesel Generator',
                               'Name': self.name,
                               'Nominal Power [kW]': round(self.p_n / 1000, 3),
                               f'Specific investment cost [{self.env.currency}/kW]': int(self.c_invest_n),
                               f'Investment cost [{self.env.currency}]': int(self.c_invest_n * self.p_n / 1000),
                               f'Specific operation maintenance cost [{self.env.currency}/kW]': int(self.c_op_main_n),
                               f'Operation maintenance cost [{self.env.currency}/a]':
                                   int(self.c_op_main_n * self.p_n / 1000)}

    def run(self, clock: dt.datetime, power: float):
        """
        Calculate power output, fuel consumption and cost per time step
        :param clock: dt.datetime
            time stamp
        :param power: float
            power [W]
        :return: float
            power [W]
        """
        if power > self.p_n:
            power = self.p_n
        self.df.at[clock, 'P [W]'] = power
        self.df.at[clock, 'P [%]'] = round(self.df.at[clock, 'P [W]'] / self.p_n, 2)
        self.df.at[clock, 'Fuel Ticks [%]'] = self.fuel_df.loc[self.df.at[clock, 'P [%]'], 'Fuel Ticks [%]']
        self.df.at[clock, 'Fuel Consumption [l/h]'] = self.df.at[clock, 'Fuel Ticks [%]'] * self.fuel_consumption
        self.df.at[clock, 'Fuel Consumption [l/Timestamp]'] = \
            self.df.at[clock, 'Fuel Consumption [l/h]'] * self.env.i_step / 60
        self.df.at[clock, 'Fuel cost [US$]'] = self.df.at[clock, 'Fuel Consumption [l/Timestamp]'] * self.fuel_price

        return self.df.at[clock, 'P [W]']

    def calc_fuel_ticks(self):
        """
        Calculate fuel ticks for every load percentage
        :return: pd.DataFrame
            df
        """
        func = np.polyfit(x=list(self.fuel_ticks.keys()),
                          y=list(self.fuel_ticks.values()),
                          deg=len(list(self.fuel_ticks.keys())) - 1)
        df = pd.DataFrame(index=range(0, 101),
                          columns=['P [%]', 'Fuel Ticks [%]'])
        df['P [%]'] = np.arange(len(df)) / 100
        df['Fuel Ticks [%]'] = round(func[0] * df['P [%]'] ** 4 + func[1] * df['P [%]'] ** 3 + func[2] * df['P [%]'] ** 2 + func[3] * df['P [%]'] ** 1 + func[4] * df['P [%]'] ** 0,
                                     3)
        df = df.set_index('P [%]')

        return df
