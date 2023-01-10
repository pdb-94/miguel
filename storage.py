import pandas as pd
import simses


class Storage:
    """
    Class to represent Energy Storages
    """
    c_invest_n = 1000.0
    c_op_main = 20.0

    def __init__(self,
                 env,
                 name: str = None,
                 p_n: float = None,
                 c: float = None):
        self.env = env
        self.name = name
        self.p_n = p_n
        self.c = c
        self.c_invest_n = 0
        self.c_op_main_n = 0

        self.df = pd.DataFrame(columns=['P [W]'], index=self.env.time)

        # Dict with technical data
        self.technical_data = {'Component': 'Energy Storage',
                               'Name': self.name,
                               'Nominal Power [kW]': round(self.p_n / 1000, 3),
                               'Capacity [kWh]': self.c,
                               'Specific investment cost [' + self.env.currency + '/kWh]': int(self.c_invest_n),
                               'Investment cost [' + self.env.currency + ']': int(self.c_invest_n * self.p_n / 1000),
                               'Specific operation maintenance cost [' + self.env.currency + '/kWh]': int(self.c_op_main_n),
                               'Operation maintenance cost [' + self.env.currency + '/a]': int(self.c_op_main_n * self.p_n / 1000)}
