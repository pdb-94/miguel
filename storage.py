import datetime as dt
import numpy as np
import pandas as pd


class Storage:
    """
    Class to represent Energy Storages with a simplified Storage model
    """
    c_invest_n = 1000.0
    c_op_main = 20.0

    def __init__(self,
                 env,
                 name: str = None,
                 p_n: float = None,
                 c: float = None,
                 soc: float = 0.5,
                 soc_max: float = 0.95,
                 soc_min: float = 0.05,
                 n_charge: float = 0.8,
                 n_discharge: float = 0.8):
        self.env = env
        self.name = name
        self.p_n = p_n
        self.c = c
        self.soc = soc
        self.soc_max = soc_max
        self.soc_min = soc_min
        self.n_charge = n_charge
        self.n_discharge = n_discharge
        self.c_invest_n = 300
        self.c_op_main_n = 0
        self.co2_init = 35  # kg/kWh

        self.cycles = 0
        self.cycle_max = 4000

        self.df = pd.DataFrame(columns=['P [W]', 'Q [Wh]', 'SOC', ], index=self.env.time)
        self.set_initial_values()

        # Dict with technical data
        self.technical_data = {'Component': 'Energy Storage',
                               'Name': self.name,
                               'Nominal Power [kW]': round(self.p_n / 1000, 3),
                               'Capacity [kWh]': self.c,
                               'Specific investment cost [' + self.env.currency + '/kWh]': int(self.c_invest_n),
                               'Investment cost [' + self.env.currency + ']': int(self.c_invest_n * self.p_n / 1000),
                               'Specific operation maintenance cost [' + self.env.currency + '/kWh]': int(
                                   self.c_op_main_n),
                               'Operation maintenance cost [' + self.env.currency + '/a]': int(
                                   self.c_op_main_n * self.p_n / 1000)}

    def set_initial_values(self):
        """
        Set initial values for ES
        :return: None
        """
        initial_time = self.df.index[0]
        self.df.loc[initial_time, 'SOC'] = self.soc
        self.df.loc[initial_time, 'Q [Wh]'] = self.c * self.df.loc[initial_time, 'SOC']
        self.df['P [W]'] = 0

    def charge(self, clock: dt.datetime, power: float):
        """
        :param clock: dt.datetime
            time stamp
        :param power: float
            charging power
        :return: None
        """
        t_step = self.env.i_step
        if clock == self.env.t_start:
            return 0
        # Check charging power
        if power <= self.p_n:
            power = power
        else:
            power = self.p_n
        # Calculate charging energy
        q_charge = power * self.n_charge * (t_step / 60)
        if self.df.loc[clock - dt.timedelta(minutes=t_step), 'Q [Wh]'] + q_charge < self.c * self.soc_max:
            self.df.loc[clock, 'P [W]'] = power
            self.df.loc[clock, 'Q [Wh]'] = self.df.loc[clock - dt.timedelta(minutes=t_step), 'Q [Wh]'] + q_charge
            self.df.loc[clock, 'SOC'] = self.df.loc[clock, 'Q [Wh]'] / self.c
            return power
        else:
            # Calculate remaining energy to charge storage
            q_remain = (self.c * self.soc_max) - self.df.loc[clock - dt.timedelta(minutes=t_step), 'Q [Wh]']
            power = (60 * q_remain) / (t_step * self.n_charge)
            if power == 0:
                self.df.loc[clock, 'P [W]'] = 0
                self.df.loc[clock, 'Q [Wh]'] = self.df.loc[clock - dt.timedelta(minutes=t_step), 'Q [Wh]']
                self.df.loc[clock, 'SOC'] = self.soc_max
                return 0
            else:
                self.df.loc[clock, 'P [W]'] = power
                self.df.loc[clock, 'Q [Wh]'] = self.df.loc[clock - dt.timedelta(minutes=self.env.i_step), 'Q [Wh]'] + q_remain
                self.df.loc[clock, 'SOC'] = self.df.loc[clock, 'Q [Wh]'] / self.c
                return power

    def discharge(self, clock: dt.datetime, power: float):
        """
        Discharge Storage
        :param clock: dt.datetime
            time stamp
        :param power: float
            discharge power
        :return: power
        """
        t_step = self.env.i_step
        if clock == self.env.t_start:
            return 0
        # Check charging power
        if power <= self.p_n:
            power = -power
        else:
            power = -self.p_n
        q_discharge = power * self.n_discharge * (t_step / 60)
        # Check if SOC after discharge > soc_min
        if self.soc_min < self.df.loc[clock, 'SOC'] + (q_discharge/self.c):
            self.df.loc[clock, 'P [W]'] = power
            self.df.loc[clock, 'Q [Wh]'] = self.df.loc[clock - dt.timedelta(minutes=t_step), 'Q [Wh]'] + q_discharge
            self.df.loc[clock, 'SOC'] = self.df.loc[clock, 'Q [Wh]'] / self.c
            return power
        else:
            # Calculate remaining energy to discharge storage
            q_remain = self.df.loc[clock - dt.timedelta(minutes=t_step), 'Q [Wh]'] - (self.c * self.soc_min)
            power = -(60 * q_remain) / (t_step * self.n_charge)
            if power == 0:
                self.df.loc[clock, 'P [W]'] = 0
                self.df.loc[clock, 'Q [Wh]'] = self.df.loc[clock - dt.timedelta(minutes=t_step), 'Q [Wh]']
                self.df.loc[clock, 'SOC'] = self.soc_min
                return 0
            else:
                self.df.loc[clock, 'P [W]'] = power
                self.df.loc[clock, 'Q [Wh]'] = self.df.loc[clock - dt.timedelta(minutes=self.env.i_step), 'Q [Wh]'] - q_remain
                self.df.loc[clock, 'SOC'] = self.df.loc[clock, 'Q [Wh]'] / self.c
                return power

    def calculate_cycle(self):
        """
        Calculate number of cycles
        :return: None
        """
