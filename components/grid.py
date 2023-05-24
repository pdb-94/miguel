import pandas as pd


class Grid:
    """
    Class to represent grid
    """
    def __init__(self,
                 env,
                 name: str = None,
                 c_var: float = 0):
        self.env = env
        self.name = name
        self.df = pd.DataFrame(columns=['P [W]', 'Blackout'],
                               index=self.env.time)
        self.c_var = c_var
