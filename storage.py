import datetime as dt
import numpy as np
import pandas as pd


class Storage:
    """
    Class to represent Energy Storages with a simple Storage model
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
        self.c_invest_n = 0
        self.c_op_main_n = 0

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
                               'Specific operation maintenance cost [' + self.env.currency + '/kWh]': int(self.c_op_main_n),
                               'Operation maintenance cost [' + self.env.currency + '/a]': int(self.c_op_main_n * self.p_n / 1000)}

    def set_initial_values(self):
        """
        Set initial values for ES
        :return: None
        """
        initial_time = self.df.index[0]
        self.df.loc[initial_time, 'SOC'] = self.soc
        self.df.loc[initial_time, 'Q [Wh]'] = self.c * self.df.loc[initial_time, 'SOC']
        self.df.loc[initial_time, 'P [W]'] = 0

    def charge(self, clock: dt.datetime, power: float):
        """
        :param clock: dt.datetime
            time stamp
        :param power: float
            charging power
        :return: None
        """
        if clock == self.env.t_start:
            pass
        else:
            if power >= self.p_n:
                power = self.p_n
            energy = power * self.n_charge * self.env.i_step/60
            if self.df.loc[clock-dt.timedelta(minutes=self.env.i_step), 'Q [Wh]'] + energy > self.c:
                d_SOC = (self.soc_max - self.df.loc[clock - dt.timedelta(minutes=self.env.i_step), 'SOC'])
                power = 0
                if power == 0:
                    print('Could not charge storage: SOC > SOC_Max.')
                    pass
                else:
                    self.df.loc[clock, 'P [W]'] = power
                    self.df.loc[clock, 'Q [Wh]'] = self.df.loc[clock-dt.timedelta(minutes=self.env.i_step), 'Q [Wh]'] + energy
                    self.df.loc[clock, 'SOC'] = self.df.loc[clock-dt.timedelta(minutes=self.env.i_step), 'SOC'] + energy/self.c
            else:
                self.df.loc[clock, 'P [W]'] = power
                self.df.loc[clock, 'Q [Wh]'] = self.df.loc[clock - dt.timedelta(minutes=self.env.i_step), 'Q [Wh]'] + energy
                self.df.loc[clock, 'SOC'] = self.df.loc[clock - dt.timedelta(minutes=self.env.i_step), 'SOC'] + energy / self.c
        # print(clock, self.df.loc[clock, 'SOC'])

        return power



            #     if self.df.loc[clock-dt.timedelta(minutes=self.env.i_step), 'SOC'] + power*self.charge/self.c > self.soc_max:
            #         # Calc max power
            #         power = self.calculate_power(clock=clock, charge=True)
            #         if power == 0:
            #             print('Could not charge storage: SOC > SOC_Max.')
            #             pass
            #         else:
            #             self.df.loc[clock, 'P [W]'] = power
            #             self.df.loc[clock, 'Q [Wh]'] = self.df.loc[clock-dt.timedelta(minutes=self.env.i_step), 'Q [Wh]']
            #             self.df.loc[clock, 'SOC'] = self.df.loc[clock-dt.timedelta(minutes=self.env.i_step), 'SOC']
            # elif self.df.loc[clock-dt.timedelta(minutes=self.env.i_step), 'SOC'] + energy/self.c < self.soc_min:
            #     # Calc max power
            #     power = self.calculate_power(clock=clock, charge=True)
            #     if power == 0:
            #         print('Could not charge storage: SOC > SOC_Max.')
            #         pass
            #     print('Could not charge storage: SOC < SOC_Min.')
            #     self.df.loc[clock, 'P [W]'] = power
            #     self.df.loc[clock, 'Q [Wh]'] = self.df.loc[clock-dt.timedelta(minutes=self.env.i_step), 'Q [Wh]']
            #     self.df.loc[clock, 'SOC'] = self.df.loc[clock-dt.timedelta(minutes=self.env.i_step), 'SOC']
            #     pass
            # else:
            #     self.df.loc[clock, 'P [W]'] = power
            #     if power > 0:
            #         eta = self.n_charge
            #     else:
            #         eta = self.n_discharge
            #     self.df.loc[clock, 'SOC'] = self.df.loc[clock-dt.timedelta(minutes=self.env.i_step), 'SOC'] + (energy*eta)/self.c
            #     self.df.loc[clock, 'Q [Wh]'] = self.df.loc[clock - dt.timedelta(minutes=self.env.i_step), 'Q [Wh]'] + (energy*eta)

    def calculate_power(self, clock: dt.datetime, charge: bool = None):
        if charge is True:
            # print(self.soc_max - self.df.loc[clock-dt.timedelta(minutes=self.env.i_step), 'SOC'])
            power = 60*(self.soc_max - self.df.loc[clock-dt.timedelta(minutes=self.env.i_step), 'SOC']) / (self.env.i_step*self.n_charge)
        else:
            power = 0

        # print(clock, power)

        return power

    def calculate_cycle(self):
        """

        :return:
        """
