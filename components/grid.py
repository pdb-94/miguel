import pandas as pd


class Grid:
    """
    Class to represent grid
    """
    def __init__(self,
                 env,
                 name: str = None,
                 c_var_n: float = 0):
        """
        :param env: Environment
        :param name: str
            grid name
        :param c_var_n: float
            Variable cost [US§/kWh]
        """
        self.env = env
        self.name = name
        self.df = pd.DataFrame(columns=['P [W]', 'Blackout'],
                               index=self.env.time)
        self.c_var_n = c_var_n
